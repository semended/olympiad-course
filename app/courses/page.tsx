import { CourseCard } from "@/components/course-card";
import { COURSES } from "@/data/courses";

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
        ))}
      </div>
    </section>
  );
}
