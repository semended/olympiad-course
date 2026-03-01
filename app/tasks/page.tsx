import Link from "next/link";

const sections = ["Алгебра", "Комбинаторика", "Теория чисел", "Геометрия"];

export default function TasksPage() {
  return (
    <section>
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Каталог задач</h1>
      <p className="mt-3 text-slate-600">Выберите раздел и начните решать задачи.</p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        {sections.map((section) => (
          <Link
            key={section}
            href="#"
            className="flex min-h-28 items-center justify-center rounded-2xl border border-slate-200 bg-white px-6 py-8 text-center text-xl font-semibold text-slate-800 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            {section}
          </Link>
        ))}
      </div>
    </section>
  );
}
