import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { clearSession } from "@/auth/session";

// The session store is module state; reset it so tests do not leak sign-in.
afterEach(() => {
  clearSession();
});
