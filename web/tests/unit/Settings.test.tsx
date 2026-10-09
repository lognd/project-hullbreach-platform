import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { loadSession, saveSession } from "@/auth/session";
import { Settings } from "@/pages/Settings";
import { profileFixture } from "../fixtures/me";

/** A JSON Response, as the server would send it. */
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

/** Persists a signed-in session so the page has a token to send. */
function signIn(): void {
  saveSession({ token: "tok-1", userId: "user-1", username: "flagship", role: "player" });
}

/** Stubs fetch with one canned response and returns the mock for call assertions. */
function stubFetch(response: Response) {
  const fetchMock = vi.fn().mockResolvedValue(response);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

/** Parses the JSON body of the mock's first call. */
function sentBody(fetchMock: ReturnType<typeof vi.fn>): unknown {
  const init = fetchMock.mock.calls[0][1] as RequestInit;
  return JSON.parse(init.body as string);
}

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.localStorage.clear();
});

describe("Settings page", () => {
  // frob:tests web/src/pages/Settings.tsx::Settings kind="unit"
  // frob:tests web/src/api/me.ts::updateMe kind="unit"
  it("sends only the changed email and current password, then confirms", async () => {
    signIn();
    const fetchMock = stubFetch(
      jsonResponse({ ...profileFixture, email: "new@example.com" }),
    );
    const user = userEvent.setup();
    render(<Settings />);

    await user.type(screen.getByLabelText(/new email/i), "new@example.com");
    await user.type(screen.getByLabelText(/current password/i), "correct-horse");
    await user.click(screen.getByRole("button", { name: /save/i }));

    expect(await screen.findByRole("status")).toHaveTextContent(/saved/i);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/me",
      expect.objectContaining({
        method: "PATCH",
        headers: expect.objectContaining({ Authorization: "Bearer tok-1" }),
      }),
    );
    expect(sentBody(fetchMock)).toEqual({
      email: "new@example.com",
      current_password: "correct-horse",
    });
    expect(screen.getByLabelText(/new email/i)).toHaveValue("");
    expect(screen.getByLabelText(/current password/i)).toHaveValue("");
  });

  // frob:tests web/src/pages/Settings.tsx::Settings kind="unit"
  it("shows the error and changes nothing when the current password is wrong", async () => {
    signIn();
    const fetchMock = stubFetch(
      jsonResponse(
        { detail: "current password is incorrect", field: "current_password" },
        403,
      ),
    );
    const user = userEvent.setup();
    render(<Settings />);

    await user.type(screen.getByLabelText(/new password/i), "brand-new-secret");
    await user.type(screen.getByLabelText(/current password/i), "wrong");
    await user.click(screen.getByRole("button", { name: /save/i }));

    await screen.findByText("current password is incorrect");
    expect(screen.getByLabelText(/current password/i)).toHaveAccessibleDescription(
      "current password is incorrect",
    );
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
    expect(loadSession()?.username).toBe("flagship");
    expect(sentBody(fetchMock)).toEqual({
      password: "brand-new-secret",
      current_password: "wrong",
    });
    expect(screen.getByLabelText(/new password/i)).toHaveValue("brand-new-secret");
  });

  // frob:tests web/src/pages/Settings.tsx::Settings kind="unit"
  it("refuses an email or password change without the current password and sends nothing", async () => {
    signIn();
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<Settings />);

    await user.type(screen.getByLabelText(/new email/i), "new@example.com");
    await user.click(screen.getByRole("button", { name: /save/i }));

    expect(screen.getByLabelText(/current password/i)).toHaveAccessibleDescription(
      /enter your current password/i,
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  // frob:tests web/src/pages/Settings.tsx::Settings kind="unit"
  it("changes the display name without a current password and updates the stored session", async () => {
    signIn();
    const fetchMock = stubFetch(jsonResponse({ ...profileFixture, username: "admiral" }));
    const user = userEvent.setup();
    render(<Settings />);

    await user.clear(screen.getByLabelText(/display name/i));
    await user.type(screen.getByLabelText(/display name/i), "admiral");
    await user.click(screen.getByRole("button", { name: /save/i }));

    expect(await screen.findByRole("status")).toHaveTextContent(/saved/i);
    expect(sentBody(fetchMock)).toEqual({ username: "admiral" });
    expect(loadSession()).toMatchObject({ token: "tok-1", username: "admiral" });
    expect(screen.getByLabelText(/display name/i)).toHaveValue("admiral");
  });

  // frob:tests web/src/pages/Settings.tsx::Settings kind="unit"
  it("shows a rejected display name next to its field", async () => {
    signIn();
    stubFetch(jsonResponse({ detail: "username already taken", field: "username" }, 409));
    const user = userEvent.setup();
    render(<Settings />);

    await user.clear(screen.getByLabelText(/display name/i));
    await user.type(screen.getByLabelText(/display name/i), "taken");
    await user.click(screen.getByRole("button", { name: /save/i }));

    expect(await screen.findByLabelText(/display name/i)).toHaveAccessibleDescription(
      "username already taken",
    );
    expect(loadSession()?.username).toBe("flagship");
  });

  // frob:tests web/src/pages/Settings.tsx::Settings kind="unit"
  it("shows a banner for a failure with no field, and for a network error", async () => {
    signIn();
    stubFetch(jsonResponse({ detail: "validation failed" }, 422));
    const user = userEvent.setup();
    render(<Settings />);
    await user.type(screen.getByLabelText(/new password/i), "short");
    await user.type(screen.getByLabelText(/current password/i), "correct-horse");
    await user.click(screen.getByRole("button", { name: /save/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent("validation failed");

    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
    await user.click(screen.getByRole("button", { name: /save/i }));
    expect(await screen.findByText(/something went wrong/i)).toBeInTheDocument();
  });

  // frob:tests web/src/pages/Settings.tsx::Settings kind="unit"
  it("says there is nothing to change when the form is untouched", async () => {
    signIn();
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<Settings />);

    await user.click(screen.getByRole("button", { name: /save/i }));

    expect(screen.getByRole("alert")).toHaveTextContent(/nothing to change/i);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  // frob:tests web/src/pages/Settings.tsx::Settings kind="unit"
  // frob:tests web/src/components/SignInPrompt.tsx::SignInPrompt kind="unit"
  it("asks a signed-out visitor to log in and shows no form", () => {
    render(<Settings />);

    expect(screen.getByRole("link", { name: /log in/i })).toHaveAttribute(
      "href",
      "/login",
    );
    expect(screen.queryByRole("button", { name: /save/i })).not.toBeInTheDocument();
  });
});
