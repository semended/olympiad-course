import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-8">
      <div className="w-full max-w-2xl rounded-2xl border bg-card p-8 shadow-sm">
        <h1 className="text-3xl font-semibold">Olympiad Course Platform</h1>
        <p className="mt-4 text-sm text-slate-600">
          Базовый SaaS-каркас на Next.js 14 + Prisma + NextAuth с ролями USER / ADMIN.
        </p>
        <div className="mt-6 flex gap-3">
          <Link
            href="/auth/login"
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
          >
            Войти
          </Link>
          <Link
            href="/auth/register"
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium"
          >
            Регистрация
          </Link>
        </div>
      </div>
    </main>
  );
}
