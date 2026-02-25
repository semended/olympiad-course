import { getServerSession } from "next-auth";
import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { PurchaseButton } from "@/components/courses/purchase-button";
import { authOptions } from "@/lib/auth";
import { getUserEnrollments } from "@/lib/data/enrollments";
import { getAllCourses } from "@/lib/data/lms";

type CoursesPageProps = {
  searchParams?: {
    message?: string;
    success?: string;
    canceled?: string;
  };
};

export default async function CoursesPage({ searchParams }: CoursesPageProps) {
  const session = await getServerSession(authOptions);
  const courses = await getAllCourses();
  const enrollments = session?.user?.id ? await getUserEnrollments(session.user.id) : [];
  const enrollmentMap = new Map(enrollments.map((enrollment) => [enrollment.courseId, enrollment]));
  const now = new Date();

  return (
    <AppShell>
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Catalog</h2>
        <p className="text-sm text-slate-600">Каталог курсов LMS.</p>
        {searchParams?.message ? (
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-700">
            {searchParams.message}
          </div>
        ) : null}
        {searchParams?.success ? (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
            Payment successful. Enrollment will be activated after webhook processing.
          </div>
        ) : null}
        {searchParams?.canceled ? (
          <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">
            Payment canceled.
          </div>
        ) : null}

        <div className="space-y-3">
          {courses.map((course) => {
            const enrollment = enrollmentMap.get(course.id);
            const hasValidAccess = enrollment ? enrollment.expiresAt > now : false;

            return (
              <article key={course.id} className="rounded-xl border bg-white p-4 shadow-sm">
                <h3 className="font-semibold">{course.title}</h3>
                <p className="text-sm text-slate-600">{course.description}</p>
                <div className="mt-3 flex items-center gap-3">
                  {hasValidAccess ? (
                    <Link
                      href={`/dashboard/courses/${course.id}`}
                      className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium"
                    >
                      Go to course
                    </Link>
                  ) : session?.user?.id ? (
                    <PurchaseButton courseId={course.id} />
                  ) : (
                    <span className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium">
                      Purchase
                    </span>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </AppShell>
  );
}
