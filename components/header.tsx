import { getServerSession } from "next-auth";
import Link from "next/link";

import { SignOutButton } from "@/components/sign-out-button";
import { authOptions } from "@/lib/auth";

export async function Header() {
  const session = await getServerSession(authOptions);

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <div>
        <p className="text-xs uppercase text-slate-500">Welcome back</p>
        <h1 className="text-lg font-semibold">{session?.user?.name ?? "User"}</h1>
      </div>
      <div className="flex items-center gap-3">
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
          {session?.user?.role ?? "USER"}
        </span>
        <Link href="/auth/login" className="text-sm text-slate-600 hover:text-slate-900">
          Account
        </Link>
        <SignOutButton />
      </div>
    </header>
  );
}
