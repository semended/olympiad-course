import Link from "next/link";
import { CircleUserRound } from "lucide-react";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl" aria-hidden>
            🐼
          </span>
          <span className="text-xl font-semibold text-slate-900">Pandamath</span>
        </Link>

        <nav className="flex items-center gap-2 sm:gap-4">
          <Link
            href="/courses"
            className="rounded-full px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-slate-900"
          >
            Каталог курсов
          </Link>
          <Link
            href="/tasks"
            className="rounded-full px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 hover:text-slate-900"
          >
            Каталог задач
          </Link>
          <Link
            href="/profile"
            aria-label="Личный кабинет"
            className="rounded-full p-2 text-slate-700 transition hover:bg-slate-100 hover:text-slate-900"
          >
            <CircleUserRound className="h-6 w-6" />
          </Link>
        </nav>
      </div>
    </header>
  );
}
