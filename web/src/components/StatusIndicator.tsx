import { useEffect, useState } from "react";
import { checkReady, type BackendStatus } from "@/api/ready";

/** How often the indicator re-probes the backend. */
export const STATUS_POLL_MS = 30_000;

/** Label and color per state; the word is always shown so color is never the only cue. */
const VIEW: Record<BackendStatus | "checking", { label: string; dot: string }> = {
  checking: { label: "checking", dot: "bg-line" },
  up: { label: "up", dot: "bg-accent" },
  down: { label: "down", dot: "bg-signal" },
};

// frob:ticket 01M2KR6R34724T0ND699BV81G9
// frob:doc docs/index.md#backend-status-indicator
/** Small footer readout of whether the backend answers /api/v1/ready; re-probes every STATUS_POLL_MS. */
export function StatusIndicator() {
  const [status, setStatus] = useState<BackendStatus | "checking">("checking");

  useEffect(() => {
    let live = true;
    const probe = () => {
      void checkReady().then((next) => {
        if (live) {
          setStatus(next);
        }
      });
    };
    probe();
    const timer = setInterval(probe, STATUS_POLL_MS);
    return () => {
      live = false;
      clearInterval(timer);
    };
  }, []);

  const view = VIEW[status];
  return (
    <span
      role="status"
      aria-label={`Backend ${view.label}`}
      className="inline-flex items-center gap-space-8 font-mono uppercase tracking-widest"
    >
      <span aria-hidden="true" className={`inline-block h-2 w-2 ${view.dot}`} />
      API {view.label}
    </span>
  );
}
