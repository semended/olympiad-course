import { getServerSession } from "next-auth";
import Link from "next/link";
import { redirect } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { authOptions } from "@/lib/auth";
import { getUserEnrollments } from "@/lib/data/enrollments";
import { getCourseProgressForUser } from "@/lib/data/progress";

function getDaysLeft(expiresAt: Date) {
  const now = new Date();
  const diffMs = expiresAt.getTime() - now.getTime();
  if (diffMs <= 0) {
    return 0;
  }

  return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
}

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);

  if (!session?.user?.id) {
    redirect("/auth/login");
  }

  const enrollments = await getUserEnrollments(session.user.id);
  const activeEnrollments = enrollments.filter((enrollment) => enrollment.expiresAt > new Date());

  return (
    <AppShell>
      <section className="space-y-5">
        <div>
          <h2 className="text-2xl font-semibold">Dashboard</h2>
          <p className="text-sm text-slate-600">Ваши активные курсы и текущий прогресс.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {await Promise.all(
            activeEnrollments.map(async (enrollment) => {
              const progress = await getCourseProgressForUser(enrollment.courseId, session.user.id);
              const daysLeft = getDaysLeft(enrollment.expiresAt);

              return (
                <article key={enrollment.id} className="rounded-xl border bg-white p-4 shadow-sm">
                  <h3 className="text-base font-semibold">{enrollment.course.title}</h3>
                  <p className="mt-1 text-sm text-slate-600">{enrollment.course.description}</p>
                  <p className="mt-3 text-xs text-slate-500">Прогресс: {progress.percent}%</p>
                  <div className="mt-2 h-2 rounded-full bg-slate-100">
                    <div className="h-2 rounded-full bg-slate-900" style={{ width: `${progress.percent}%` }} />
                  </div>
                  <p className="mt-2 text-xs text-slate-500">
                    Средний балл: {progress.averageScore === null ? "—" : progress.averageScore}
                  </p>
                  <p className="mt-2 text-xs text-slate-500">
                    Проверено задач: {progress.completedTasks}/{progress.totalTasks}
                  </p>
                  <p className="mt-2 text-xs text-slate-500">
                    Expiration date: {enrollment.expiresAt.toLocaleDateString()}
                  </p>
                  <p className="mt-2 text-xs text-slate-500">Days left: {daysLeft}</p>
                  <Link
                    href={`/dashboard/courses/${enrollment.course.id}`}
                    className="mt-4 inline-flex rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium"
                  >
                    Открыть курс
                  </Link>
                </article>
              );
            })
          )}
        </div>
      </section>
    </AppShell>
  );
}
