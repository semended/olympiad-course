"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export function RegisterForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");

    const response = await fetch("/api/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name, email, password })
    });

    setLoading(false);

    if (!response.ok) {
      const payload = (await response.json()) as { error?: string };
      setError(payload.error ?? "Не удалось создать пользователя.");
      return;
    }

    router.push("/auth/login");
  };

  return (
    <form className="space-y-4" onSubmit={onSubmit}>
      <input
        type="text"
        required
        placeholder="Имя"
        value={name}
        onChange={(event) => setName(event.target.value)}
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
      />
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
        minLength={6}
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
        {loading ? "Создаем..." : "Создать аккаунт"}
      </button>
    </form>
  );
}
