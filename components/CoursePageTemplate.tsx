"use client";

import { Award, BookOpenCheck, ChevronDown, ClipboardCheck, Layers, Target } from "lucide-react";
import { useMemo, useState } from "react";

export type ProgramSection = {
  title: string;
  topics: string[];
};

type CourseContent = {
  title: string;
  description: string;
  program: ProgramSection[];
};

type CoursePageTemplateProps = {
  slug: string;
};

const sharedProgram: ProgramSection[] = [
  {
    title: "Геометрия треугольника",
    topics: ["Медианы, биссектрисы и высоты", "Классические конфигурации", "Тренировочные задачи"]
  },
  {
    title: "Геометрия окружности",
    topics: ["Углы и дуги", "Сила точки", "Касательные и секущие"]
  },
  {
    title: "Алгебра",
    topics: ["Преобразования выражений", "Многочлены", "Уравнения и системы"]
  },
  {
    title: "Последовательности",
    topics: ["Рекуррентные формулы", "Прогрессии", "Оценка роста и паттерны"]
  },
  {
    title: "Неравенства",
    topics: ["Оценки", "Базовые классические неравенства", "Приёмы доказательства"]
  },
  {
    title: "Графы",
    topics: ["Деревья", "Эйлеровы пути", "Инварианты и раскраски"]
  },
  {
    title: "Теория чисел",
    topics: ["Делимость", "Сравнения по модулю", "Диофантовы уравнения"]
  },
  {
    title: "Теория вероятностей",
    topics: ["Классическая вероятность", "Комбинаторные модели", "Независимые события"]
  },
  {
    title: "Комбинаторика",
    topics: ["Подсчёты и конструкции", "Принцип Дирихле", "Биномиальные коэффициенты"]
  }
];

const coursesBySlug: Record<string, CourseContent> = {
  "olmat-5-6": {
    title: "Олмат 5–6",
    description:
      "Мягкий старт в олимпиадную математику: развиваем логическое мышление, учимся оформлять решения и нарабатываем уверенность на задачах.",
    program: sharedProgram
  },
  "olmat-6-7": {
    title: "Олмат 6–7",
    description:
      "Системный курс с акцентом на методики решения: регулярная практика, разборы и пробные олимпиады для стабильного прогресса.",
    program: sharedProgram
  },
  "olmat-7-8": {
    title: "Олмат 7–8",
    description:
      "Продвинутый уровень подготовки к серьёзным этапам олимпиад: сложные темы, стратегии и интенсивная самостоятельная работа.",
    program: sharedProgram
  }
};

const trainingLeft = ["2 листка в неделю", "Разбор ключевых задач", "Самостоятельный листок", "Пробная олимпиада"];

const trainingRight = [
  "Нет проблем со школьной математикой",
  "Есть опыт кружков",
  "Призёр этапа",
  "Хочешь стать победителем"
];

const advantages = [
  { icon: Layers, title: "Большой объём материала" },
  { icon: ClipboardCheck, title: "Проверяемые олимпиады" },
  { icon: Target, title: "Системная практика" }
];


export default function CoursePageTemplate({ slug }: CoursePageTemplateProps) {
  const [openedIndex, setOpenedIndex] = useState<number | null>(0);

  const course = useMemo(() => coursesBySlug[slug], [slug]);

  if (!course) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-slate-700 shadow-sm">
        Курс не найден.
      </div>
    );
  }

  return (
    <div className="space-y-10 pb-8">
      <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">{course.title}</h1>
        <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">{course.description}</p>
        <button
          type="button"
          className="mt-6 inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
        >
          <Award className="h-4 w-4" />
          Записаться
        </button>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Как проходит обучение</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="mb-3 flex items-center gap-2 text-lg font-semibold text-slate-900">
              <BookOpenCheck className="h-5 w-5" /> Формат курса
            </h3>
            <ul className="space-y-2 text-sm text-slate-600">
              {trainingLeft.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </article>

          <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="mb-3 flex items-center gap-2 text-lg font-semibold text-slate-900">
              <Award className="h-5 w-5" /> Для кого
            </h3>
            <ul className="space-y-2 text-sm text-slate-600">
              {trainingRight.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </article>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Преимущества</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {advantages.map((advantage) => (
            <article key={advantage.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <advantage.icon className="h-6 w-6 text-slate-700" />
              <h3 className="mt-3 text-lg font-semibold text-slate-900">{advantage.title}</h3>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Программа курса</h2>
        <p className="mt-2 text-sm text-slate-600">Нажмите на раздел, чтобы раскрыть список тем.</p>

        <div className="mt-5 space-y-3">
          {course.program.map((section, index) => {
            const isOpen = openedIndex === index;

            return (
              <article
                key={section.title}
                className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
              >
                <button
                  type="button"
                  onClick={() => setOpenedIndex(isOpen ? null : index)}
                  className="flex w-full items-center justify-between px-5 py-4 text-left"
                >
                  <span className="font-semibold text-slate-900">{section.title}</span>
                  <ChevronDown
                    className={`h-5 w-5 text-slate-500 transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`}
                  />
                </button>

                <div
                  className={`grid transition-all duration-300 ease-in-out ${isOpen ? "grid-rows-[1fr]" : "grid-rows-[0fr]"}`}
                >
                  <div className="overflow-hidden">
                    <ul className="list-disc space-y-2 px-10 pb-5 text-sm text-slate-600">
                      {section.topics.map((topic) => (
                        <li key={topic}>{topic}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
}
