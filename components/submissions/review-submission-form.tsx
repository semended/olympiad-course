"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

type ReviewSubmissionFormProps = {
  submissionId: string;
  defaultScore: number | null;
  defaultFeedback: string | null;
};

export function ReviewSubmissionForm({
  submissionId,
  defaultScore,
  defaultFeedback
}: ReviewSubmissionFormProps) {
  const [teacherScore, setTeacherScore] = useState(defaultScore ?? 0);
  const [teacherFeedback, setTeacherFeedback] = useState(defaultFeedback ?? "");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    const response = await fetch(`/api/admin/submissions/${submissionId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ teacherScore, teacherFeedback })
    });

    setLoading(false);

    if (!response.ok) {
      setMessage("Не удалось сохранить review.");
      return;
    }

    setMessage("Review saved");
    router.refresh();
  };

  return (
    <form className="space-y-4 rounded-xl border bg-white p-4 shadow-sm" onSubmit={onSubmit}>
      <h3 className="text-lg font-semibold">Review Submission</h3>
      <div>
        <label className="mb-1 block text-sm font-medium">Teacher Score (0–7)</label>
        <input
          type="number"
          min={0}
          max={7}
          value={teacherScore}
          onChange={(event) => setTeacherScore(Number(event.target.value))}
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Teacher Feedback</label>
        <textarea
          rows={6}
          value={teacherFeedback}
          onChange={(event) => setTeacherFeedback(event.target.value)}
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
      >
        {loading ? "Saving..." : "Save Review"}
      </button>
      {message ? <p className="text-sm text-emerald-600">{message}</p> : null}
    </form>
  );
}
