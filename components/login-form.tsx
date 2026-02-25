"use client";

import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    const response = await signIn("credentials", {
      email,
      password,
      redirect: false,
      callbackUrl: "/dashboard"
    });

    setLoading(false);

    if (response?.error) {
      setError("Неверный email или пароль.");
      return;
    }

    router.push("/dashboard");
    router.refresh();
  };

  return (
    <form className="space-y-4" onSubmit={onSubmit}>
      <input
        type="email"
        required
        placeholder="Email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
      />
      <input
        type="password"
        required
        placeholder="Пароль"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
      />
      {error ? <p className="text-sm text-red-500">{error}</p> : null}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white"
      >
        {loading ? "Входим..." : "Войти"}
      </button>
    </form>
  );
}
