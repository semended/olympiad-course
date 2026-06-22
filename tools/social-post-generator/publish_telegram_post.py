#!/usr/bin/env python3
"""Publish reviewed allmath social post drafts to a Telegram channel.

The script is deliberately dry-run by default. Passing --live is the only path
that touches Telegram, so local checks and GitHub Actions previews are boring in
the best possible way.
"""
from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import re
import ssl
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_API_BASE = "https://api.telegram.org"
MAX_MESSAGE_CHARS = 4096
MAX_CAPTION_CHARS = 1024
MAX_MEDIA_GROUP_ITEMS = 10


class PublishError(RuntimeError):
    pass


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str
    chat_id: str
    api_base: str
    timeout: int
    ssl_context: ssl.SSLContext


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PublishError(f"{path}: invalid JSON: {exc}") from exc


def path_from_manifest(manifest_path: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (manifest_path.parent / path).resolve()


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if not manifest.get("caption") and not manifest.get("post"):
        raise PublishError("manifest.caption or manifest.post is required")
    cards = manifest.get("cards")
    if not isinstance(cards, list) or not cards:
        raise PublishError("manifest.cards must be a non-empty list")
    return manifest


def markdownish_to_telegram_html(markdown: str) -> str:
    lines = markdown.splitlines()
    if "Картинки:" in lines:
        lines = lines[: lines.index("Картинки:")]
    while lines and not lines[-1].strip():
        lines.pop()

    converted: list[str] = []
    bold_pattern = re.compile(r"\*\*(.+?)\*\*")
    for line in lines:
        cursor = 0
        chunks: list[str] = []
        for match in bold_pattern.finditer(line):
            chunks.append(html.escape(line[cursor : match.start()]))
            chunks.append(f"<b>{html.escape(match.group(1))}</b>")
            cursor = match.end()
        chunks.append(html.escape(line[cursor:]))
        converted.append("".join(chunks))
    return "\n".join(converted).strip()


def split_html_message(text: str, limit: int = MAX_MESSAGE_CHARS) -> list[str]:
    if len(text) <= limit:
        return [text] if text else []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for paragraph in text.split("\n\n"):
        addition = paragraph if not current else "\n\n" + paragraph
        if current and current_len + len(addition) > limit:
            chunks.append("".join(current))
            current = [paragraph]
            current_len = len(paragraph)
        elif len(paragraph) > limit:
            if current:
                chunks.append("".join(current))
                current = []
                current_len = 0
            for index in range(0, len(paragraph), limit):
                chunks.append(paragraph[index : index + limit])
        else:
            current.append(addition)
            current_len += len(addition)
    if current:
        chunks.append("".join(current))
    return chunks


def build_payload_summary(
    manifest_path: Path,
    manifest: dict[str, Any],
    text_path: Path,
    post_html: str,
    card_paths: list[Path],
    *,
    caption_mode: str,
    live: bool,
) -> dict[str, Any]:
    return {
        "mode": "live" if live else "dry-run",
        "manifest": str(manifest_path),
        "slug": manifest.get("slug"),
        "text": str(text_path),
        "cards": [str(path) for path in card_paths],
        "text_chars": len(post_html),
        "caption_mode": caption_mode,
    }


def resolve_caption_mode(requested: str, post_html: str, card_count: int) -> str:
    if requested != "auto":
        return requested
    if post_html and len(post_html) <= MAX_CAPTION_CHARS and card_count > 0:
        return "album"
    return "message"


def require_publish_flag(manifest_path: Path, manifest: dict[str, Any]) -> None:
    source = manifest.get("source")
    if not source:
        raise PublishError("manifest.source is required when --require-publish-flag is used")
    source_path = path_from_manifest(manifest_path, str(source))
    spec = load_json(source_path)
    telegram = spec.get("telegram")
    if not isinstance(telegram, dict) or telegram.get("publish") is not True:
        raise PublishError(f"{source_path}: set telegram.publish to true before automatic publishing")


def read_config(args: argparse.Namespace) -> TelegramConfig:
    token = os.environ.get(args.bot_token_env, "").strip()
    chat_id = args.channel_id or os.environ.get(args.channel_env, "").strip()
    if not token:
        raise PublishError(f"{args.bot_token_env} is required for --live")
    if not chat_id:
        raise PublishError(f"{args.channel_env} or --channel-id is required for --live")
    return TelegramConfig(
        bot_token=token,
        chat_id=chat_id,
        api_base=args.api_base.rstrip("/"),
        timeout=args.timeout,
        ssl_context=build_ssl_context(args),
    )


def build_ssl_context(args: argparse.Namespace) -> ssl.SSLContext:
    if args.insecure_skip_verify:
        return ssl._create_unverified_context()

    ca_file = args.ca_file or os.environ.get("TELEGRAM_CA_FILE") or discover_certifi_ca_file()
    if ca_file:
        return ssl.create_default_context(cafile=str(ca_file))
    return ssl.create_default_context()


def discover_certifi_ca_file() -> str | None:
    try:
        import certifi  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return None
    return str(certifi.where())


def telegram_url(config: TelegramConfig, method: str) -> str:
    return f"{config.api_base}/bot{config.bot_token}/{method}"


def telegram_json(config: TelegramConfig, method: str, payload: dict[str, Any]) -> Any:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        telegram_url(config, method),
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    return decode_telegram_response(method, req, config)


def telegram_multipart(
    config: TelegramConfig,
    method: str,
    fields: dict[str, str],
    files: dict[str, Path],
) -> Any:
    boundary = f"----allmath{uuid.uuid4().hex}"
    body = bytearray()

    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")

    for name, path in files.items():
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            (
                f'Content-Disposition: form-data; name="{name}"; '
                f'filename="{path.name}"\r\n'
                f"Content-Type: {mime_type}\r\n\r\n"
            ).encode("utf-8")
        )
        body.extend(path.read_bytes())
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    req = request.Request(
        telegram_url(config, method),
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    return decode_telegram_response(method, req, config)


def decode_telegram_response(method: str, req: request.Request, config: TelegramConfig) -> Any:
    try:
        with request.urlopen(req, timeout=config.timeout, context=config.ssl_context) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise PublishError(f"Telegram {method} failed with HTTP {exc.code}: {safe_telegram_error(raw)}") from exc
    except error.URLError as exc:
        if is_ssl_certificate_error(exc.reason):
            raise PublishError(ssl_certificate_help(method, exc.reason)) from exc
        raise PublishError(f"Telegram {method} failed: {exc.reason}") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PublishError(f"Telegram {method} returned invalid JSON") from exc
    if not payload.get("ok"):
        raise PublishError(f"Telegram {method} failed: {payload.get('description', 'unknown error')}")
    return payload.get("result")


def safe_telegram_error(raw: str) -> str:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw[:400]
    return str(payload.get("description") or payload)[:400]


def is_ssl_certificate_error(reason: Any) -> bool:
    if isinstance(reason, ssl.SSLCertVerificationError):
        return True
    if isinstance(reason, ssl.SSLError) and "CERTIFICATE_VERIFY_FAILED" in str(reason):
        return True
    return "CERTIFICATE_VERIFY_FAILED" in str(reason)


def ssl_certificate_help(method: str, reason: Any) -> str:
    return (
        f"Telegram {method} failed: {reason}\n"
        "Python cannot verify Telegram's HTTPS certificate chain on this machine.\n"
        "On macOS with python.org Python, run once:\n"
        '  "/Applications/Python 3.13/Install Certificates.command"\n'
        "Then reopen the terminal, export TELEGRAM_BOT_TOKEN/TELEGRAM_CHANNEL_ID again, and rerun --live.\n"
        "Alternative: install/use certifi or pass a trusted CA bundle via --ca-file /path/to/cacert.pem "
        "or TELEGRAM_CA_FILE=/path/to/cacert.pem."
    )


def send_text_messages(
    config: TelegramConfig,
    post_html: str,
    *,
    disable_notification: bool,
    protect_content: bool,
) -> list[Any]:
    results: list[Any] = []
    for chunk in split_html_message(post_html):
        payload: dict[str, Any] = {
            "chat_id": config.chat_id,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_notification": disable_notification,
            "protect_content": protect_content,
        }
        results.append(telegram_json(config, "sendMessage", payload))
    return results


def send_photo(
    config: TelegramConfig,
    path: Path,
    *,
    caption_html: str | None,
    disable_notification: bool,
    protect_content: bool,
) -> Any:
    fields: dict[str, str] = {
        "chat_id": config.chat_id,
        "disable_notification": json.dumps(disable_notification),
        "protect_content": json.dumps(protect_content),
    }
    if caption_html:
        fields["caption"] = caption_html
        fields["parse_mode"] = "HTML"
    return telegram_multipart(config, "sendPhoto", fields, {"photo": path})


def send_media_groups(
    config: TelegramConfig,
    card_paths: list[Path],
    *,
    caption_html: str | None,
    disable_notification: bool,
    protect_content: bool,
) -> list[Any]:
    results: list[Any] = []
    for offset in range(0, len(card_paths), MAX_MEDIA_GROUP_ITEMS):
        chunk = card_paths[offset : offset + MAX_MEDIA_GROUP_ITEMS]
        if len(chunk) == 1:
            results.append(
                send_photo(
                    config,
                    chunk[0],
                    caption_html=caption_html if offset == 0 else None,
                    disable_notification=disable_notification,
                    protect_content=protect_content,
                )
            )
            continue

        media: list[dict[str, str]] = []
        files: dict[str, Path] = {}
        for index, path in enumerate(chunk):
            field_name = f"photo{offset + index}"
            item = {"type": "photo", "media": f"attach://{field_name}"}
            if offset == 0 and index == 0 and caption_html:
                item["caption"] = caption_html
                item["parse_mode"] = "HTML"
            media.append(item)
            files[field_name] = path
        fields = {
            "chat_id": config.chat_id,
            "media": json.dumps(media, ensure_ascii=False),
            "disable_notification": json.dumps(disable_notification),
            "protect_content": json.dumps(protect_content),
        }
        results.append(telegram_multipart(config, "sendMediaGroup", fields, files))
    return results


def publish(args: argparse.Namespace) -> dict[str, Any]:
    manifest_path = args.manifest.resolve()
    manifest = load_manifest(manifest_path)
    if args.require_publish_flag:
        require_publish_flag(manifest_path, manifest)

    text_source = manifest.get("caption") or manifest.get("post")
    text_path = path_from_manifest(manifest_path, str(text_source))
    if not text_path.exists():
        raise PublishError(f"text file does not exist: {text_path}")
    card_paths = [path_from_manifest(manifest_path, str(path)) for path in manifest["cards"]]
    missing_cards = [str(path) for path in card_paths if not path.exists()]
    if missing_cards:
        raise PublishError("card file(s) do not exist:\n- " + "\n- ".join(missing_cards))

    post_html = markdownish_to_telegram_html(text_path.read_text(encoding="utf-8"))
    caption_mode = resolve_caption_mode(args.caption_mode, post_html, len(card_paths))
    if caption_mode == "album" and len(post_html) > MAX_CAPTION_CHARS:
        raise PublishError(f"album caption is {len(post_html)} chars; Telegram limit is {MAX_CAPTION_CHARS}")

    summary = build_payload_summary(
        manifest_path,
        manifest,
        text_path,
        post_html,
        card_paths,
        caption_mode=caption_mode,
        live=args.live,
    )

    if not args.live:
        summary["would_send"] = describe_actions(caption_mode, post_html, len(card_paths))
        return summary

    config = read_config(args)
    results: dict[str, Any] = {"messages": [], "media": []}
    caption_html = post_html if caption_mode == "album" else None
    if post_html and caption_mode == "message":
        results["messages"] = send_text_messages(
            config,
            post_html,
            disable_notification=args.disable_notification,
            protect_content=args.protect_content,
        )
    results["media"] = send_media_groups(
        config,
        card_paths,
        caption_html=caption_html,
        disable_notification=args.disable_notification,
        protect_content=args.protect_content,
    )
    summary["telegram_result"] = summarize_result_ids(results)
    return summary


def describe_actions(caption_mode: str, post_html: str, card_count: int) -> list[str]:
    actions: list[str] = []
    if post_html and caption_mode == "message":
        actions.append(f"sendMessage with {len(post_html)} HTML chars")
    if card_count == 1:
        detail = "with caption" if post_html and caption_mode == "album" else "without caption"
        actions.append(f"sendPhoto {detail}")
    else:
        groups = mathish_ceil(card_count, MAX_MEDIA_GROUP_ITEMS)
        detail = "with first-photo caption" if post_html and caption_mode == "album" else "without caption"
        actions.append(f"sendMediaGroup for {card_count} cards in {groups} album(s) {detail}")
    return actions


def mathish_ceil(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor


def summarize_result_ids(results: dict[str, Any]) -> dict[str, Any]:
    message_ids: list[int] = []
    media_group_ids: list[str] = []
    for message in results.get("messages", []):
        if isinstance(message, dict) and "message_id" in message:
            message_ids.append(message["message_id"])
    for media_result in results.get("media", []):
        if isinstance(media_result, dict) and "message_id" in media_result:
            message_ids.append(media_result["message_id"])
        elif isinstance(media_result, list):
            for message in media_result:
                if isinstance(message, dict) and "message_id" in message:
                    message_ids.append(message["message_id"])
                if isinstance(message, dict) and message.get("media_group_id"):
                    media_group_ids.append(message["media_group_id"])
    return {
        "message_ids": message_ids,
        "media_group_ids": sorted(set(media_group_ids)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish rendered allmath social post assets to Telegram.")
    parser.add_argument("manifest", type=Path, help="Path to render_social_post.py manifest.json")
    parser.add_argument("--live", action="store_true", help="Actually call Telegram Bot API")
    parser.add_argument(
        "--caption-mode",
        choices=("auto", "message", "album"),
        default="auto",
        help="Where to put post.md text. auto uses album caption when it fits.",
    )
    parser.add_argument(
        "--require-publish-flag",
        action="store_true",
        help="Require source JSON to contain telegram.publish=true; useful for push automation.",
    )
    parser.add_argument("--channel-id", help="Telegram channel id or @username; defaults to TELEGRAM_CHANNEL_ID")
    parser.add_argument("--bot-token-env", default="TELEGRAM_BOT_TOKEN", help="Env var that stores the bot token")
    parser.add_argument("--channel-env", default="TELEGRAM_CHANNEL_ID", help="Env var that stores the channel id")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="Telegram Bot API base URL")
    parser.add_argument("--timeout", type=int, default=45, help="Telegram HTTP timeout in seconds")
    parser.add_argument("--ca-file", type=Path, help="Trusted CA bundle for Telegram HTTPS requests")
    parser.add_argument(
        "--insecure-skip-verify",
        action="store_true",
        help="Disable TLS certificate verification. Use only for a one-off local test.",
    )
    parser.add_argument("--disable-notification", action="store_true", help="Publish silently")
    parser.add_argument("--protect-content", action="store_true", help="Ask Telegram to protect published content")
    parser.add_argument("--json-report", type=Path, help="Optional path to write a JSON publish report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = publish(args)
    except PublishError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output = json.dumps(report, ensure_ascii=False, indent=2)
    print(output)
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(output + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
