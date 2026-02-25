import Link from "next/link";

import { RegisterForm } from "@/components/register-form";

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md rounded-2xl border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Регистрация</h1>
        <p className="mt-2 text-sm text-slate-600">Создайте аккаунт с ролью USER по умолчанию.</p>
        <div className="mt-6">
          <RegisterForm />
        </div>
        <p className="mt-4 text-sm text-slate-600">
          Уже есть аккаунт? <Link href="/auth/login" className="font-medium text-slate-900">Войти</Link>
        </p>
      </div>
    </main>
  );
}
