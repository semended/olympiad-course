import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { authOptions } from "@/lib/auth";
import { getUserSubmissions } from "@/lib/data/submissions";

export default async function DashboardSubmissionsPage() {
  const session = await getServerSession(authOptions);

  if (!session?.user?.id) {
    redirect("/auth/login");
  }

  const submissions = await getUserSubmissions(session.user.id);

  return (
    <AppShell>
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">My Submissions</h2>
        <p className="text-sm text-slate-600">Все отправленные решения текущего пользователя.</p>

        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left">
              <tr>
                <th className="px-4 py-3 font-medium text-slate-600">Material</th>
                <th className="px-4 py-3 font-medium text-slate-600">Status</th>
                <th className="px-4 py-3 font-medium text-slate-600">TeacherScore</th>
                <th className="px-4 py-3 font-medium text-slate-600">CreatedAt</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {submissions.length > 0 ? (
                submissions.map((submission) => (
                  <tr key={submission.id}>
                    <td className="px-4 py-3">{submission.material.title}</td>
                    <td className="px-4 py-3">{submission.status}</td>
                    <td className="px-4 py-3">
                      {submission.teacherScore === null ? "—" : submission.teacherScore}
                    </td>
                    <td className="px-4 py-3">{new Date(submission.createdAt).toLocaleString()}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-slate-500">
                    Пока нет submissions.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </AppShell>
  );
}
