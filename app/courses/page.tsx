import { CourseCard } from "@/components/course-card";
import { COURSES } from "@/data/courses";

const courses = [
  {
    title: "Олмат 5–6",
    description: "Основа олимпиадной математики для среднего звена: логика, арифметика и аккуратное оформление решений."
  },
  {
    title: "Олмат 6–7",
    description: "Системный курс с акцентом на методы: инварианты, разбиения, оценки и графические модели."
  },
  {
    title: "Олмат 7–8",
    description: "Продвинутый уровень подготовки к муниципальному и региональному этапам олимпиады."
  }
];

export default function CoursesPage() {
  return (
    <section>
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Каталог курсов</h1>
      <p className="mt-3 max-w-2xl text-slate-600">Три направления подготовки для разных возрастов.</p>

      <div className="mt-8 grid gap-6 md:grid-cols-3">
        {COURSES.map((course) => (
          <CourseCard
            key={course.slug}
            title={course.title}
            description={course.shortDescription}
            href={`/courses/${course.slug}`}
          />
        {courses.map((course) => (
          <CourseCard key={course.title} title={course.title} description={course.description} />
        ))}
      </div>
    </section>
  );
}
