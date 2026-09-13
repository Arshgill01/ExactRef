"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import { firstMismatchIndex, type DiffCell } from "@/lib/diff";
import { provenanceLabel, type IdentifierDecision } from "@/lib/provenance";

export type BoardCase = {
  id: string;
  title: string;
  fieldLabel: string;
  destinationLabel: string;
  summary: string;
  waitNote: string;
  decision: IdentifierDecision;
  task: { task: string; leaksIntended: boolean };
  cells: DiffCell[];
};

export function Board({ cases, current }: { cases: BoardCase[]; current: BoardCase }) {
  const router = useRouter();
  const [typed, setTyped] = useState("");
  const [second, setSecond] = useState(false);
  const [preview, setPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const typedId = useId();
  const checkId = useId();
  const mismatch = firstMismatchIndex(current.cells);
  const summary = current.summary.replace(/\.$/, "");

  useEffect(() => {
    setTyped("");
    setSecond(false);
    setPreview(false);
    setError(null);
  }, [current.id]);

  async function post(path: string, body?: unknown) {
    setError(null);
    const response = await fetch(path, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!response.ok) {
      const payload = (await response.json().catch(() => null)) as { error?: string } | null;
      setError(payload?.error ?? "Request failed.");
      return;
    }
    router.refresh();
  }

  return (
    <div className="shell">
      <nav className="list" aria-label="Cases">
        <h2>Cases</h2>
        {cases.map((item) => (
          <Link
            key={item.id}
            href={`/cases/${item.id}`}
            className="case-link"
            data-active={item.id === current.id}
          >
            <strong>{item.id}</strong>
            <span>{item.title}</span>
          </Link>
        ))}
      </nav>
      <main className="work">
        <div className="kicker">
          {current.id} · {current.fieldLabel} · {current.destinationLabel}
        </div>
        <h1>{current.title}</h1>
        <div className="stamp" data-kind={current.decision.provenance}>
          {provenanceLabel(current.decision.provenance)}
        </div>
        <p className="reason">{current.decision.reason}</p>
        <p className="wait">{current.waitNote}</p>

        <div className="pair">
          <div>
            <p>Intended</p>
            <div className="chars" aria-label="Intended identifier">
              {current.cells.map((cell, index) => (
                <span key={`i-${index}`} className="ch" data-mark={cell.mark}>
                  {cell.intended ?? "·"}
                </span>
              ))}
            </div>
          </div>
          <div>
            <p>Extracted</p>
            <div className="chars" aria-label="Extracted identifier">
              {current.cells.map((cell, index) => (
                <span key={`e-${index}`} className="ch" data-mark={cell.mark}>
                  {cell.extracted ?? "·"}
                </span>
              ))}
            </div>
          </div>
        </div>
        {mismatch !== null ? (
          <p className="reason">
            First difference at character {mismatch + 1}
            {current.cells[mismatch]?.intended
              ? `: intended ${current.cells[mismatch].intended}, extracted ${current.cells[mismatch].extracted ?? "none"}`
              : ""}
            .
          </p>
        ) : null}

        {current.decision.evidenceText ? (
          <p className="quote">“{current.decision.evidenceText}”</p>
        ) : (
          <p className="quote">No verbatim evidence span.</p>
        )}

        <p className="reason">
          Summary (do not schedule from this): {summary}. Writable:{" "}
          {current.decision.writable ? "yes" : "no"}.
        </p>

        <div className="actions">
          <button type="button" className="btn" onClick={() => post(`/api/cases/${current.id}/replay`)}>
            Replay fixture
          </button>
          <button type="button" className="btn" onClick={() => setPreview((value) => !value)}>
            {preview ? "Hide task" : "Preview task"}
          </button>
          <button type="button" className="btn" onClick={() => post(`/api/cases/${current.id}/keep`)}>
            Keep spoken-only
          </button>
          <button type="button" className="btn" onClick={() => dialog.current?.showModal()}>
            Place live call
          </button>
        </div>

        <form
          className="form"
          onSubmit={(event) => {
            event.preventDefault();
            void post(`/api/cases/${current.id}/verify`, {
              typed,
              claimsSecondChannel: second,
            });
          }}
        >
          <label htmlFor={typedId}>Type the identifier from a second channel</label>
          <input
            id={typedId}
            type="text"
            autoComplete="off"
            spellCheck={false}
            value={typed}
            onChange={(event) => setTyped(event.target.value)}
          />
          <label className="check" htmlFor={checkId}>
            <input
              id={checkId}
              type="checkbox"
              checked={second}
              onChange={(event) => setSecond(event.target.checked)}
            />
            I compared this to a written channel (email, portal, or paper). A spoken yes is not enough.
          </label>
          <button type="submit" className="btn" data-kind="primary">
            Mark independently verified
          </button>
        </form>
        {error ? (
          <p className="reason" role="alert">
            {error}
          </p>
        ) : null}

        {preview ? (
          <div className="preview">
            <h2>Outbound task</h2>
            <p className="reason">
              {current.task.leaksIntended
                ? "Rejected: intended identifier leaked into the task."
                : "Intended identifier is not in the task."}
            </p>
            <pre>{current.task.task}</pre>
          </div>
        ) : null}

        <dialog ref={dialog} aria-labelledby="live-title">
          <h2 id="live-title">Live create is disabled</h2>
          <p>
            ExactRef will not place a CALL-E call from this board unless{" "}
            <code>EXACTREF_LIVE=1</code> is set and a consented destination is configured.
            Replay FS-01 instead. The live F/S substitution already exists from 2026-09-05.
          </p>
          <button type="button" className="btn" onClick={() => dialog.current?.close()}>
            Close
          </button>
        </dialog>
      </main>
    </div>
  );
}
