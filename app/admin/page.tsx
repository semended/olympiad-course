import { getServerSession } from "next-auth";
import Link from "next/link";
import { redirect } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { authOptions } from "@/lib/auth";
import { getAllCourses } from "@/lib/data/lms";
import { getAllSubmissions } from "@/lib/data/submissions";

export default async function AdminPage() {
  const session = await getServerSession(authOptions);

  if (session?.user.role !== "ADMIN") {
    redirect("/dashboard");
  }

  const [courses, submissions] = await Promise.all([getAllCourses(), getAllSubmissions()]);

  return (
    <AppShell>
      <section className="space-y-6">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold">Admin</h2>
            <p className="text-sm text-slate-600">Управление курсами LMS.</p>
          </div>
          <button
            type="button"
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
          >
            Create Course
          </button>
        </div>

        <div>
          <h3 className="mb-3 text-lg font-semibold">Courses</h3>
          <div className="space-y-3">
            {courses.map((course) => (
              <article key={course.id} className="rounded-xl border bg-white p-4 shadow-sm">
                <h4 className="font-semibold">{course.title}</h4>
                <p className="text-sm text-slate-600">{course.description}</p>
              </article>
            ))}
          </div>
        </div>

        <div>
          <h3 className="mb-3 text-lg font-semibold">Submissions</h3>
          <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50 text-left">
                <tr>
                  <th className="px-4 py-3 font-medium text-slate-600">User</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Material</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Status</th>
                  <th className="px-4 py-3 font-medium text-slate-600">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {submissions.length > 0 ? (
                  submissions.map((submission) => (
                    <tr key={submission.id}>
                      <td className="px-4 py-3">{submission.user.name ?? submission.user.email}</td>
                      <td className="px-4 py-3">{submission.material.title}</td>
                      <td className="px-4 py-3">{submission.status}</td>
                      <td className="px-4 py-3">
                        <Link
                          href={`/admin/submissions/${submission.id}`}
                          className="rounded-lg border border-slate-200 px-3 py-1.5"
                        >
                          Review
                        </Link>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-center text-slate-500">
                      Нет submissions для проверки.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </AppShell>
  );
}
