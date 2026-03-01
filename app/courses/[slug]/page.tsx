import { notFound } from "next/navigation";

import { CoursePageTemplate, type ProgramSection } from "@/components/CoursePageTemplate";

type CoursePageProps = {
  params: {
    slug: string;
  };
};

type CourseContent = {
  title: string;
  description: string;
  program: ProgramSection[];
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

const courses: Record<string, CourseContent> = {
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

export function generateStaticParams() {
  return Object.keys(courses).map((slug) => ({ slug }));
}

export default function CourseDetailsPage({ params }: CoursePageProps) {
  const course = courses[params.slug];

  if (!course) {
    notFound();
  }

  return <CoursePageTemplate title={course.title} description={course.description} program={course.program} />;
}
