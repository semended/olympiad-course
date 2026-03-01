import { CourseCard } from "@/components/course-card";
import { COURSES } from "@/data/courses";

const homeCourses = [
  {
    title: "Олмат 5–6",
    description: "Вводный курс по олимпиадной математике для 5–6 классов: базовые идеи, логика и первые нестандартные задачи."
  },
  {
    title: "Олмат 6–7",
    description: "Продолжение подготовки: комбинаторные рассуждения, делимость, геометрические конструкции и стратегии решения."
  },
  {
    title: "Олмат 7–8",
    description: "Углублённый трек с олимпиадными техниками, разбором сложных задач и регулярной практикой на время."
  }
];

export default function HomePage() {
  return (
    <section>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Pandamath</h1>
        <p className="mt-3 max-w-2xl text-slate-600">
          Годовой курс олимпиады: выбирайте программу и занимайтесь в удобном темпе.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {COURSES.map((course) => (
          <CourseCard
            key={course.slug}
            title={course.title}
            description={course.shortDescription}
            href={`/courses/${course.slug}`}
          />
        {homeCourses.map((course) => (
          <CourseCard key={course.title} title={course.title} description={course.description} />
        ))}
      </div>
    </section>
  );
}
