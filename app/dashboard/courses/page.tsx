import Link from "next/link";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { authOptions } from "@/lib/auth";
import { getUserEnrollments } from "@/lib/data/enrollments";

export default async function DashboardCoursesPage() {
  const session = await getServerSession(authOptions);

  if (!session?.user?.id) {
    redirect("/auth/login");
  }

  const enrollments = await getUserEnrollments(session.user.id);
  const activeEnrollments = enrollments.filter((enrollment) => enrollment.expiresAt > new Date());

  return (
    <AppShell>
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">My Courses</h2>
        <p className="text-sm text-slate-600">Раздел ваших активных курсов.</p>
        <div className="space-y-3">
          {activeEnrollments.map((enrollment) => (
            <Link
              key={enrollment.id}
              href={`/dashboard/courses/${enrollment.course.id}`}
              className="block rounded-xl border bg-white p-4 shadow-sm"
            >
              <p className="font-semibold">{enrollment.course.title}</p>
              <p className="text-sm text-slate-600">{enrollment.course.description}</p>
            </Link>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
