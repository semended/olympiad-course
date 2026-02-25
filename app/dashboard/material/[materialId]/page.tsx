import { getServerSession } from "next-auth";
import { notFound, redirect } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { SubmitSolutionForm } from "@/components/submissions/submit-solution-form";
import { authOptions } from "@/lib/auth";
import { getEnrollmentForCourse } from "@/lib/data/enrollments";
import { getMaterialById } from "@/lib/data/lms";

type MaterialPageProps = {
  params: {
    materialId: string;
  };
};

export default async function MaterialPage({ params }: MaterialPageProps) {
  const session = await getServerSession(authOptions);

  if (!session?.user?.id) {
    redirect("/auth/login");
  }

  const material = await getMaterialById(params.materialId);

  if (!material) {
    notFound();
  }

  const courseId = material.module.course.id;
  const enrollment = await getEnrollmentForCourse(session.user.id, courseId);

  if (!enrollment || enrollment.expiresAt <= new Date()) {
    redirect("/courses?message=Access%20expired%20or%20not%20purchased");
  }

  return (
    <AppShell>
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Material: {material.title}</h2>
        <p className="text-sm text-slate-600">Type: {material.type}</p>
        <div className="rounded-xl border bg-white p-4 text-sm text-slate-700 shadow-sm">{material.content}</div>

        {material.type === "HOMEWORK" || material.type === "EXAM" ? (
          <SubmitSolutionForm materialId={params.materialId} />
        ) : (
          <div className="rounded-xl border bg-white p-4 text-sm text-slate-600 shadow-sm">
            Для LESSON отправка решения не требуется.
          </div>
        )}
      </section>
    </AppShell>
  );
}
