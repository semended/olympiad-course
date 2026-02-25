import { getServerSession } from "next-auth";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { authOptions } from "@/lib/auth";
import { getEnrollmentForCourse } from "@/lib/data/enrollments";
import { getCourseById } from "@/lib/data/lms";
import { getCourseProgressForUser } from "@/lib/data/progress";

type CoursePageProps = {
  params: {
    courseId: string;
  };
};

export default async function CourseDetailsPage({ params }: CoursePageProps) {
  const session = await getServerSession(authOptions);

  if (!session?.user?.id) {
    redirect("/auth/login");
  }

  const enrollment = await getEnrollmentForCourse(session.user.id, params.courseId);

  if (!enrollment || enrollment.expiresAt <= new Date()) {
    redirect("/courses?message=Access%20expired%20or%20not%20purchased");
  }

  const course = await getCourseById(params.courseId);

  if (!course) {
    notFound();
  }

  const progress = await getCourseProgressForUser(params.courseId, session.user.id);

  return (
    <AppShell>
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">{course.title}</h2>
        <p className="text-sm text-slate-600">{course.description}</p>

        <div className="grid gap-3 md:grid-cols-4">
          <article className="rounded-xl border bg-white p-4 shadow-sm">
            <p className="text-xs text-slate-500">Total tasks</p>
            <p className="mt-2 text-2xl font-semibold">{progress.totalTasks}</p>
          </article>
          <article className="rounded-xl border bg-white p-4 shadow-sm">
            <p className="text-xs text-slate-500">Completed tasks</p>
            <p className="mt-2 text-2xl font-semibold">{progress.completedTasks}</p>
          </article>
          <article className="rounded-xl border bg-white p-4 shadow-sm">
            <p className="text-xs text-slate-500">Average score</p>
            <p className="mt-2 text-2xl font-semibold">
              {progress.averageScore === null ? "—" : progress.averageScore}
            </p>
          </article>
          <article className="rounded-xl border bg-white p-4 shadow-sm">
            <p className="text-xs text-slate-500">Progress</p>
            <p className="mt-2 text-2xl font-semibold">{progress.percent}%</p>
          </article>
        </div>

        <div className="h-2 rounded-full bg-slate-100">
          <div className="h-2 rounded-full bg-slate-900" style={{ width: `${progress.percent}%` }} />
        </div>

        <div className="space-y-3">
          {course.modules.map((module) => (
            <Link
              key={module.id}
              href={`/dashboard/courses/${course.id}/modules/${module.id}`}
              className="block rounded-xl border bg-white p-4 shadow-sm"
            >
              <p className="font-semibold">{module.title}</p>
              <p className="text-sm text-slate-600">Материалов: {module.materials.length}</p>
            </Link>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
