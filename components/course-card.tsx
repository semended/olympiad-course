import Link from "next/link";

type CourseCardProps = {
  title: string;
  description: string;
  href: string;
};

export function CourseCard({ title, description, href }: CourseCardProps) {
type CourseCardProps = {
  title: string;
  description: string;
};

export function CourseCard({ title, description }: CourseCardProps) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-lg">
      <h3 className="text-xl font-semibold text-slate-900">{title}</h3>
      <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
      <Link
        href={href}
        className="mt-5 inline-flex rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-900 hover:text-slate-900"
      >
        Подробнее
      </Link>
      <button className="mt-5 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-900 hover:text-slate-900">
        Подробнее
      </button>
    </article>
  );
}
