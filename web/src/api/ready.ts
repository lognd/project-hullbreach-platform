import { apiFetch } from "@/api/auth";

/** Path of the readiness endpoint (T-0012). */
const READY_PATH = "/api/v1/ready";

/** Request budget of the status probe; shorter than the default so a dead backend shows "down" quickly. */
export const READY_TIMEOUT_MS = 3_000;

/** Whether the backend answered its readiness probe. */
export type BackendStatus = "up" | "down";

// frob:ticket 01M2KR6R34724T0ND699BV81G9
// frob:doc docs/index.md#backend-status-indicator
/** GET /api/v1/ready with a READY_TIMEOUT_MS budget; "up" only for a 2xx, "down" for any other status, a timeout or a network failure (never throws). */
export async function checkReady(): Promise<BackendStatus> {
  try {
    const response = await apiFetch(READY_PATH, {}, READY_TIMEOUT_MS);
    if (response.ok) {
      return "up";
    }
    console.warn(`backend not ready: HTTP ${String(response.status)}`);
    return "down";
  } catch (error) {
    console.warn("backend ready probe failed", error);
    return "down";
  }
}
