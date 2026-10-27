import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { checkReady, READY_TIMEOUT_MS } from "@/api/ready";
import { Footer } from "@/components/Footer";
import { StatusIndicator, STATUS_POLL_MS } from "@/components/StatusIndicator";
import { overflowRisks } from "../support/layout";

beforeEach(() => {
  vi.spyOn(console, "warn").mockImplementation(() => undefined);
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("checkReady", () => {
  // frob:tests web/src/api/ready.ts::checkReady kind="unit"
  it("is up for a 200 from /api/v1/ready", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response("{}", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    expect(await checkReady()).toBe("up");
    expect(fetchMock.mock.calls[0][0]).toBe("/api/v1/ready");
  });

  // frob:tests web/src/api/ready.ts::checkReady kind="unit"
  it("is down for a 503 and for a network failure", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("{}", { status: 503 })));
    expect(await checkReady()).toBe("down");
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
    expect(await checkReady()).toBe("down");
  });

  // frob:tests web/src/api/ready.ts::checkReady kind="unit"
  it("is down when the request exceeds the timeout", async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      "fetch",
      vi.fn(
        (_path: string, init: RequestInit) =>
          new Promise<Response>((_resolve, reject) => {
            init.signal?.addEventListener("abort", () => {
              reject(new DOMException("aborted", "AbortError"));
            });
          }),
      ),
    );
    const result = checkReady();
    await vi.advanceTimersByTimeAsync(READY_TIMEOUT_MS + 1);
    expect(await result).toBe("down");
  });
});

describe("StatusIndicator", () => {
  // frob:tests web/src/components/StatusIndicator.tsx::StatusIndicator kind="unit"
  it("shows up when the backend is ready", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("{}", { status: 200 })));
    render(<StatusIndicator />);
    expect(await screen.findByText(/API up/)).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveAccessibleName("Backend up");
  });

  // frob:tests web/src/components/StatusIndicator.tsx::StatusIndicator kind="unit"
  it("shows down, then recovers on the next poll", async () => {
    vi.useFakeTimers();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response("{}", { status: 503 }))
      .mockResolvedValue(new Response("{}", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<StatusIndicator />);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(screen.getByText(/API down/)).toBeInTheDocument();
    await act(async () => {
      await vi.advanceTimersByTimeAsync(STATUS_POLL_MS);
    });
    expect(screen.getByText(/API up/)).toBeInTheDocument();
  });

  // frob:tests web/src/components/Footer.tsx::Footer kind="unit"
  it("sits in the footer without width that overflows 390 px", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("{}", { status: 200 })));
    const { container } = render(<Footer />);
    expect(await screen.findByText(/API up/)).toBeInTheDocument();
    expect(overflowRisks(container, 390)).toEqual([]);
  });
});
