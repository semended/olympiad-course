# Olympiad Course — Next.js 14 LMS

Production-ready каркас LMS/SaaS на **Next.js 14 (App Router)** с реальной **Prisma + PostgreSQL** интеграцией.

## Stack
- Next.js 14 + TypeScript
- TailwindCSS
- Prisma ORM
- PostgreSQL
- NextAuth (Credentials)
- Stripe Checkout + Webhook
- AWS S3 upload for submissions

## Быстрый старт
1. Скопируйте `.env.example` в `.env` и заполните значения.
2. Установите зависимости:
   ```bash
   npm install
   ```
3. Сгенерируйте Prisma client:
   ```bash
   npm run prisma:generate
   ```
4. Выполните миграции (dev):
   ```bash
   npm run prisma:migrate
   ```
5. Заполните базу тестовыми данными:
   ```bash
   npm run prisma:seed
   ```
6. Запустите приложение:
   ```bash
   npm run dev
   ```

## Environment variables
- `DATABASE_URL` (**обязателен**)
- `NEXTAUTH_SECRET`
- `NEXTAUTH_URL`
- `NEXT_PUBLIC_APP_URL`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PUBLIC_KEY`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_S3_BUCKET`

## Основные Prisma-команды
```bash
npm run prisma:generate
npm run prisma:migrate
npm run prisma:seed
```

## Production Prisma
Для production используйте:
```bash
npx prisma migrate deploy
```

## Healthcheck
Доступен endpoint для проверки деплоя:
- `GET /api/health` → `{ "status": "ok" }`

## Stripe purchase flow
- Endpoint `POST /api/stripe/checkout`:
  - проверяет авторизацию
  - принимает `courseId`
  - создаёт Stripe Checkout Session
  - success URL: `${NEXT_PUBLIC_APP_URL}/courses?success=true`
  - cancel URL: `${NEXT_PUBLIC_APP_URL}/courses?canceled=true`
  - metadata: `userId`, `courseId`
- Endpoint `POST /api/stripe/webhook`:
  - проверяет подпись через `STRIPE_WEBHOOK_SECRET`
  - обрабатывает `checkout.session.completed`
  - создаёт/обновляет enrollment c `expiresAt = now + course.durationDays`
- На странице `/courses` кнопка `Purchase` запускает checkout и редиректит на Stripe.

## Deploy to Vercel
1. Подключите GitHub-репозиторий в Vercel.
2. Добавьте ENV переменные в проект Vercel:
   - `DATABASE_URL`
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `NEXT_PUBLIC_APP_URL`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `AWS_S3_BUCKET`
3. Настройте Stripe webhook URL:
   - `https://your-domain.vercel.app/api/stripe/webhook`
4. Убедитесь, что миграции в production выполняются командой:
   - `npx prisma migrate deploy`

## Course access gating
Серверная проверка access применяется на страницах:
- `/dashboard/courses/[courseId]`
- `/dashboard/courses/[courseId]/modules/[moduleId]`
- `/dashboard/material/[materialId]`

Условия доступа:
- у пользователя должен быть `Enrollment` для курса
- `expiresAt` должен быть больше текущего времени

При отсутствии доступа выполняется редирект на:
- `/courses?message=Access expired or not purchased`

## Submission flow + file upload
- Пользователь выбирает файл (`.pdf`, `.jpg`, `.png`) в `/dashboard/material/[materialId]`
- Файл загружается в S3 через `POST /api/upload`
- Ключ объекта: `submissions/{userId}/{timestamp}.pdf`
- Возвращается публичный `fileUrl`
- `POST /api/submissions` создаёт Submission с `fileUrl` и `extractedText = null`
- Админ на `/admin/submissions/[submissionId]` может открыть файл кнопкой `View file`
