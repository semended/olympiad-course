"use client";

import { useState } from "react";

type PurchaseButtonProps = {
  courseId: string;
};

export function PurchaseButton({ courseId }: PurchaseButtonProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handlePurchase = async () => {
    setLoading(true);
    setError("");

    const response = await fetch("/api/stripe/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId })
    });

    setLoading(false);

    if (!response.ok) {
      setError("Не удалось создать checkout сессию.");
      return;
    }

    const payload = (await response.json()) as { url: string };

    window.location.href = payload.url;
  };

  return (
    <div className="flex flex-col items-start gap-2">
      <button
        type="button"
        onClick={handlePurchase}
        disabled={loading}
        className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white"
      >
        {loading ? "Redirecting..." : "Purchase"}
      </button>
      {error ? <p className="text-xs text-red-500">{error}</p> : null}
    </div>
  );
}
