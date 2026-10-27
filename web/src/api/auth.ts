/** Base path for every auth endpoint (docs/design/sprint-1.md sec.5); vite proxies /api to the server in dev. */
const AUTH_BASE = "/api/v1/auth";

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** A user's role, as returned by every auth endpoint that exposes one. */
export type Role = "player" | "admin";

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** The profile shape every auth endpoint that returns a user echoes (docs/design/sprint-1.md sec.5). */
export type UserProfile = {
  id: string;
  username: string;
  email: string;
  role: Role;
  currency: number;
  rating: number;
  created_at: string;
};

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** POST /api/v1/auth/register's request body. */
export type RegisterRequest = {
  username: string;
  email: string;
  password: string;
};

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** POST /api/v1/auth/login's request body. */
export type LoginRequest = {
  username: string;
  password: string;
};

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** POST /api/v1/auth/login's 200 response body. */
export type LoginResponse = {
  token: string;
  user: UserProfile;
};

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** A non-2xx auth response, normalized to a status/detail/optional field shape (docs/design/sprint-1.md sec.6). */
export class ApiError extends Error {
  status: number;
  detail: string;
  field?: string;
  /** Every rejected field with its reason (register's 422 `errors` list); absent otherwise. */
  fieldErrors?: Record<string, string>;

  // frob:doc docs/index.md#auth-api-client-and-the-register-page
  constructor(
    status: number,
    detail: string,
    field?: string,
    fieldErrors?: Record<string, string>,
  ) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
    this.field = field;
    this.fieldErrors = fieldErrors;
  }
}

/** Reads register's `errors` list ([{field, detail}]) into a field-keyed map; undefined when absent or empty. */
function parseFieldErrors(errors: unknown): Record<string, string> | undefined {
  if (!Array.isArray(errors)) {
    return undefined;
  }
  const out: Record<string, string> = {};
  for (const item of errors as unknown[]) {
    if (item !== null && typeof item === "object") {
      const { field, detail } = item as Record<string, unknown>;
      if (typeof field === "string" && typeof detail === "string" && !(field in out)) {
        out[field] = detail;
      }
    }
  }
  return Object.keys(out).length > 0 ? out : undefined;
}

/** Extracts a {detail, field?, fieldErrors?} triple from a non-ok Response body, tolerating FastAPI's array-shaped 422 detail. */
async function parseErrorBody(response: Response): Promise<{
  detail: string;
  field?: string;
  fieldErrors?: Record<string, string>;
}> {
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  if (body !== null && typeof body === "object") {
    const record = body as Record<string, unknown>;
    if (typeof record.detail === "string") {
      const field = typeof record.field === "string" ? record.field : undefined;
      return {
        detail: record.detail,
        field,
        fieldErrors: parseFieldErrors(record.errors),
      };
    }
    if (Array.isArray(record.detail)) {
      return { detail: "validation failed" };
    }
  }
  return { detail: "request failed" };
}

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** Builds the ApiError for a non-ok Response, so every client throws the same normalized shape. */
export async function errorFromResponse(response: Response): Promise<ApiError> {
  const { detail, field, fieldErrors } = await parseErrorBody(response);
  return new ApiError(response.status, detail, field, fieldErrors);
}

/** Default per-request budget; a hung server must not hang the page (~R5PHHZC). */
export const REQUEST_TIMEOUT_MS = 10_000;

/** Header every web request carries so the server accepts cookie-authenticated writes (CSRF defence, ~6TZCHZ0). */
export const CSRF_HEADER = "X-Hullbreach-Web";

// frob:ticket 01M2KR6R362BWF543KBR5PHHZC
// frob:ticket 01M4GS9A33TBP96SJ646TZCHZ0
// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** fetch() with the session cookie (credentials: include), the CSRF header and an AbortController timeout; a timeout rejects with an ApiError of status 0; other network failures propagate unchanged. */
export async function apiFetch(
  path: string,
  init: RequestInit = {},
  timeoutMs: number = REQUEST_TIMEOUT_MS,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => {
    controller.abort();
  }, timeoutMs);
  try {
    return await fetch(path, {
      ...init,
      credentials: "include",
      headers: { ...(init.headers as Record<string, string>), [CSRF_HEADER]: "1" },
      signal: controller.signal,
    });
  } catch (error) {
    if (controller.signal.aborted) {
      throw new ApiError(0, "request timed out");
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** Fetches `path` via apiFetch, parsing the JSON body or throwing an ApiError for a non-ok response; shared by every API client module. */
export async function requestJson<T>(
  path: string,
  init?: RequestInit,
  timeoutMs?: number,
): Promise<T> {
  const response = await apiFetch(path, init, timeoutMs);
  if (!response.ok) {
    throw await errorFromResponse(response);
  }
  return (await response.json()) as T;
}

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** The Authorization header for a signed-in request; empty for a cookie-restored session (token ""), which authenticates by cookie instead. */
export function bearerHeaders(token: string): Record<string, string> {
  if (token === "") {
    return {};
  }
  return { Authorization: `Bearer ${token}` };
}

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** POST /api/v1/auth/register; 201 UserProfile on success, 409/422 rejects with an ApiError. */
export async function register(payload: RegisterRequest): Promise<UserProfile> {
  return requestJson<UserProfile>(`${AUTH_BASE}/register`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
}

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** POST /api/v1/auth/login; 200 LoginResponse on success, 401/429 rejects with an ApiError. */
export async function login(payload: LoginRequest): Promise<LoginResponse> {
  return requestJson<LoginResponse>(`${AUTH_BASE}/login`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });
}

// frob:doc docs/index.md#auth-api-client-and-the-register-page
/** POST /api/v1/auth/logout with the caller's bearer token; 204 on success, throws an ApiError otherwise. */
export async function logout(token: string): Promise<void> {
  const response = await apiFetch(`${AUTH_BASE}/logout`, {
    method: "POST",
    headers: bearerHeaders(token),
  });
  if (!response.ok) {
    throw await errorFromResponse(response);
  }
}
