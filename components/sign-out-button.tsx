"use client";

import { signOut } from "next-auth/react";

export function SignOutButton() {
  return (
    <button
      onClick={() => signOut({ callbackUrl: "/auth/login" })}
      className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700"
      type="button"
    >
      Выйти
    </button>
  );
}
