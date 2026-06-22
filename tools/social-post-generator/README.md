# allmath Social Post Generator

Локальная надстройка для черновиков Telegram-постов: на входе JSON с задачей,
идеей решения, карточками и текстом поста; на выходе PNG-карточки,
редактируемый `caption.md`, полный `post.md` и `review.md` с комментариями для
ручной проверки.

## Что Берём Из `degeneration-videos`

- safe-area и фиксированные размеры кадра;
- разделение на смысловые beats, а не “просто красивую картинку”;
- обязательные формулы как отдельные математические объекты;
- acceptance mindset: если карточка переполнена или формула не собралась,
  генератор пишет warning в `manifest.json`.

Manim-видео-слой не переносим: для Telegram-картинок он тяжёлый. Здесь
используется Python + Pillow, а формулы рендерятся локальным `xelatex` и
`pdftocairo`.

## Нормальный UX

Основной сценарий не требует терминала: пользователь отправляет материал в
Telegram-бота, backend генерирует JSON-черновик, рендерит карточки и присылает
draft bundle в закрытый Telegram draft-чат/канал. CLI ниже остаётся для
локальной отладки и ручной регенерации.

Бот принимает свободный текст. Команда `/format` показывает не анкету для
заполнения, а стиль-канон выходного поста: какие бывают рубрики, как звучит
caption и как устроены карточки. Канон лежит в [`FORMAT.md`](FORMAT.md).

## Запуск

```bash
python3 tools/social-post-generator/render_social_post.py \
  tools/social-post-generator/example-post.json
```

Результат:

```text
tmp/social-posts/<slug>/
  cards/card-01.png
  cards/card-02.png
  cards/card-03.png
  caption.md
  post.md
  review.md
  manifest.json
```

## Draft-First Флоу

Публикация не автоматическая. Сначала генератор собирает черновик, потом человек
правит текст и только после этого вручную запускает отправку.

Что смотреть после рендера:

- `caption.md` — текст, который publish-скрипт возьмёт в Telegram; его и надо
  руками править перед отправкой;
- `review.md` — редакторские комментарии, чеклист и список карточек;
- `cards/*.png` — картинки для финального просмотра;
- `manifest.json` — технический файл, по нему запускается dry-run/publish.

Проверка без публикации:

```bash
python3 tools/social-post-generator/publish_telegram_post.py \
  tmp/social-posts/boxes-operation-count/manifest.json
```

Команда покажет, что ушло бы в Telegram, но ничего не отправит.

## Ручная Публикация В Telegram

Для настоящей отправки нужны переменные окружения в текущем терминале:

```bash
export TELEGRAM_BOT_TOKEN="123456:bot-token-from-botfather"
export TELEGRAM_CHANNEL_ID="@your_channel"
```

После ручной правки `caption.md` и dry-run:

```bash
python3 tools/social-post-generator/publish_telegram_post.py \
  tmp/social-posts/boxes-operation-count/manifest.json \
  --live
```

Бот должен быть админом канала с правом постинга. Скрипт не читает `.env`,
не печатает токен и не отправляет ничего без `--live`.

Технически публикация устроена так:

- если текст помещается в лимит подписи Telegram, он уходит подписью к альбому;
- если текст длиннее, сначала уходит текстовый пост, затем альбом карточек;
- одна карточка отправляется как `sendPhoto`, 2-10 карточек как `sendMediaGroup`;
- больше 10 карточек автоматически режутся на несколько альбомов.

## GitHub Actions

В репозитории есть workflow `.github/workflows/build-telegram-draft.yml`.
Он не публикует в Telegram и не использует secrets. Он только рендерит
draft bundle и загружает его как artifact.

Для ручной сборки:

1. Откройте action `Build Telegram draft`.
2. Укажите путь к JSON-черновику.
3. Скачайте artifact `telegram-draft-build`.
4. Проверьте `review.md`, поправьте `caption.md`, посмотрите карточки.

При пуше в `main` JSON из этой папки тоже только рендерятся в draft artifact:

```text
tools/social-post-generator/queue/<slug>.json
```

## Рабочий Процесс

1. Пользователь даёт задачу и решение/идею.
2. Codex проверяет математическую линию и пишет JSON-черновик:
   `post.title`, `post.paragraphs`, `cards[]`, `steps[]`, `formulas[]`.
3. Скрипт рендерит вертикальные мобильные карточки в стиле allmath с плотностью Школково:
   крупный заголовок, короткая идея, формулы, блоки `Маркер`/`Что делать?`,
   правый Telegram-бейдж и брендовые элементы на фоне.
4. Пользователь проверяет PNG, `review.md` и руками правит `caption.md`.
5. Сначала запускаем dry-run `publish_telegram_post.py` без `--live`.
6. Только после финального ручного ok запускаем `publish_telegram_post.py --live`.

## Минимальная Структура Карточки

```json
{
  "type": "hint",
  "theme": "cream",
  "rubric": "Олимпиадный приём",
  "kicker": "Трюк №1",
  "title": "Считай операции, а не форму",
  "paragraphs": ["Текст с **жирным акцентом**."],
  "formulas": ["7 + 10\\cdot 7 = 77"],
  "callouts": [
    {"label": "Маркер", "text": "Что нужно заметить."},
    {"label": "Что делать?", "text": "Как действовать дальше."}
  ]
}
```

Для решения используйте `type: "solution"` и `steps`.
