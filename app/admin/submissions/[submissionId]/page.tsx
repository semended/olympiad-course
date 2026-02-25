import { getServerSession } from "next-auth";
import { notFound, redirect } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { ReviewSubmissionForm } from "@/components/submissions/review-submission-form";
import { authOptions } from "@/lib/auth";
import { getSubmissionById } from "@/lib/data/submissions";

type AdminSubmissionReviewPageProps = {
  params: {
    submissionId: string;
  };
};

export default async function AdminSubmissionReviewPage({ params }: AdminSubmissionReviewPageProps) {
  const session = await getServerSession(authOptions);

  if (session?.user.role !== "ADMIN") {
    redirect("/dashboard");
  }

  const submission = await getSubmissionById(params.submissionId);

  if (!submission) {
    notFound();
  }

  return (
    <AppShell>
      <section className="space-y-4">
        <h2 className="text-2xl font-semibold">Submission Review</h2>
        <div className="rounded-xl border bg-white p-4 shadow-sm">
          <p className="text-sm text-slate-500">User: {submission.user.name ?? submission.user.email}</p>
          <p className="text-sm text-slate-500">Material: {submission.material.title}</p>
          <a
            href={submission.fileUrl}
            target="_blank"
            rel="noreferrer"
            className="mt-3 inline-flex rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium"
          >
            View file
          </a>
          {submission.extractedText ? (
            <p className="mt-3 whitespace-pre-wrap text-sm text-slate-800">{submission.extractedText}</p>
          ) : null}
        </div>

        <ReviewSubmissionForm
          submissionId={submission.id}
          defaultScore={submission.teacherScore}
          defaultFeedback={submission.teacherFeedback}
        />
      </section>
    </AppShell>
  );
}
