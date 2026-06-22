from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from typing import Annotated

import asyncpg
import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

from app.telegram_posts import (
  TelegramPostBotSettings,
  bool_env,
  handle_telegram_post_update,
  maybe_set_telegram_webhook,
  normalize_public_base_url,
  require_telegram_config,
  split_csv_ints,
)


def _split_csv(value: str | None) -> list[str]:
  return [item.strip() for item in (value or "").split(",") if item.strip()]


class Settings(BaseModel):
  database_url: str | None = None
  admin_api_key: str | None = None
  ai_check_api_key: str | None = None
  ai_check_api_url: str = "https://api.openai.com/v1/chat/completions"
  ai_check_model: str = "gpt-4o-mini"
  cors_origins: list[str] = Field(default_factory=list)
  db_pool_max_size: int = 5
  telegram_post_bot: TelegramPostBotSettings


def load_settings() -> Settings:
  return Settings(
    database_url=os.getenv("DATABASE_URL"),
    admin_api_key=os.getenv("ADMIN_API_KEY"),
    ai_check_api_key=os.getenv("AI_CHECK_API_KEY"),
    ai_check_api_url=os.getenv("AI_CHECK_API_URL", "https://api.openai.com/v1/chat/completions"),
    ai_check_model=os.getenv("AI_CHECK_MODEL", "gpt-4o-mini"),
    cors_origins=_split_csv(os.getenv("PUBLIC_SITE_ORIGINS")) or [
      "http://127.0.0.1:4173",
      "http://localhost:4173",
      "https://golodnyuk-math.netlify.app",
    ],
    db_pool_max_size=int(os.getenv("DB_POOL_MAX_SIZE", "5")),
    telegram_post_bot=TelegramPostBotSettings(
      bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
      webhook_secret=os.getenv("TELEGRAM_WEBHOOK_SECRET"),
      draft_chat_id=os.getenv("TELEGRAM_DRAFT_CHAT_ID"),
      allowed_user_ids=split_csv_ints(os.getenv("TELEGRAM_ALLOWED_USER_IDS")),
      ai_api_key=os.getenv("TELEGRAM_POST_AI_API_KEY") or os.getenv("AI_CHECK_API_KEY"),
      ai_api_url=os.getenv("TELEGRAM_POST_AI_API_URL", os.getenv("AI_CHECK_API_URL", "https://api.openai.com/v1/chat/completions")),
      ai_model=os.getenv("TELEGRAM_POST_AI_MODEL", os.getenv("AI_CHECK_MODEL", "gpt-4o-mini")),
      public_base_url=normalize_public_base_url(os.getenv("TELEGRAM_PUBLIC_BASE_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN")),
      set_webhook_on_startup=bool_env(os.getenv("TELEGRAM_SET_WEBHOOK_ON_STARTUP")),
    ),
  )


settings = load_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
  app.state.db_pool = None

  if settings.database_url:
    app.state.db_pool = await asyncpg.create_pool(
      settings.database_url,
      min_size=1,
      max_size=settings.db_pool_max_size,
      command_timeout=15,
    )

  await maybe_set_telegram_webhook(settings.telegram_post_bot)

  try:
    yield
  finally:
    if app.state.db_pool:
      await app.state.db_pool.close()


app = FastAPI(
  title="Golodnyuk Math backend",
  version="0.1.0",
  lifespan=lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.cors_origins,
  allow_credentials=True,
  allow_methods=["GET", "POST", "OPTIONS"],
  allow_headers=["*"],
)


async def get_pool(request: Request) -> asyncpg.Pool:
  pool = getattr(request.app.state, "db_pool", None)

  if not pool:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail="Database is not configured",
    )

  return pool


def require_admin_key(
  x_admin_key: Annotated[str | None, Header(alias="X-Admin-Key")] = None,
) -> None:
  if not settings.admin_api_key:
    raise HTTPException(
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      detail="Admin API key is not configured",
    )

  if x_admin_key != settings.admin_api_key:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid admin API key",
    )


class GrantSubscriptionRequest(BaseModel):
  email: EmailStr
  plan: str = Field(default="pro_monthly", min_length=2, max_length=64)
  duration_days: int = Field(default=31, ge=1, le=370)
  trial_days: int = Field(default=0, ge=0, le=60)
  source: str = Field(default="manual", min_length=2, max_length=64)
  note: str | None = Field(default=None, max_length=500)


class GrantSubscriptionResponse(BaseModel):
  id: str
  email: str
  plan: str
  status: str
  source: str
  paid_until: str | None
  trial_ends_at: str | None
  updated_at: str


class CheckSolutionTask(BaseModel):
  statement: str = Field(min_length=1, max_length=12000)
  official_answer: str | None = Field(default=None, max_length=4000)
  official_solution: str | None = Field(default=None, max_length=16000)
  criteria: str | None = Field(default=None, max_length=4000)


class CheckSolutionRequest(BaseModel):
  exam: str = Field(min_length=1, max_length=32)
  task_id: str = Field(min_length=1, max_length=160)
  task: CheckSolutionTask
  student_solution: str = Field(min_length=1, max_length=20000)


class CheckSolutionResponse(BaseModel):
  score: float = Field(ge=0)
  max_score: float = Field(gt=0)
  verdict: str
  mistakes: list[str] = Field(default_factory=list)
  missing_steps: list[str] = Field(default_factory=list)
  feedback: str
  next_steps: list[str] = Field(default_factory=list)
  provider: str = "mock"


def _mock_solution_check(payload: CheckSolutionRequest) -> CheckSolutionResponse:
  official_answer = (payload.task.official_answer or "").strip()
  student_solution = payload.student_solution.strip()
  answer_seen = bool(official_answer and official_answer.lower() in student_solution.lower())

  if not student_solution:
    return CheckSolutionResponse(
      score=0,
      max_score=3,
      verdict="нет решения",
      mistakes=["Решение не отправлено."],
      missing_steps=["Нужно написать хотя бы идею и финальный ответ."],
      feedback="Пустой текст нельзя проверить даже в мок-режиме.",
      next_steps=["Запиши ход решения и отправь ещё раз."],
      provider="mock",
    )

  if answer_seen:
    return CheckSolutionResponse(
      score=2,
      max_score=3,
      verdict="похоже на верное, нужна проверка обоснования",
      mistakes=[],
      missing_steps=["Мок-режим не проверяет строгость каждого перехода."],
      feedback="Официальный ответ найден в решении. После подключения AI provider endpoint проверит логику и полноту.",
      next_steps=["Сверь рассуждение с официальным решением и допиши пропущенные переходы."],
      provider="mock",
    )

  return CheckSolutionResponse(
    score=1,
    max_score=3,
    verdict="нужно доработать",
    mistakes=["Официальный ответ не найден в тексте решения."],
    missing_steps=["Нужны финальный вывод и проверка вычислений."],
    feedback="Это мок-проверка: она не видит совпадения с официальным ответом и просит перепроверить ход.",
    next_steps=["Сравни финальный ответ с официальным и допиши ключевые шаги."],
    provider="mock",
  )


def _extract_json_object(value: str) -> dict:
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


async def _call_ai_checker(payload: CheckSolutionRequest) -> CheckSolutionResponse:
  system_prompt = (
    "Ты проверяешь математическое решение ученика. "
    "Верни только JSON с полями score, max_score, verdict, mistakes, "
    "missing_steps, feedback, next_steps. Пиши по-русски, коротко и аккуратно."
  )
  user_prompt = {
    "exam": payload.exam,
    "task_id": payload.task_id,
    "statement": payload.task.statement,
    "official_answer": payload.task.official_answer,
    "official_solution": payload.task.official_solution,
    "criteria": payload.task.criteria,
    "student_solution": payload.student_solution,
  }

  request_body = {
    "model": settings.ai_check_model,
    "temperature": 0.2,
    "response_format": {"type": "json_object"},
    "messages": [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
    ],
  }

  headers = {
    "Authorization": f"Bearer {settings.ai_check_api_key}",
    "Content-Type": "application/json",
  }

  async with httpx.AsyncClient(timeout=45) as client:
    response = await client.post(
      settings.ai_check_api_url,
      headers=headers,
      json=request_body,
    )

  if response.status_code >= 400:
    raise HTTPException(
      status_code=status.HTTP_502_BAD_GATEWAY,
      detail="AI provider returned an error",
    )

  data = response.json()
  content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
  parsed = _extract_json_object(content)
  parsed["provider"] = "ai"
  return CheckSolutionResponse(**parsed)


@app.get("/")
async def root() -> dict[str, str]:
  return {"service": "golodnyuk-math-backend"}


@app.get("/health")
async def health(request: Request) -> JSONResponse:
  if not settings.database_url:
    return JSONResponse({"ok": True, "database": "not_configured"})

  pool = getattr(request.app.state, "db_pool", None)

  if not pool:
    return JSONResponse(
      {"ok": False, "database": "pool_not_ready"},
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )

  try:
    async with pool.acquire() as connection:
      await connection.fetchval("select 1")
  except Exception:
    return JSONResponse(
      {"ok": False, "database": "error"},
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )

  return JSONResponse({"ok": True, "database": "ok"})


@app.post(
  "/api/subscriptions/grant",
  response_model=GrantSubscriptionResponse,
  dependencies=[Depends(require_admin_key)],
)
async def grant_subscription(
  payload: GrantSubscriptionRequest,
  pool: Annotated[asyncpg.Pool, Depends(get_pool)],
) -> dict[str, str | None]:
  row = await pool.fetchrow(
    """
    insert into public.subscription_access (
      email,
      plan,
      status,
      source,
      note,
      paid_until,
      trial_ends_at
    )
    values (
      lower($1::text),
      $2,
      'active',
      $3,
      $4,
      now() + ($5::int * interval '1 day'),
      case
        when $6::int > 0 then now() + ($6::int * interval '1 day')
        else null
      end
    )
    on conflict (email) do update set
      plan = excluded.plan,
      status = 'active',
      source = excluded.source,
      note = coalesce(excluded.note, public.subscription_access.note),
      paid_until = greatest(
        coalesce(public.subscription_access.paid_until, '-infinity'::timestamptz),
        excluded.paid_until
      ),
      trial_ends_at = coalesce(
        excluded.trial_ends_at,
        public.subscription_access.trial_ends_at
      ),
      updated_at = now()
    returning
      id::text,
      email::text,
      plan,
      status,
      source,
      paid_until::text,
      trial_ends_at::text,
      updated_at::text
    """,
    str(payload.email).lower(),
    payload.plan,
    payload.source,
    payload.note,
    payload.duration_days,
    payload.trial_days,
  )

  return dict(row)


@app.post("/api/ai/check-solution", response_model=CheckSolutionResponse)
async def check_solution(payload: CheckSolutionRequest) -> CheckSolutionResponse:
  if not settings.ai_check_api_key:
    return _mock_solution_check(payload)

  return await _call_ai_checker(payload)


@app.post("/api/telegram/post-drafts/{webhook_secret}")
async def telegram_post_drafts_webhook(webhook_secret: str, payload: dict[str, object]) -> dict[str, object]:
  require_telegram_config(settings.telegram_post_bot)

  if webhook_secret != settings.telegram_post_bot.webhook_secret:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Not found",
    )

  return await handle_telegram_post_update(payload, settings.telegram_post_bot)
