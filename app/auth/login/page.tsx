import Link from "next/link";

import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md rounded-2xl border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Вход</h1>
        <p className="mt-2 text-sm text-slate-600">Авторизуйтесь, чтобы перейти в dashboard.</p>
        <div className="mt-6">
          <LoginForm />
        </div>
        <p className="mt-4 text-sm text-slate-600">
          Нет аккаунта? <Link href="/auth/register" className="font-medium text-slate-900">Зарегистрироваться</Link>
        </p>
      </div>
    </main>
  );
}
