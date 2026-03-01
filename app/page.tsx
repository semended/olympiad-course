import { CourseCard } from "@/components/course-card";
import { COURSES } from "@/data/courses";

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
        ))}
      </div>
    </section>
  );
}
