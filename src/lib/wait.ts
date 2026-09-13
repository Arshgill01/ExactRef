export type CallSurface = "calls" | "goals" | "mcp";

export type WaitHonesty = {
  surface: CallSurface;
  topLevelStatus: string | null;
  hasAttemptActivity: boolean;
  structuredResult: unknown;
  goalResult: unknown;
  goalError: unknown;
  localWaitTimedOut: boolean;
};

export type WaitDecision = {
  treatAsIdle: boolean;
  treatAsMaterialized: boolean;
  treatTimeoutAsHangup: boolean;
  note: string;
};

export function interpretWait(input: WaitHonesty): WaitDecision {
  if (input.localWaitTimedOut) {
    return {
      treatAsIdle: false,
      treatAsMaterialized: false,
      treatTimeoutAsHangup: false,
      note: "A local wait timeout does not cancel or hang up the call. Keep the stored id and poll again.",
    };
  }

  if (input.surface === "calls") {
    const terminal = ["completed", "failed", "canceled"].includes(input.topLevelStatus ?? "");
    if (input.topLevelStatus === "queued" && input.hasAttemptActivity) {
      return {
        treatAsIdle: false,
        treatAsMaterialized: false,
        treatTimeoutAsHangup: false,
        note: "Top-level queued can include an active attempt. Do not create again.",
      };
    }
    return {
      treatAsIdle: !terminal && !input.hasAttemptActivity,
      treatAsMaterialized: terminal && input.structuredResult != null,
      treatTimeoutAsHangup: false,
      note: terminal
        ? "Calls wait returns on top-level status. Check structuredResult before writing."
        : "Call has not reached a terminal status.",
    };
  }

  if (input.surface === "goals") {
    const materialized = input.goalResult != null || input.goalError != null;
    return {
      treatAsIdle: false,
      treatAsMaterialized: materialized,
      treatTimeoutAsHangup: false,
      note: materialized
        ? "Goal wait is materialized (result or error is non-null)."
        : "Goal run is not materialized yet. Status completed is not enough.",
    };
  }

  return {
    treatAsIdle: false,
    treatAsMaterialized: false,
    treatTimeoutAsHangup: false,
    note: "MCP get_call_run fields live under result{}. COMPLETED is not task success. Do not call track_ui_events.",
  };
}
