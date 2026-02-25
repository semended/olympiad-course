import { getServerSession } from "next-auth";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { authOptions } from "@/lib/auth";
import { getEnrollmentForCourse } from "@/lib/data/enrollments";
import { getModuleById } from "@/lib/data/lms";
import { getCourseProgressForUser } from "@/lib/data/progress";

type ModulePageProps = {
  params: {
    courseId: string;
    moduleId: string;
  };
};

function formatStatus(status: "NOT_SUBMITTED" | "PENDING" | "REVIEWED", score: number | null) {
  if (status === "REVIEWED") {
    return `Reviewed${score === null ? "" : ` (${score})`}`;
  }

  if (status === "PENDING") {
    return "Pending";
  }

  return "Not submitted";
}

export default async function ModulePage({ params }: ModulePageProps) {
  const session = await getServerSession(authOptions);

  if (!session?.user?.id) {
    redirect("/auth/login");
  }

  const enrollment = await getEnrollmentForCourse(session.user.id, params.courseId);

  if (!enrollment || enrollment.expiresAt <= new Date()) {
    redirect("/courses?message=Access%20expired%20or%20not%20purchased");
  }

  const module = await getModuleById(params.courseId, params.moduleId);

  if (!module) {
    notFound();
  }

  const progress = await getCourseProgressForUser(params.courseId, session.user.id);

  return (
    <AppShell>
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">
          {module.title} ({module.course.title})
        </h2>
        <p className="text-sm text-slate-600">Список материалов модуля и текущий статус отправки.</p>

        <div className="space-y-3">
          {module.materials.map((material) => {
            const materialState = progress.materialStates.find((item) => item.material.id === material.id);
            const statusLabel = formatStatus(
              materialState?.status ?? "NOT_SUBMITTED",
              materialState?.teacherScore ?? null
            );

            return (
              <Link
                key={material.id}
                href={`/dashboard/material/${material.id}`}
                className="flex items-center justify-between rounded-xl border bg-white p-4 shadow-sm"
              >
                <div>
                  <p className="font-semibold">{material.title}</p>
                  <p className="text-xs text-slate-500">{material.type}</p>
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                  {statusLabel}
                </span>
              </Link>
            );
          })}
        </div>
      </section>
    </AppShell>
  );
}
