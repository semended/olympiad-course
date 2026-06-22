from __future__ import annotations

import html
import importlib.util
import json
import mimetypes
import re
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from fastapi import HTTPException, status


MAX_CAPTION_CHARS = 1024
MAX_MEDIA_GROUP_ITEMS = 10

MATERIAL_STYLE_HELP = """Стиль caption: короткий человеческий комментарий к карточкам.
Референс нужен как настроение, а не как текст для копирования.

#советы_олимпиадникам@allmath

Что хорошего в референсе:
- сразу понятно, что это регулярная рубрика;
- текст короткий и не объясняет всю математику;
- есть живой повод открыть карточки;
- есть мягкое приглашение к реакциям/комментариям;
- нет тяжёлого вступления.

Что НЕ копировать механически:
- одинаковое `Продолжаем с вами...` каждый раз;
- блок `На что обращать внимание? Что делать? Всё как обычно)` в каждом посте;
- одинаковое предупреждение `подсказки не заменяют практику`;
- одинаковые p.s. про файлик или комментарии.

Caption должен звучать как человек, который пишет именно этот пост:
- 2-4 коротких абзаца;
- конкретный повод: какая тема/задача/приём сегодня;
- один лёгкий крючок, почему стоит открыть карточки;
- мягкий финал: попробовать самому, поставить реакцию или написать тему.

Допустимы разные формы: совет, закрепление, разбор, подборка задач. Не надо,
чтобы все они начинались одной фразой."""

POST_FORMAT_RULES = [
  "caption.md — не статья и не условие задачи, а короткий комментарий к карточкам.",
  "Длина caption: обычно 180-650 символов, максимум 800.",
  "Начинать с серийного хэштега `#советы_олимпиадникам@allmath` или близкого allmath-тега.",
  "Не копировать Shkolkovo-паттерн дословно; использовать его только как ориентир по длине и простоте.",
  "Не использовать больше одной стоковой фразы из референса в одном caption.",
  "Caption должен быть конкретным к материалу: тема, задача или приём должны ощущаться в тексте.",
  "CTA мягкий: попробовать самому, поставить реакцию, написать тему, задать вопрос в комментариях.",
  "Не добавлять пафосные метафоры и нейро-красивости; писать проще.",
  "Не делать продажный CTA, не писать мини-лонгрид, не тащить полное решение в caption.",
  "Математика, условия, подсказки и решение живут в карточках.",
  "cards[0..n-2]: идеи/шпаргалки/задачи, каждая карточка несёт одну мысль.",
  "cards[-1] для разбора должна быть `solution`; для чистой шпаргалки можно не раскрывать решение, если задач нет.",
  "Hint-карточки используют пары `На что смотреть?`/`Что делать?` или `Маркер`/`Что делать?`.",
  "Формулы писать в LaTeX без $$; длинные выкладки дробить.",
  "Карточки по умолчанию вертикальные: `size: portrait` для чтения с телефона.",
  "Если исходного решения не хватает, не выдумывать математику.",
]

POST_SPEC_SCHEMA_HINT: dict[str, Any] = {
  "slug": "safe-kebab-slug",
  "brand": {"name": "allmath", "handle": "@allmath"},
  "post": {
    "title": "короткий заголовок до 70 символов",
    "caption": "готовый короткий комментарий к Telegram-посту в стиле рубрики",
    "paragraphs": [
      "fallback only: если caption не используется",
    ],
    "task": "полное условие задачи",
    "prompt": "одно короткое приглашение решить самому",
    "cta": "мягкий финальный комментарий без продажного тона",
    "hashtags": ["#олимпиаднаяматематика", "#математика", "#allmath"],
  },
  "cards": [
    {
      "type": "hint",
      "size": "portrait",
      "theme": "cream|lavender|sky",
      "rubric": "Олимпиадный приём",
      "kicker": "короткий контекст",
      "title": "одна мысль до 42 символов",
      "paragraphs": ["1-2 коротких абзаца, можно **акцент**"],
      "formulas": ["LaTeX без $$"],
      "callouts": [
        {"label": "Маркер", "text": "что заметить"},
        {"label": "Что делать?", "text": "какое действие сделать"},
      ],
    },
    {
      "type": "solution",
      "size": "portrait",
      "theme": "yellow",
      "rubric": "Разбор задачи",
      "title": "короткий заголовок",
      "problem": "сжатое условие",
      "badge": "Решение",
      "steps": [{"text": "один шаг", "formulas": ["LaTeX без $$"]}],
      "answer": "ответ",
    },
  ],
}


@dataclass(frozen=True)
class TelegramPostBotSettings:
  bot_token: str | None
  webhook_secret: str | None
  draft_chat_id: str | None
  allowed_user_ids: set[int]
  ai_api_key: str | None
  ai_api_url: str
  ai_model: str
  public_base_url: str | None
  set_webhook_on_startup: bool


def split_csv_ints(value: str | None) -> set[int]:
  result: set[int] = set()
  for item in (value or "").split(","):
    item = item.strip()
    if not item:
      continue
    result.add(int(item))
  return result


def bool_env(value: str | None) -> bool:
  return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def normalize_public_base_url(value: str | None) -> str | None:
  cleaned = (value or "").strip().rstrip("/")
  if not cleaned:
    return None
  if cleaned.startswith("http://") or cleaned.startswith("https://"):
    return cleaned
  return f"https://{cleaned}"


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
      chunks.append(html.escape(line[cursor:match.start()]))
      chunks.append(f"<b>{html.escape(match.group(1))}</b>")
      cursor = match.end()
    chunks.append(html.escape(line[cursor:]))
    converted.append("".join(chunks))
  return "\n".join(converted).strip()


def slugify(value: str) -> str:
  cleaned = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "-", value.lower()).strip("-")
  cleaned = cleaned[:72].strip("-")
  return cleaned or f"telegram-draft-{int(time.time())}"


def extract_json_object(value: str) -> dict[str, Any]:
  try:
    parsed = json.loads(value)
    if isinstance(parsed, dict):
      return parsed
  except json.JSONDecodeError:
    pass

  start = value.find("{")
  end = value.rfind("}")
  if start >= 0 and end > start:
    parsed = json.loads(value[start:end + 1])
    if isinstance(parsed, dict):
      return parsed

  raise ValueError("AI response does not contain a JSON object")


def build_fallback_spec(material: str) -> dict[str, Any]:
  title = material.splitlines()[0].strip()[:80] if material.strip() else "Черновик разбора"
  return {
    "slug": slugify(title),
    "brand": {"name": "allmath", "handle": "@allmath"},
    "post": {
      "title": title,
      "caption": (
        "#советы_олимпиадникам@allmath\n\n"
        "Собрал технический черновик по присланному материалу. "
        "Карточки ниже пока нужно руками довести: выделить главную идею, проверить решение и убрать лишнее.\n\n"
        "Важно! Просто подсказки без самостоятельного решения не заменяют практику."
      ),
      "paragraphs": [
        "Это технический черновик без AI-генерации: структура готова, но текст и математику нужно дописать руками.",
        "Главная задача ревью — выделить один понятный приём и убрать лишнее до публикации.",
      ],
      "task": material.strip(),
      "prompt": "Сначала попробуй решить сам, потом сверяйся с карточками.",
      "cta": "Если хочется больше таких разборов, оставь реакцию.",
      "hashtags": ["#олимпиаднаяматематика", "#математика", "#allmath"],
    },
    "cards": [
      {
        "type": "hint",
        "size": "portrait",
        "theme": "cream",
        "rubric": "Черновик разбора",
        "kicker": "Идея",
        "title": "Найди главный ход",
        "paragraphs": [
          "Здесь должен быть короткий комментарий: какой объект считаем, какой инвариант ищем или какой переход делает задачу простой."
        ],
        "callouts": [
          {"label": "Маркер", "text": "Проверь, что именно в условии повторяется или сохраняется."},
          {"label": "Что делать?", "text": "Сформулируй один главный ход решения."},
        ],
      },
      {
        "type": "solution",
        "size": "portrait",
        "theme": "yellow",
        "rubric": "Разбор задачи",
        "title": title,
        "problem": material.strip()[:420],
        "badge": "Решение",
        "steps": [
          {"text": "Вставь первый ключевой шаг решения."},
          {"text": "Вставь вычисление или доказательный переход."},
          {"text": "Заверши ответом и проверкой."},
        ],
        "answer": "дописать",
      },
    ],
  }


async def generate_post_spec(material: str, settings: TelegramPostBotSettings) -> dict[str, Any]:
  if not settings.ai_api_key:
    return build_fallback_spec(material)

  system_prompt = (
    "Ты редактор Telegram-канала allmath по олимпиадной математике. "
    "По материалу пользователя сделай черновик рубричного Telegram-поста и карточек. "
    "Главное: короткий комментарий к посту в стиле регулярной рубрики, а не лонгрид. "
    "Верни только JSON. Тон: живой, разговорный, уверенный, без канцелярита, без чрезмерного восторга. "
    "Математику не выдумывай: если решения не хватает, честно пометь это в тексте карточки. "
    "Пиши как редактор Telegram-канала, а не как учебник."
  )
  user_prompt = {
    "material": material,
    "style_reference": MATERIAL_STYLE_HELP,
    "output_schema": POST_SPEC_SCHEMA_HINT,
    "format_rules": POST_FORMAT_RULES,
    "hard_requirements": [
      "Верни валидный JSON-объект без markdown fence.",
      "Не добавляй поля вне output_schema.",
      "Всегда заполняй `post.caption`; renderer возьмёт его как готовый комментарий к посту.",
      "`post.caption` должен быть коротким человеческим комментарием к карточкам, а не шаблоном и не мини-статьёй.",
      "Не копируй style_reference строка-в-строку; максимум одна узнаваемая фраза из референса на caption.",
      "В caption должен быть конкретный повод открыть карточки: тема, приём, тип задачи или что именно закрепляем.",
      "Если это practice-пост, можно сослаться на предыдущую идею и предложить задачи; если solution-пост, коротко объявить разбор.",
      "Не включай полное условие и решение в `post.caption`, если они есть на карточках.",
      "Сделай 2-4 карточки; если это разбор задач, последняя карточка type=solution.",
      "Не используй слово `черновик`, если материал достаточен для нормального поста.",
      "Не пиши `дописать`, если в материале есть ответ или решение.",
      "Не упоминай YouTube, курс, покупку, подписку или вебинар, если пользователь прямо этого не дал.",
      "Избегай нейро-штампов: `в этой задаче скрывается`, `главный ход`, `не утонуть`, `магия`, `ловушка`.",
      "Каждая карточка должна нести новую мысль, а не пересказывать caption.",
    ],
  }

  request_body = {
    "model": settings.ai_model,
    "temperature": 0.35,
    "response_format": {"type": "json_object"},
    "messages": [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
    ],
  }
  headers = {
    "Authorization": f"Bearer {settings.ai_api_key}",
    "Content-Type": "application/json",
  }

  async with httpx.AsyncClient(timeout=90) as client:
    response = await client.post(settings.ai_api_url, headers=headers, json=request_body)

  if response.status_code >= 400:
    raise RuntimeError(f"AI provider returned {response.status_code}")

  content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
  spec = extract_json_object(content)
  spec["slug"] = slugify(str(spec.get("slug") or spec.get("post", {}).get("title") or "telegram-draft"))
  spec.setdefault("brand", {"name": "allmath", "handle": "@allmath"})
  return spec


def load_renderer() -> Any:
  candidates = [
    Path(__file__).resolve().parents[2] / "tools" / "social-post-generator" / "render_social_post.py",
    Path("/app/tools/social-post-generator/render_social_post.py"),
  ]
  for path in candidates:
    if path.exists():
      spec = importlib.util.spec_from_file_location("allmath_social_post_renderer", path)
      if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
  raise RuntimeError("social post renderer not found")


def render_spec_to_tmp(spec: dict[str, Any]) -> dict[str, Any]:
  renderer = load_renderer()
  root = Path(tempfile.mkdtemp(prefix="allmath-telegram-draft-"))
  spec_path = root / "draft.json"
  spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
  return renderer.render_post(spec_path, root / "out")


async def telegram_json(settings: TelegramPostBotSettings, method: str, payload: dict[str, Any]) -> Any:
  if not settings.bot_token:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
  url = f"https://api.telegram.org/bot{settings.bot_token}/{method}"
  async with httpx.AsyncClient(timeout=45) as client:
    response = await client.post(url, json=payload)
  data = response.json()
  if response.status_code >= 400 or not data.get("ok"):
    raise RuntimeError(data.get("description") or f"Telegram {method} failed")
  return data.get("result")


async def telegram_multipart(
  settings: TelegramPostBotSettings,
  method: str,
  fields: dict[str, str],
  files: dict[str, Path],
) -> Any:
  if not settings.bot_token:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
  url = f"https://api.telegram.org/bot{settings.bot_token}/{method}"
  opened = []
  try:
    multipart_files = {}
    for name, path in files.items():
      handle = path.open("rb")
      opened.append(handle)
      mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
      multipart_files[name] = (path.name, handle, mime_type)
    async with httpx.AsyncClient(timeout=90) as client:
      response = await client.post(url, data=fields, files=multipart_files)
  finally:
    for handle in opened:
      handle.close()

  data = response.json()
  if response.status_code >= 400 or not data.get("ok"):
    raise RuntimeError(data.get("description") or f"Telegram {method} failed")
  return data.get("result")


async def send_text(settings: TelegramPostBotSettings, chat_id: str | int, text: str) -> Any:
  return await telegram_json(settings, "sendMessage", {
    "chat_id": chat_id,
    "text": text,
    "parse_mode": "HTML",
    "disable_web_page_preview": True,
  })


async def send_card_album(
  settings: TelegramPostBotSettings,
  chat_id: str | int,
  card_paths: list[Path],
  caption_html: str | None,
) -> Any:
  results = []
  for offset in range(0, len(card_paths), MAX_MEDIA_GROUP_ITEMS):
    chunk = card_paths[offset:offset + MAX_MEDIA_GROUP_ITEMS]
    if len(chunk) == 1:
      fields = {"chat_id": str(chat_id)}
      if caption_html and offset == 0:
        fields["caption"] = caption_html
        fields["parse_mode"] = "HTML"
      results.append(await telegram_multipart(settings, "sendPhoto", fields, {"photo": chunk[0]}))
      continue

    media: list[dict[str, str]] = []
    files: dict[str, Path] = {}
    for index, path in enumerate(chunk):
      field = f"photo{offset + index}"
      item = {"type": "photo", "media": f"attach://{field}"}
      if caption_html and offset == 0 and index == 0:
        item["caption"] = caption_html
        item["parse_mode"] = "HTML"
      media.append(item)
      files[field] = path
    fields = {"chat_id": str(chat_id), "media": json.dumps(media, ensure_ascii=False)}
    results.append(await telegram_multipart(settings, "sendMediaGroup", fields, files))
  return results


async def deliver_draft_to_telegram(
  manifest: dict[str, Any],
  settings: TelegramPostBotSettings,
  source_chat_id: int,
) -> None:
  target_chat_id: str | int = settings.draft_chat_id or source_chat_id
  caption_path = Path(str(manifest["caption"]))
  review_path = Path(str(manifest["review"]))
  card_paths = [Path(str(path)) for path in manifest["cards"]]
  caption_md = caption_path.read_text(encoding="utf-8")
  caption_html = markdownish_to_telegram_html(caption_md)
  warnings = manifest.get("warnings") or []

  header = (
    f"📝 <b>Черновик поста готов</b>\n"
    f"slug: <code>{html.escape(str(manifest.get('slug', 'draft')))}</code>\n\n"
    "Это не публикация в основной канал. Проверь текст и карточки здесь."
  )
  await send_text(settings, target_chat_id, header)

  if len(caption_html) <= MAX_CAPTION_CHARS:
    await send_card_album(settings, target_chat_id, card_paths, caption_html)
  else:
    await send_text(settings, target_chat_id, caption_html)
    await send_card_album(settings, target_chat_id, card_paths, None)

  review_text = html.escape(review_path.read_text(encoding="utf-8")[:3600])
  await send_text(settings, target_chat_id, f"<b>Review / комментарии</b>\n<pre>{review_text}</pre>")

  if warnings:
    await send_text(settings, target_chat_id, "<b>Render warnings</b>\n" + html.escape("\n".join(map(str, warnings))))


def extract_update_text(update: dict[str, Any]) -> tuple[int, int, str] | None:
  message = update.get("message") or update.get("edited_message")
  if not isinstance(message, dict):
    return None
  chat = message.get("chat") or {}
  user = message.get("from") or {}
  chat_id = chat.get("id")
  user_id = user.get("id")
  text = message.get("text") or message.get("caption") or ""
  if not isinstance(chat_id, int) or not isinstance(user_id, int):
    return None
  return chat_id, user_id, text.strip()


async def handle_telegram_post_update(update: dict[str, Any], settings: TelegramPostBotSettings) -> dict[str, Any]:
  extracted = extract_update_text(update)
  if not extracted:
    return {"ok": True, "ignored": "unsupported_update"}

  chat_id, user_id, material = extracted
  if settings.allowed_user_ids and user_id not in settings.allowed_user_ids:
    await send_text(settings, chat_id, "Нет доступа к генерации черновиков.")
    return {"ok": True, "ignored": "unauthorized_user"}

  if not material or material.startswith("/start"):
    await send_text(
      settings,
      chat_id,
      "Кидай сюда материал для поста: тему, задачи, шпаргалку или решение. "
      "Я соберу рубричный комментарий, карточки и review-комменты. Для описания стиля отправь /format.",
    )
    return {"ok": True, "message": "help_sent"}

  if material.startswith("/format"):
    await send_text(settings, chat_id, "<pre>" + html.escape(MATERIAL_STYLE_HELP) + "</pre>")
    return {"ok": True, "message": "format_sent"}

  if material.startswith("/"):
    await send_text(settings, chat_id, "Команды: /format. Или просто пришли материал одним сообщением.")
    return {"ok": True, "message": "command_ignored"}

  await send_text(settings, chat_id, "Принял. Генерю черновик, карточки и review-комменты.")

  try:
    spec = await generate_post_spec(material, settings)
    manifest = render_spec_to_tmp(spec)
    await deliver_draft_to_telegram(manifest, settings, chat_id)
  except Exception as exc:
    await send_text(settings, chat_id, f"Не смог собрать черновик: <code>{html.escape(str(exc))}</code>")
    raise

  return {"ok": True, "slug": manifest.get("slug")}


async def maybe_set_telegram_webhook(settings: TelegramPostBotSettings) -> None:
  if not settings.bot_token or not settings.webhook_secret:
    return
  if not settings.public_base_url or not settings.set_webhook_on_startup:
    return

  webhook_url = settings.public_base_url.rstrip("/") + f"/api/telegram/post-drafts/{settings.webhook_secret}"
  await telegram_json(settings, "setWebhook", {
    "url": webhook_url,
    "allowed_updates": ["message", "edited_message"],
    "drop_pending_updates": False,
  })


def require_telegram_config(settings: TelegramPostBotSettings) -> None:
  if not settings.bot_token:
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="TELEGRAM_BOT_TOKEN is not configured")
  if not settings.webhook_secret:
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="TELEGRAM_WEBHOOK_SECRET is not configured")
