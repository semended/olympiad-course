#!/usr/bin/env python3
"""Render allmath Telegram post drafts into PNG cards and a post.md file.

The generator is intentionally deterministic: copy, layout, formulas and
background assets are explicit data. Codex can author the JSON draft from a
task/solution, while this script handles repeatable production output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "tmp" / "social-posts"

FontSpec: TypeAlias = Path | tuple[Path, int]

CARD_SIZES = {
    "mobile": (1080, 1350),
    "portrait": (1080, 1350),
    "square": (1280, 1280),
}

FONT_PATHS: dict[str, list[FontSpec]] = {
    "regular": [
        ROOT / "assets/fonts/Manrope-Regular.ttf",
        (Path("/System/Library/Fonts/Avenir Next.ttc"), 7),
        Path("/System/Library/Fonts/SFNS.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ],
    "bold": [
        ROOT / "assets/fonts/Manrope-Bold.ttf",
        (Path("/System/Library/Fonts/Avenir Next.ttc"), 0),
        Path("/System/Library/Fonts/SFNS.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ],
    "heavy": [
        ROOT / "assets/fonts/Manrope-ExtraBold.ttf",
        ROOT / "assets/fonts/Manrope-Bold.ttf",
        (Path("/System/Library/Fonts/Avenir Next.ttc"), 0),
        Path("/System/Library/Fonts/SFNS.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Black.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ],
    "italic": [
        ROOT / "assets/fonts/Manrope-Regular.ttf",
        (Path("/System/Library/Fonts/Avenir Next.ttc"), 4),
        Path("/System/Library/Fonts/SFNSItalic.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Italic.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Italic.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
    ],
}

THEMES: dict[str, dict[str, Any]] = {
    "cream": {
        "bg_top": "#fff9ea",
        "bg_bottom": "#edf8ff",
        "bg_mid": "#fff4c5",
        "ink": "#090910",
        "muted": "#5e584d",
        "accent": "#ffe24a",
        "accent_2": "#9fd6ff",
        "accent_dark": "#090910",
        "badge": "#111111",
        "badge_text": "#ffffff",
        "soft": "#fff0a6",
        "panel": "#ffffff",
        "decor": [
            {"path": "public/brand/allmath/artifacts/glossy/trophy_cup_balloon.png", "pos": "top_right", "size": 230, "opacity": 0.14, "rotate": -15, "dx": 38, "dy": -8},
            {"path": "public/brand/allmath/artifacts/glossy/key_balloon.png", "pos": "right_mid", "size": 175, "opacity": 0.10, "rotate": 8, "dx": 44, "dy": -42},
            {"path": "public/brand/allmath/artifacts/pixel/star.png", "pos": "bottom_left", "size": 128, "opacity": 0.22, "rotate": 9, "dx": 18, "dy": -20},
            {"path": "public/assets/allmath/balloons/02_rocket_balloon.png", "pos": "bottom_right", "size": 250, "opacity": 0.10, "rotate": -10, "dx": 48, "dy": 8},
        ],
    },
    "lavender": {
        "bg_top": "#fff8ea",
        "bg_bottom": "#efe7ff",
        "bg_mid": "#e5dcff",
        "ink": "#23035f",
        "muted": "#463d5f",
        "accent": "#bda5ff",
        "accent_2": "#ffbd79",
        "accent_dark": "#240067",
        "badge": "#240067",
        "badge_text": "#ffffff",
        "soft": "#ffffff",
        "panel": "#ffffff",
        "decor": [
            {"path": "public/brand/allmath/artifacts/glossy/crystal_balloon.png", "pos": "top_right", "size": 225, "opacity": 0.20, "rotate": 12, "dx": 34, "dy": -4},
            {"path": "public/brand/allmath/artifacts/glossy/diamond_balloon.png", "pos": "left_mid", "size": 145, "opacity": 0.11, "rotate": -10, "dx": -28, "dy": 24},
            {"path": "public/assets/allmath/balloons/03_star_balloon.png", "pos": "bottom_right", "size": 235, "opacity": 0.13, "rotate": -4, "dx": 36, "dy": 6},
            {"path": "public/brand/allmath/artifacts/pixel/cup_pi.png", "pos": "bottom_left", "size": 132, "opacity": 0.24, "rotate": 8, "dx": 16, "dy": -14},
        ],
    },
    "yellow": {
        "bg_top": "#fff1a9",
        "bg_bottom": "#ffd84d",
        "bg_mid": "#fff9df",
        "ink": "#15120b",
        "muted": "#514726",
        "accent": "#ff3d83",
        "accent_2": "#7a5cff",
        "accent_dark": "#15120b",
        "badge": "#ff3d83",
        "badge_text": "#ffffff",
        "soft": "#fff6b6",
        "panel": "#fff9df",
        "decor": [
            {"path": "public/brand/allmath/artifacts/glossy/medal_balloon.png", "pos": "right_mid", "size": 265, "opacity": 0.20, "rotate": -7, "dx": 46, "dy": -20},
            {"path": "public/brand/allmath/artifacts/pixel/lightning.png", "pos": "top_left", "size": 112, "opacity": 0.20, "rotate": 8, "dx": 20, "dy": 132},
            {"path": "public/assets/allmath/balloons/01_trophy_balloon.png", "pos": "bottom_left", "size": 210, "opacity": 0.12, "rotate": 12, "dx": -4, "dy": -8},
        ],
    },
    "sky": {
        "bg_top": "#f8fbff",
        "bg_bottom": "#d7f0ff",
        "bg_mid": "#e9fbff",
        "ink": "#071a2f",
        "muted": "#36536a",
        "accent": "#7a5cff",
        "accent_2": "#9cf4cd",
        "accent_dark": "#071a2f",
        "badge": "#071a2f",
        "badge_text": "#ffffff",
        "soft": "#ffffff",
        "panel": "#ffffff",
        "decor": [
            {"path": "public/brand/allmath/artifacts/glossy/rocket_balloon.png", "pos": "top_right", "size": 245, "opacity": 0.22, "rotate": 10, "dx": 36, "dy": -6},
            {"path": "public/brand/allmath/artifacts/glossy/flag_balloon.png", "pos": "right_mid", "size": 155, "opacity": 0.12, "rotate": -6, "dx": 54, "dy": 48},
            {"path": "public/brand/allmath/artifacts/pixel/compass.png", "pos": "bottom_left", "size": 138, "opacity": 0.24, "rotate": -8, "dx": 18, "dy": -14},
        ],
    },
}


@dataclass(frozen=True)
class RenderedFormula:
    image: Image.Image | None
    warning: str | None = None


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected #RRGGBB color, got {value!r}")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def lerp(a: int, b: int, t: float) -> int:
    return int(round(a + (b - a) * t))


def mix_rgb(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(lerp(a[i], b[i], t) for i in range(3))


def color_with_alpha(value: str, alpha: int) -> tuple[int, int, int, int]:
    return (*hex_to_rgb(value), alpha)


def layout_margin(width: int) -> int:
    return 76 if width <= 1080 else 96


def load_font(kind: str, size: int) -> ImageFont.ImageFont:
    candidates = [*FONT_PATHS.get(kind, []), *FONT_PATHS["regular"]]
    for spec in candidates:
        if isinstance(spec, tuple):
            path, index = spec
        else:
            path, index = spec, 0
        if path.exists():
            return ImageFont.truetype(str(path), size=size, index=index)
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


def latex_main_font() -> tuple[str, str | None]:
    manrope = ROOT / "assets/fonts/Manrope-Regular.ttf"
    if manrope.exists():
        return manrope.name, str(manrope.parent) + "/"
    if Path("/System/Library/Fonts/Avenir Next.ttc").exists():
        return "Avenir Next", None
    if Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf").exists():
        return "Liberation Sans", None
    return "DejaVu Sans", None


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    if not text:
        return 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text or "Ag", font=font)
    return bbox[3] - bbox[1]


def split_markup(text: str) -> list[tuple[str, bool]]:
    """Split a small markdown-ish string into regular/bold spans."""

    spans: list[tuple[str, bool]] = []
    is_bold = False
    buffer: list[str] = []
    index = 0
    while index < len(text):
        if text.startswith("**", index):
            if buffer:
                spans.append(("".join(buffer), is_bold))
                buffer = []
            is_bold = not is_bold
            index += 2
            continue
        buffer.append(text[index])
        index += 1
    if buffer:
        spans.append(("".join(buffer), is_bold))
    return spans


def tokenize_spans(spans: list[tuple[str, bool]]) -> list[tuple[str, bool, bool]]:
    tokens: list[tuple[str, bool, bool]] = []
    for text, bold in spans:
        for raw in re.findall(r"\s+|\S+", text):
            tokens.append((raw, bold, raw.isspace()))
    return tokens


def wrap_rich_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    regular: ImageFont.ImageFont,
    bold: ImageFont.ImageFont,
) -> list[list[tuple[str, bool, bool]]]:
    lines: list[list[tuple[str, bool, bool]]] = []
    current: list[tuple[str, bool, bool]] = []
    current_width = 0
    space_regular = text_width(draw, " ", regular)
    tokens = tokenize_spans(split_markup(text))
    pending_space = False

    for token, is_bold, is_space in tokens:
        if is_space and "\n" in token:
            if current:
                lines.append(current)
            current = []
            current_width = 0
            pending_space = False
            continue
        if is_space:
            pending_space = bool(current)
            continue

        font = bold if is_bold else regular
        token_width = text_width(draw, token, font)
        add_space = pending_space and bool(current)
        next_width = current_width + (space_regular if add_space else 0) + token_width
        if current and next_width > max_width:
            lines.append(current)
            current = [(token, is_bold, False)]
            current_width = token_width
        else:
            current.append((token, is_bold, add_space))
            current_width = next_width
        pending_space = False

    if current:
        lines.append(current)
    return lines


def draw_rich_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    max_width: int,
    regular: ImageFont.ImageFont,
    bold: ImageFont.ImageFont,
    fill: str,
    *,
    line_gap: int = 10,
) -> int:
    x, y = xy
    lines = wrap_rich_text(draw, text, max_width, regular, bold)
    line_height = max(text_height(draw, "Ag", regular), text_height(draw, "Ag", bold)) + line_gap
    for line in lines:
        cursor = x
        for token, is_bold, add_space in line:
            if add_space:
                cursor += text_width(draw, " ", regular)
            font = bold if is_bold else regular
            draw.text((cursor, y), token, font=font, fill=fill)
            cursor += text_width(draw, token, font)
        y += line_height
    return y


def measure_rich_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    regular: ImageFont.ImageFont,
    bold: ImageFont.ImageFont,
    *,
    line_gap: int = 10,
) -> int:
    lines = wrap_rich_text(draw, text, max_width, regular, bold)
    if not lines:
        return 0
    line_height = max(text_height(draw, "Ag", regular), text_height(draw, "Ag", bold)) + line_gap
    return len(lines) * line_height - line_gap


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    max_width: int,
    font: ImageFont.ImageFont,
    fill: str,
    *,
    line_gap: int = 10,
) -> int:
    return draw_rich_text(draw, text, xy, max_width, font, font, fill, line_gap=line_gap)


def draw_plus(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    size: int,
    fill: tuple[int, int, int, int],
    *,
    width: int = 3,
) -> None:
    x, y = center
    half = size // 2
    draw.line((x - half, y, x + half, y), fill=fill, width=width)
    draw.line((x, y - half, x, y + half), fill=fill, width=width)


def draw_math_texture(draw: ImageDraw.ImageDraw, size: tuple[int, int], theme: dict[str, Any]) -> None:
    width, height = size
    ink = hex_to_rgb(theme["ink"])
    accent = hex_to_rgb(theme["accent"])
    accent_2 = hex_to_rgb(theme.get("accent_2", theme["accent"]))

    for x in range(34, width, 112):
        for y in range(52, height, 118):
            if (x + y) % 4 == 0:
                draw.ellipse((x, y, x + 3, y + 3), fill=(*ink, 18))

    for index, (rx, ry, label, scale) in enumerate(
        [
            (0.12, 0.17, "x+7", 0.80),
            (0.74, 0.22, "A=B", 0.86),
            (0.20, 0.48, "1:1", 0.76),
            (0.84, 0.55, "n^2", 0.82),
            (0.18, 0.78, "77", 0.92),
            (0.72, 0.84, "mod", 0.72),
        ]
    ):
        font = load_font("bold", int(30 * scale))
        base_color = accent if index % 2 == 0 else accent_2
        color = (*base_color, 26)
        draw.text((int(width * rx), int(height * ry)), label, font=font, fill=color)

    for rx, ry, plus_size, color in [
        (0.08, 0.33, 22, (*accent, 76)),
        (0.58, 0.13, 18, (*accent_2, 62)),
        (0.90, 0.38, 24, (*ink, 30)),
        (0.12, 0.64, 18, (*accent_2, 60)),
        (0.80, 0.73, 20, (*accent, 64)),
    ]:
        draw_plus(draw, (int(width * rx), int(height * ry)), plus_size, color)

    for rx, ry, box_w, box_h, color in [
        (0.05, 0.88, 54, 54, (*accent, 38)),
        (0.63, 0.06, 44, 44, (*accent_2, 44)),
        (0.86, 0.68, 46, 46, (*ink, 18)),
    ]:
        x = int(width * rx)
        y = int(height * ry)
        draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=10, outline=color, width=3)


def build_background(size: tuple[int, int], theme: dict[str, Any]) -> Image.Image:
    width, height = size
    top = hex_to_rgb(theme["bg_top"])
    mid = hex_to_rgb(theme.get("bg_mid", theme["bg_top"]))
    bottom = hex_to_rgb(theme["bg_bottom"])
    image = Image.new("RGBA", size, (255, 255, 255, 255))
    pixels = image.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        if t < 0.52:
            row_rgb = mix_rgb(top, mid, t / 0.52)
        else:
            row_rgb = mix_rgb(mid, bottom, (t - 0.52) / 0.48)
        for x in range(width):
            x_factor = x / max(width - 1, 1)
            light = int(8 * math.sin((x_factor + t) * math.pi))
            pixels[x, y] = tuple(max(0, min(255, channel + light)) for channel in row_rgb) + (255,)

    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    accent = hex_to_rgb(theme["accent"])
    accent_2 = hex_to_rgb(theme.get("accent_2", theme["accent"]))
    ink = hex_to_rgb(theme["ink"])

    draw.rounded_rectangle(
        (width * 0.50, height * 0.06, width * 1.08, height * 0.38),
        radius=54,
        fill=color_with_alpha(theme.get("panel", "#ffffff"), 116),
        outline=(*accent, 22),
        width=2,
    )
    draw.rounded_rectangle(
        (-width * 0.20, height * 0.62, width * 0.48, height * 1.06),
        radius=58,
        fill=color_with_alpha(theme["soft"], 82),
        outline=(*accent_2, 24),
        width=2,
    )
    draw.rounded_rectangle(
        (width * 0.12, height * 0.80, width * 0.92, height * 1.12),
        radius=46,
        fill=(255, 255, 255, 38),
    )

    for x in range(-height, width + height, 88):
        draw.line((x, 0, x + height, height), fill=(*accent, 16), width=2)
    for x in range(-height // 2, width + height, 176):
        draw.line((x, 0, x + height, height), fill=(*accent_2, 16), width=1)
    for y in range(126, height, 172):
        draw.line((0, y, width, y - 74), fill=(*ink, 9), width=1)

    draw_math_texture(draw, size, theme)

    grain = Image.new("RGBA", size, (0, 0, 0, 0))
    grain_pixels = grain.load()
    for y in range(0, height, 3):
        for x in range(0, width, 3):
            value = ((x * 17 + y * 31) % 13) - 6
            if value > 2:
                grain_pixels[x, y] = (255, 255, 255, 18)
            elif value < -3:
                grain_pixels[x, y] = (*ink, 6)
    layer = Image.alpha_composite(layer, grain)
    return Image.alpha_composite(image, layer)


def fit_asset(image: Image.Image, target: int, opacity: float, rotate: float) -> Image.Image:
    asset = image.convert("RGBA")
    if rotate:
        asset = asset.rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)
    scale = target / max(asset.width, asset.height)
    asset = asset.resize((max(1, int(asset.width * scale)), max(1, int(asset.height * scale))), Image.Resampling.LANCZOS)
    if opacity < 1:
        alpha = asset.getchannel("A").point(lambda value: int(value * opacity))
        asset.putalpha(alpha)
    return asset


def paste_decor(canvas: Image.Image, theme: dict[str, Any], explicit_decor: list[dict[str, Any]] | None = None) -> None:
    width, height = canvas.size
    decor_items = explicit_decor if explicit_decor is not None else theme.get("decor", [])
    for item in decor_items:
        path = ROOT / item["path"]
        if not path.exists():
            continue
        asset = fit_asset(
            Image.open(path),
            int(item.get("size", 260)),
            float(item.get("opacity", 0.18)),
            float(item.get("rotate", 0)),
        )
        pos = item.get("pos", "top_right")
        if pos == "top_right":
            xy = (width - asset.width + int(item.get("dx", 24)), -int(asset.height * 0.18) + int(item.get("dy", 0)))
        elif pos == "top_left":
            xy = (-int(asset.width * 0.18) + int(item.get("dx", 0)), -int(asset.height * 0.12) + int(item.get("dy", 0)))
        elif pos == "bottom_right":
            xy = (width - asset.width + int(item.get("dx", 30)), height - asset.height + int(item.get("dy", 26)))
        elif pos == "bottom_left":
            xy = (-int(asset.width * 0.18) + int(item.get("dx", 0)), height - asset.height + int(item.get("dy", 22)))
        elif pos == "right_mid":
            xy = (width - asset.width + int(item.get("dx", 42)), int(height * 0.45 - asset.height / 2) + int(item.get("dy", 0)))
        elif pos == "left_mid":
            xy = (-int(asset.width * 0.28) + int(item.get("dx", 0)), int(height * 0.48 - asset.height / 2) + int(item.get("dy", 0)))
        else:
            xy = (int(item.get("x", 0)), int(item.get("y", 0)))
        canvas.alpha_composite(asset, xy)


class FormulaRenderer:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.xelatex = shutil.which("xelatex")
        self.pdftocairo = shutil.which("pdftocairo")
        self.latex_font, self.latex_font_path = latex_main_font()

    @property
    def available(self) -> bool:
        return bool(self.xelatex and self.pdftocairo)

    def render(self, latex: str, *, color: str, font_size: int = 32) -> RenderedFormula:
        if not self.available:
            return RenderedFormula(None, "xelatex/pdftocairo not found; formula drawn as fallback text")

        color_hex = rgb_to_hex(hex_to_rgb(color))
        digest = hashlib.sha1(
            f"formula-v3|{latex}|{color_hex}|{font_size}|{self.latex_font}|{self.latex_font_path}".encode("utf-8")
        ).hexdigest()[:16]
        item_dir = self.cache_dir / digest
        png_path = item_dir / "formula.png"
        if png_path.exists():
            return RenderedFormula(crop_transparent(Image.open(png_path).convert("RGBA")))

        item_dir.mkdir(parents=True, exist_ok=True)
        tex_path = item_dir / "formula.tex"
        pdf_path = item_dir / "formula.pdf"
        font_options = f"[Path={self.latex_font_path}]" if self.latex_font_path else ""
        tex = textwrap.dedent(
            rf"""
            \documentclass[12pt]{{article}}
            \usepackage[paperwidth=20in,paperheight=4in,margin=0.05in]{{geometry}}
            \usepackage{{amsmath,amssymb,xcolor,fontspec}}
            \setmainfont{font_options}{{{self.latex_font}}}
            \pagestyle{{empty}}
            \setlength{{\parindent}}{{0pt}}
            \begin{{document}}
            {{\color[HTML]{{{color_hex}}}\fontsize{{{font_size}}}{{{int(font_size * 1.2)}}}\selectfont \[
            {latex}
            \]}}
            \end{{document}}
            """
        ).strip()
        tex_path.write_text(tex, encoding="utf-8")

        try:
            subprocess.run(
                [self.xelatex, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
                cwd=item_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=20,
            )
            subprocess.run(
                [self.pdftocairo, "-png", "-transp", "-singlefile", "-r", "230", str(pdf_path), str(item_dir / "formula")],
                cwd=item_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=20,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            log = item_dir / "formula-error.log"
            output = getattr(exc, "stdout", "") or str(exc)
            log.write_text(output, encoding="utf-8")
            return RenderedFormula(None, f"Formula failed: {latex!r}; see {log}")

        if not png_path.exists():
            return RenderedFormula(None, f"Formula PNG was not created for {latex!r}")
        return RenderedFormula(crop_transparent(Image.open(png_path).convert("RGBA")))


def crop_transparent(image: Image.Image, padding: int = 8) -> Image.Image:
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return image
    cropped = image.crop(bbox)
    out = Image.new("RGBA", (cropped.width + padding * 2, cropped.height + padding * 2), (0, 0, 0, 0))
    out.alpha_composite(cropped, (padding, padding))
    return out


def resize_to_width(image: Image.Image, max_width: int, max_height: int | None = None) -> Image.Image:
    scale = min(1.0, max_width / image.width)
    if max_height is not None:
        scale = min(scale, max_height / image.height)
    if scale >= 1:
        return image
    return image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))), Image.Resampling.LANCZOS)


def paste_centered(canvas: Image.Image, image: Image.Image, y: int, max_width: int, max_height: int | None = None) -> int:
    image = resize_to_width(image, max_width, max_height)
    x = int((canvas.width - image.width) / 2)
    canvas.alpha_composite(image, (x, y))
    return y + image.height


def draw_badge_row(
    draw: ImageDraw.ImageDraw,
    label: str,
    body: str,
    *,
    x: int,
    y: int,
    label_width: int,
    body_width: int,
    theme: dict[str, Any],
    body_font: ImageFont.ImageFont,
    body_bold: ImageFont.ImageFont,
) -> int:
    label_font = load_font("bold", 22)
    badge_height = 48
    draw.rounded_rectangle(
        (x, y + 4, x + label_width, y + badge_height + 4),
        radius=0,
        fill=theme["badge"],
    )
    label_bbox = draw.textbbox((0, 0), label, font=label_font)
    label_x = x + (label_width - (label_bbox[2] - label_bbox[0])) // 2
    draw.text((label_x, y + 15), label, font=label_font, fill=theme["badge_text"])
    body_x = x + label_width + 32
    body_y = y
    next_y = draw_rich_text(
        draw,
        body,
        (body_x, body_y),
        body_width,
        body_font,
        body_bold,
        theme["ink"],
        line_gap=10,
    )
    return max(y + badge_height + 18, next_y + 14)


def draw_telegram_icon(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int) -> None:
    cx, cy = center
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill="#229ed9")
    draw.ellipse((cx - radius + 5, cy - radius + 5, cx + radius - 5, cy + radius - 5), outline=(255, 255, 255, 44), width=2)
    plane = [
        (cx - int(radius * 0.58), cy - int(radius * 0.06)),
        (cx + int(radius * 0.58), cy - int(radius * 0.50)),
        (cx + int(radius * 0.20), cy + int(radius * 0.54)),
        (cx - int(radius * 0.05), cy + int(radius * 0.18)),
        (cx - int(radius * 0.30), cy + int(radius * 0.34)),
        (cx - int(radius * 0.18), cy + int(radius * 0.10)),
    ]
    draw.polygon(plane, fill="#ffffff")
    draw.polygon(
        [
            (cx - int(radius * 0.18), cy + int(radius * 0.10)),
            (cx + int(radius * 0.36), cy - int(radius * 0.36)),
            (cx - int(radius * 0.05), cy + int(radius * 0.18)),
        ],
        fill="#d9f3ff",
    )


def draw_footer(draw: ImageDraw.ImageDraw, canvas: Image.Image, brand: dict[str, str], theme: dict[str, Any]) -> None:
    width, height = canvas.size
    handle = brand.get("handle", "@allmath")
    handle_font = load_font("bold", 30 if width <= 1080 else 32)
    handle_w = text_width(draw, handle, handle_font)
    icon_r = 28
    pad_x = 18
    gap = 14
    pill_h = 68
    pill_w = pad_x * 2 + icon_r * 2 + gap + handle_w
    x = width - layout_margin(width) - pill_w
    y = height - 104

    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    layer_draw.rounded_rectangle((x + 8, y + 9, x + pill_w + 8, y + pill_h + 9), radius=22, fill=(7, 26, 47, 22))
    layer_draw.rounded_rectangle(
        (x, y, x + pill_w, y + pill_h),
        radius=22,
        fill=(255, 255, 255, 202),
        outline=(*hex_to_rgb(theme["ink"]), 22),
        width=1,
    )
    canvas.alpha_composite(layer)

    cy = y + pill_h // 2
    cx = x + pad_x + icon_r
    draw_telegram_icon(draw, (cx, cy), icon_r)
    draw.text((cx + icon_r + gap, y + 18), handle, font=handle_font, fill=theme["ink"])


def draw_header(draw: ImageDraw.ImageDraw, card: dict[str, Any], theme: dict[str, Any], width: int) -> int:
    rubric = card.get("rubric", "Олимпиадная математика")
    number = card.get("number")
    margin = layout_margin(width)
    draw.text((margin, 86), rubric, font=load_font("bold", 28), fill=theme["accent_dark"])
    if number:
        number_font = load_font("regular", 22)
        draw.text((width - margin - text_width(draw, str(number), number_font), 92), str(number), font=number_font, fill=theme["muted"])
    kicker = card.get("kicker", "")
    if kicker:
        draw.text((margin, 166), kicker, font=load_font("regular", 28), fill=theme["muted"])
        return 226
    return 164


def draw_formula_block(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    formula_renderer: FormulaRenderer,
    formula: str | dict[str, Any],
    *,
    y: int,
    max_width: int,
    theme: dict[str, Any],
    warnings: list[str],
    font_size: int = 34,
) -> int:
    latex = formula.get("latex") if isinstance(formula, dict) else str(formula)
    caption = formula.get("caption") if isinstance(formula, dict) else None
    result = formula_renderer.render(latex, color=theme["accent_dark"], font_size=font_size)
    if result.warning:
        warnings.append(result.warning)
    if result.image is not None:
        y = paste_centered(canvas, result.image, y, max_width, 170)
    else:
        fallback_font = load_font("bold", max(26, font_size - 3))
        lines = textwrap.wrap(latex, width=44)
        for line in lines:
            w = text_width(draw, line, fallback_font)
            draw.text(((canvas.width - w) // 2, y), line, font=fallback_font, fill=theme["accent_dark"])
            y += text_height(draw, line, fallback_font) + 8
    if caption:
        caption_font = load_font("regular", 22)
        caption_w = text_width(draw, caption, caption_font)
        draw.text(((canvas.width - caption_w) // 2, y + 8), caption, font=caption_font, fill=theme["muted"])
        y += 40
    return y + 28


def render_hint_card(
    card: dict[str, Any],
    brand: dict[str, str],
    out_path: Path,
    formula_renderer: FormulaRenderer,
    warnings: list[str],
) -> None:
    theme = THEMES.get(card.get("theme", "cream"), THEMES["cream"]).copy()
    theme.update(card.get("theme_overrides", {}))
    size = CARD_SIZES.get(card.get("size", "portrait"), CARD_SIZES["portrait"])
    canvas = build_background(size, theme)
    paste_decor(canvas, theme, card.get("decor"))
    draw = ImageDraw.Draw(canvas)

    y = draw_header(draw, card, theme, size[0])
    margin = layout_margin(size[0])
    title = card["title"]
    title_font_size = 64 if size[0] >= 1200 else 54
    title_font = load_font("heavy", title_font_size)
    title_width = size[0] - margin * 2
    y = draw_wrapped_text(draw, title, (margin, y), title_width, title_font, theme["ink"], line_gap=8) + 32

    body_font = load_font("regular", 29 if size[0] <= 1080 else 31)
    body_bold = load_font("bold", 29 if size[0] <= 1080 else 31)
    paragraph_width = size[0] - margin * 2
    for paragraph in card.get("paragraphs", []):
        y = draw_rich_text(draw, paragraph, (margin, y), paragraph_width, body_font, body_bold, theme["ink"], line_gap=11) + 18

    for formula in card.get("formulas", []):
        y = draw_formula_block(
            canvas,
            draw,
            formula_renderer,
            formula,
            y=y,
            max_width=size[0] - 260,
            theme=theme,
            warnings=warnings,
            font_size=34 if size[0] <= 1080 else 36,
        )

    callouts = card.get("callouts", [])
    if callouts:
        y += 10
    label_width = 150
    body_width = size[0] - margin * 2 - label_width - 28
    for callout in callouts:
        y = draw_badge_row(
            draw,
            callout["label"],
            callout["text"],
            x=margin,
            y=y,
            label_width=label_width,
            body_width=body_width,
            theme=theme,
            body_font=body_font,
            body_bold=body_bold,
        )

    if y > size[1] - 150:
        warnings.append(f"{out_path.name}: content reaches footer area; shorten card copy or split into two cards")

    draw_footer(draw, canvas, brand, theme)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, optimize=True)


def render_solution_card(
    card: dict[str, Any],
    brand: dict[str, str],
    out_path: Path,
    formula_renderer: FormulaRenderer,
    warnings: list[str],
) -> None:
    theme = THEMES.get(card.get("theme", "yellow"), THEMES["yellow"]).copy()
    theme.update(card.get("theme_overrides", {}))
    size = CARD_SIZES.get(card.get("size", "portrait"), CARD_SIZES["portrait"])
    canvas = build_background(size, theme)
    paste_decor(canvas, theme, card.get("decor"))
    draw = ImageDraw.Draw(canvas)

    draw_header(draw, card, theme, size[0])
    margin = layout_margin(size[0])
    y = 178
    title_font = load_font("heavy", 54 if size[0] <= 1080 else 58)
    y = draw_wrapped_text(draw, card["title"], (margin, y), size[0] - margin * 2, title_font, theme["ink"], line_gap=8) + 22

    if card.get("problem"):
        problem_font = load_font("regular", 26)
        y = draw_rich_text(draw, card["problem"], (margin, y), size[0] - margin * 2, problem_font, load_font("bold", 26), theme["ink"], line_gap=9) + 26

    badge_font = load_font("bold", 24)
    badge_text = card.get("badge", "Решение")
    badge_w = max(132, text_width(draw, badge_text, badge_font) + 42)
    draw.rounded_rectangle((margin, y, margin + badge_w, y + 46), radius=0, fill=theme["badge"])
    draw.text((margin + 21, y + 11), badge_text, font=badge_font, fill=theme["badge_text"])
    y += 82

    step_font = load_font("regular", 23)
    step_bold = load_font("bold", 23)
    number_font = load_font("bold", 24)
    for index, step in enumerate(card.get("steps", []), start=1):
        draw.text((margin, y + 2), f"{index}.", font=number_font, fill=theme["ink"])
        body_x = margin + 36
        text = step.get("text", "") if isinstance(step, dict) else str(step)
        y = draw_rich_text(draw, text, (body_x, y), size[0] - body_x - margin, step_font, step_bold, theme["ink"], line_gap=8) + 10
        formulas = step.get("formulas", []) if isinstance(step, dict) else []
        for formula in formulas:
            y = draw_formula_block(
                canvas,
                draw,
                formula_renderer,
                formula,
                y=y,
                max_width=size[0] - 220,
                theme=theme,
                warnings=warnings,
                font_size=27,
            )
        y += 10

    if card.get("answer"):
        answer_font = load_font("bold", 25)
        y += 8
        draw.text((margin, y), f"Ответ: {card['answer']}", font=answer_font, fill=theme["ink"])

    if y > size[1] - 152:
        warnings.append(f"{out_path.name}: solution content is too tall; split steps into another card")

    draw_footer(draw, canvas, brand, theme)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, optimize=True)


def build_caption_markdown(spec: dict[str, Any]) -> str:
    post = spec.get("post", {})
    if post.get("caption"):
        return str(post["caption"]).strip() + "\n"
    if post.get("caption_lines"):
        return "\n".join(str(line) for line in post["caption_lines"]).strip() + "\n"

    lines: list[str] = []
    title = post.get("title") or spec.get("title") or "Черновик поста"
    if title:
        lines.append(f"**{title}**")
        lines.append("")
    for paragraph in post.get("paragraphs", []):
        lines.append(str(paragraph))
        lines.append("")
    if post.get("task"):
        lines.append("Задача:")
        lines.append(str(post["task"]))
        lines.append("")
    if post.get("prompt"):
        lines.append(str(post["prompt"]))
        lines.append("")
    if post.get("cta"):
        lines.append(str(post["cta"]))
        lines.append("")
    if post.get("hashtags"):
        lines.append(" ".join(post["hashtags"]))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_post_markdown(spec: dict[str, Any], card_paths: list[Path]) -> str:
    lines = build_caption_markdown(spec).rstrip().splitlines()
    lines.append("")
    lines.append("Картинки:")
    for path in card_paths:
        lines.append(f"- {path.name}")
    return "\n".join(lines).rstrip() + "\n"


def plain_text_length(markdown: str) -> int:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", markdown)
    return len(text.strip())


def rich_text_plain(value: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"\1", value).strip()


def text_list_length(values: list[Any]) -> int:
    return sum(len(rich_text_plain(str(value))) for value in values)


def build_editor_comments(spec: dict[str, Any], caption_md: str, warnings: list[str]) -> list[str]:
    comments: list[str] = []
    post = spec.get("post", {})
    cards = spec.get("cards", [])
    caption_len = plain_text_length(caption_md)

    if warnings:
        comments.append("Есть render warnings: сначала проверь карточки и формулы.")
    if caption_len > 900:
        comments.append("Комментарий к посту длинный: в этом формате лучше 300-700 символов, математику оставляем карточкам.")
    elif caption_len < 120:
        comments.append("Комментарий очень короткий: можно добавить одну живую фразу о теме или просьбу написать темы для следующих карточек.")

    title = str(post.get("title") or spec.get("title") or "")
    if len(title) > 76:
        comments.append("Заголовок длинный: для Telegram лучше ужать до одной читаемой строки.")
    if title.lower().startswith(("задача про", "разбор задачи", "черновик")):
        comments.append("Заголовок слишком служебный: лучше назвать приём или ловушку, а не просто `задача/разбор`.")
    caption_lower = caption_md.lower()
    if "#советы_олимпиадникам" not in caption_lower and "#олимпиаднаяматематика" not in caption_lower:
        comments.append("В комментарии нет серийного хэштега; для рубрики лучше держать один узнаваемый тег.")
    if "на что обращать внимание" in caption_lower and "что делать" not in caption_lower:
        comments.append("Есть `На что обращать внимание?`, но нет пары `Что делать?`; в этом формате они хорошо работают вместе.")
    if any(phrase in caption_lower for phrase in ("не утонуть", "короткие идеи", "главный ход", "магия", "скрывается")):
        comments.append("Caption звучит как нейро-хук; лучше проще и конкретнее по материалу.")
    stock_phrases = [
        "продолжаем с вами закреплять",
        "сохраняйте себе ключевые идеи",
        "всё как обычно",
        "просто подсказки без самостоятельного решения",
        "удобный файлик",
        "вам с радостью помогут",
    ]
    stock_count = sum(1 for phrase in stock_phrases if phrase in caption_lower)
    if stock_count >= 3:
        comments.append("Caption слишком похож на шаблонную копипасту; оставь рубричность, но перепиши человечески под конкретный материал.")
    cta = str(post.get("cta", "")).lower()
    if any(word in cta for word in ("покуп", "запис", "скидк")):
        comments.append("CTA выглядит продажно; для этой рубрики лучше реакции, комментарии и запросы тем.")
    if len(post.get("hashtags", [])) > 4:
        comments.append("Хэштегов больше четырёх: для канала лучше оставить 2-3 самых нужных.")

    if len(cards) < 2:
        comments.append("Карточек меньше двух: проверь, хватает ли отдельного хинта перед решением.")
    if len(cards) > 5:
        comments.append("Карточек больше пяти: для Telegram-разбора это может быть тяжеловато, лучше собрать серию или сократить.")
    has_solution_card = any(card.get("type") == "solution" for card in cards if isinstance(card, dict))
    if has_solution_card and cards and cards[-1].get("type") != "solution":
        comments.append("Solution-карточка есть, но не последняя: финальный разбор лучше ставить в конец.")

    for index, card in enumerate(cards, start=1):
        title = str(card.get("title") or "")
        if len(title) > 42:
            comments.append(f"card-{index:02d}: заголовок длинноват, может просесть визуальный ритм.")
        paragraphs = card.get("paragraphs", [])
        if text_list_length(paragraphs) > 360:
            comments.append(f"card-{index:02d}: слишком много текста в paragraphs; лучше оставить одну мысль и часть перенести в review/caption.")
        formulas = card.get("formulas", [])
        if len(formulas) > 3:
            comments.append(f"card-{index:02d}: много формул; проверь читаемость на телефоне.")
        if any("$$" in str(formula) for formula in formulas):
            comments.append(f"card-{index:02d}: формулы должны быть без `$$`, renderer сам делает display math.")
        if card.get("type", "hint") == "hint" and not card.get("callouts"):
            comments.append(f"card-{index:02d}: для hint-карточки полезны callouts `Маркер` и `Что делать?`.")
        if card.get("type", "hint") == "hint":
            labels = [str(item.get("label", "")).strip() for item in card.get("callouts", []) if isinstance(item, dict)]
            first_label_ok = labels[:1] in (["Маркер"], ["На что смотреть?"], ["На что обращать внимание?"])
            second_label_ok = len(labels) < 2 or labels[1] == "Что делать?"
            if labels and not (first_label_ok and second_label_ok):
                comments.append(f"card-{index:02d}: callouts лучше держать в формате `На что обращать внимание?` / `Что делать?`.")
        if card.get("type") == "solution":
            steps = card.get("steps", [])
            if len(steps) < 2:
                comments.append(f"card-{index:02d}: solution слишком короткое; нужен хотя бы ключевой ход и финальный вывод.")
            if len(steps) > 5:
                comments.append(f"card-{index:02d}: решение длинное, возможно стоит разбить на две карточки.")
            if str(card.get("answer", "")).strip().lower() in {"", "дописать", "todo", "?"}:
                comments.append(f"card-{index:02d}: ответ не готов; это нельзя публиковать без ручной правки.")

    if not comments:
        comments.append("Автопроверка не нашла явных проблем; всё равно перечитай математику и тон перед отправкой.")
    return comments


def build_review_markdown(
    spec: dict[str, Any],
    card_paths: list[Path],
    caption_md: str,
    warnings: list[str],
) -> str:
    slug = spec.get("slug", "draft")
    title = spec.get("post", {}).get("title") or spec.get("title") or "Черновик поста"
    comments = build_editor_comments(spec, caption_md, warnings)
    lines = [
        f"# Review draft: {slug}",
        "",
        f"Пост: {title}",
        "",
        "## Текст для правки",
        "",
        "Редактируй `caption.md`; publish-скрипт возьмёт именно его.",
        "",
        "```markdown",
        caption_md.rstrip(),
        "```",
        "",
        "## Карточки",
        "",
    ]
    for path in card_paths:
        lines.append(f"- `cards/{path.name}`")
    lines.extend(["", "## Редакторские комментарии", ""])
    for comment in comments:
        lines.append(f"- {comment}")
    lines.extend(["", "## Перед отправкой", ""])
    checklist = [
        "условие совпадает с задачей;",
        "решение математически корректно;",
        "нет лишней воды в подписи;",
        "формулы читаются на телефоне;",
        "последняя карточка даёт понятный ответ;",
        "после ручной правки запущен dry-run publish без `--live`.",
    ]
    for item in checklist:
        lines.append(f"- [ ] {item}")
    return "\n".join(lines).rstrip() + "\n"


def validate_spec(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not spec.get("slug"):
        errors.append("slug is required")
    cards = spec.get("cards")
    if not isinstance(cards, list) or not cards:
        errors.append("cards must be a non-empty list")
    else:
        for index, card in enumerate(cards, start=1):
            if not card.get("title"):
                errors.append(f"cards[{index}].title is required")
            if card.get("type", "hint") == "solution" and not card.get("steps"):
                errors.append(f"cards[{index}] is a solution card but has no steps")
    return errors


def render_post(spec_path: Path, out_root: Path) -> dict[str, Any]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    errors = validate_spec(spec)
    if errors:
        raise ValueError("Invalid post spec:\n- " + "\n- ".join(errors))

    slug = spec["slug"]
    out_dir = out_root / slug
    cards_dir = out_dir / "cards"
    cache_dir = out_dir / "_formula_cache"
    out_dir.mkdir(parents=True, exist_ok=True)
    formula_renderer = FormulaRenderer(cache_dir)
    warnings: list[str] = []
    if not formula_renderer.available:
        warnings.append("Formula renderer unavailable; install/use xelatex and pdftocairo for exact formulas")

    brand = spec.get("brand", {"name": "allmath", "handle": "@allmath"})
    card_paths: list[Path] = []
    for index, card in enumerate(spec["cards"], start=1):
        card_type = card.get("type", "hint")
        out_path = cards_dir / f"card-{index:02d}.png"
        if card_type == "solution":
            render_solution_card(card, brand, out_path, formula_renderer, warnings)
        else:
            render_hint_card(card, brand, out_path, formula_renderer, warnings)
        card_paths.append(out_path)

    caption_md = build_caption_markdown(spec)
    caption_path = out_dir / "caption.md"
    caption_path.write_text(caption_md, encoding="utf-8")

    post_md = build_post_markdown(spec, card_paths)
    post_path = out_dir / "post.md"
    post_path.write_text(post_md, encoding="utf-8")

    review_md = build_review_markdown(spec, card_paths, caption_md, warnings)
    review_path = out_dir / "review.md"
    review_path.write_text(review_md, encoding="utf-8")

    manifest = {
        "slug": slug,
        "source": str(spec_path),
        "caption": str(caption_path),
        "post": str(post_path),
        "review": str(review_path),
        "cards": [str(path) for path in card_paths],
        "warnings": warnings,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render allmath Telegram post cards from a JSON draft.")
    parser.add_argument("spec", type=Path, help="Path to post JSON spec")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output root directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = render_post(args.spec.resolve(), args.out.resolve())
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
