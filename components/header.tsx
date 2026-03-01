import Link from "next/link";

export function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">
      <div>
        <p className="text-xs uppercase text-slate-500">Olympiad Course</p>
        <h1 className="text-lg font-semibold">Публичная платформа курсов</h1>
      </div>
      <div className="flex items-center gap-4 text-sm">
        {/* Временно отключено: отображение ролей пользователей */}
        <Link href="/" className="text-slate-600 hover:text-slate-900">
          Главная
        </Link>
        <Link href="/courses" className="text-slate-600 hover:text-slate-900">
          Каталог
        </Link>
      </div>
    </header>
  );
}
