"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function ReplayAll() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="actions">
      <button
        type="button"
        className="btn"
        onClick={async () => {
          setError(null);
          const response = await fetch("/api/docket/replay", { method: "POST" });
          if (!response.ok) {
            setError("Replay failed.");
            return;
          }
          router.refresh();
          router.push("/");
        }}
      >
        Replay fixtures
      </button>
      {error ? (
        <p className="reason" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
