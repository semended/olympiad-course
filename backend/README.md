# Railway backend

Минимальный приватный API для MVP подписки.

## Зачем он нужен

- Supabase хранит пользователей, подписки, наборы задач и отправленные решения.
- Статический фронт ходит в Supabase только публичным publishable key и работает через RLS.
- Railway держит операции, которым нужны секреты: ручная выдача доступа, будущие платежные webhook-и, Telegram-бот.

## Локальный запуск

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Railway variables

```text
DATABASE_URL=...
ADMIN_API_KEY=...
PUBLIC_SITE_ORIGINS=https://golodnyuk-math.netlify.app,http://127.0.0.1:4173
AI_CHECK_API_KEY=...
AI_CHECK_API_URL=https://api.openai.com/v1/chat/completions
AI_CHECK_MODEL=gpt-4o-mini
TELEGRAM_BOT_TOKEN=...
TELEGRAM_WEBHOOK_SECRET=random-long-secret
TELEGRAM_ALLOWED_USER_IDS=123456789
TELEGRAM_DRAFT_CHAT_ID=-1001234567890
TELEGRAM_SET_WEBHOOK_ON_STARTUP=true
TELEGRAM_PUBLIC_BASE_URL=https://your-railway-domain.up.railway.app
TELEGRAM_POST_AI_API_KEY=...
TELEGRAM_POST_AI_MODEL=gpt-4o-mini
```

`DATABASE_URL` лучше брать из Supabase connection pooler. `ADMIN_API_KEY` нужен только для ручной выдачи доступа и не должен попадать во фронт.
Если `AI_CHECK_API_KEY` пустой, `/api/ai/check-solution` работает в мок-режиме и возвращает JSON без внешнего вызова.

## Telegram post draft bot

Флоу без терминала:

1. Пользователь пишет материал для поста в личку Telegram-боту.
2. Backend через AI собирает JSON-черновик поста и карточек.
3. Renderer создаёт `caption.md`, `review.md` и PNG-карточки во временной папке.
4. Бот отправляет черновик в `TELEGRAM_DRAFT_CHAT_ID` или обратно в личку, если draft chat не задан.

Это именно review/draft-чат, а не публикация в основной канал. Бот не вызывает live publish в основной канал.
Команда `/format` в боте присылает стиль-канон выходного поста, не анкету для заполнения.

Переменные:

- `TELEGRAM_BOT_TOKEN` — токен от BotFather.
- `TELEGRAM_WEBHOOK_SECRET` — случайная строка в URL webhook-а.
- `TELEGRAM_ALLOWED_USER_IDS` — comma-separated список Telegram user id, которым можно генерить черновики.
- `TELEGRAM_DRAFT_CHAT_ID` — закрытый канал/чат для черновиков; бот должен быть там админом/участником.
- `TELEGRAM_SET_WEBHOOK_ON_STARTUP=true` — backend сам выставит webhook на старте.
- `TELEGRAM_PUBLIC_BASE_URL` — публичный URL Railway. Если не задан, используется `RAILWAY_PUBLIC_DOMAIN`.
- `TELEGRAM_POST_AI_API_KEY` — ключ для генерации постов; если не задан, используется `AI_CHECK_API_KEY`.
- `TELEGRAM_POST_AI_MODEL` — модель генерации постов; по умолчанию `AI_CHECK_MODEL`.

Если AI-ключа нет, бот всё равно вернёт грубый шаблон черновика без настоящей генерации.

## Ручная выдача доступа

```bash
curl -X POST "$RAILWAY_API_URL/api/subscriptions/grant" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $ADMIN_API_KEY" \
  -d '{"email":"student@example.com","duration_days":31,"source":"telegram"}'
```

## AI-проверка решения

```bash
curl -X POST "$RAILWAY_API_URL/api/ai/check-solution" \
  -H "Content-Type: application/json" \
  -d '{"exam":"ege","task_id":"demo","task":{"statement":"2+2?","official_answer":"4","official_solution":"2+2=4","criteria":"Проверь ответ и ход."},"student_solution":"2+2=4"}'
```
