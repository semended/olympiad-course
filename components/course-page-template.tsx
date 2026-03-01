import { BookOpenCheck, ClipboardCheck, Infinity, NotebookPen, Trophy } from "lucide-react";

import { CourseAccordion } from "@/components/course-accordion";
import type { CourseInfo } from "@/data/courses";
import { PROGRAM_SECTIONS } from "@/data/courses";

const studyFlowLeft = [
  "2 листка в неделю",
  "Разбор ключевых задач",
  "Листок для самостоятельного решения",
  "Пробная олимпиада раз в месяц"
];

const studyFlowRight = [
  "Нет проблем со школьной математикой",
  "Есть опыт занятий в кружках",
  "Призёр или победитель этапа",
  "Хочешь стать победителем олимпиад"
];

const advantages = [
  {
    icon: Infinity,
    title: "Огромное количество материала",
    description: "Теория, подборки задач и дополнительные материалы для закрепления каждой темы."
  },
  {
    icon: ClipboardCheck,
    title: "Пробные олимпиады с проверкой",
    description: "Регулярные пробники в формате реальной олимпиады с обратной связью по решениям."
  },
  {
    icon: NotebookPen,
    title: "Регулярная практика",
    description: "Еженедельный ритм занятий и домашних листков для устойчивого роста результатов."
  }
];

export function CoursePageTemplate({ course }: { course: CourseInfo }) {
  return (
    <div className="space-y-10 pb-4">
      <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">{course.title}</h1>
        <p className="mt-4 max-w-3xl text-slate-600">{course.heroDescription}</p>
        <button className="mt-6 inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-700">
          <Trophy className="h-4 w-4" />
          Записаться
        </button>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Как проходит обучение</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="mb-3 flex items-center gap-2 text-lg font-semibold text-slate-900">
              <BookOpenCheck className="h-5 w-5" /> Формат занятий
            </h3>
            <ul className="space-y-2 text-sm text-slate-600">
              {studyFlowLeft.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </article>

          <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="mb-3 flex items-center gap-2 text-lg font-semibold text-slate-900">
              <Trophy className="h-5 w-5" /> Кому подойдёт
            </h3>
            <ul className="space-y-2 text-sm text-slate-600">
              {studyFlowRight.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </article>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Преимущества программы</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {advantages.map((advantage) => (
            <article key={advantage.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <advantage.icon className="h-6 w-6 text-slate-700" />
              <h3 className="mt-3 text-lg font-semibold text-slate-900">{advantage.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{advantage.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Программа курса</h2>
        <p className="mt-2 text-sm text-slate-600">Нажмите на раздел, чтобы раскрыть темы.</p>
        <div className="mt-5">
          <CourseAccordion sections={PROGRAM_SECTIONS} />
        </div>
      </section>
    </div>
  );
}
