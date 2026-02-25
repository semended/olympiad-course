"use client";

import { FormEvent, useEffect, useState } from "react";

type Submission = {
  id: string;
  status: "PENDING" | "REVIEWED";
  teacherScore: number | null;
  createdAt: string;
};

type SubmitSolutionFormProps = {
  materialId: string;
};

export function SubmitSolutionForm({ materialId }: SubmitSolutionFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [currentSubmission, setCurrentSubmission] = useState<Submission | null>(null);

  useEffect(() => {
    const loadSubmission = async () => {
      const response = await fetch(`/api/submissions?materialId=${materialId}`);
      if (!response.ok) {
        return;
      }

      const payload = (await response.json()) as { submission: Submission | null };
      setCurrentSubmission(payload.submission);
    };

    void loadSubmission();
  }, [materialId]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();

    if (!selectedFile) {
      setMessage("Выберите файл для отправки.");
      return;
    }

    setLoading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    const uploadResponse = await fetch("/api/upload", {
      method: "POST",
      body: formData
    });

    if (!uploadResponse.ok) {
      setLoading(false);
      setMessage("Не удалось загрузить файл.");
      return;
    }

    const uploadPayload = (await uploadResponse.json()) as { fileUrl: string };

    const submissionResponse = await fetch("/api/submissions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ materialId, fileUrl: uploadPayload.fileUrl })
    });

    setLoading(false);

    if (!submissionResponse.ok) {
      setMessage("Не удалось отправить решение.");
      return;
    }

    const payload = (await submissionResponse.json()) as { submission: Submission };
    setCurrentSubmission(payload.submission);
    setSelectedFile(null);
    setMessage("Solution submitted");
  };

  return (
    <div className="rounded-xl border bg-white p-4 shadow-sm">
      <h3 className="text-lg font-semibold">Submit Solution</h3>
      <form className="mt-3 space-y-3" onSubmit={onSubmit}>
        <input
          type="file"
          required
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
          className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white"
        >
          {loading ? "Submitting..." : "Submit"}
        </button>
      </form>

      {message ? <p className="mt-3 text-sm text-emerald-600">{message}</p> : null}

      {currentSubmission ? (
        <div className="mt-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
          <p>Status: {currentSubmission.status}</p>
          <p>Created: {new Date(currentSubmission.createdAt).toLocaleString()}</p>
          <p>
            Teacher Score: {currentSubmission.teacherScore === null ? "—" : currentSubmission.teacherScore}
          </p>
        </div>
      ) : null}
    </div>
  );
}
