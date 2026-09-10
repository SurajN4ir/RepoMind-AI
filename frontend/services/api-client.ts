/**
 * Extract a human-readable message from a FastAPI error body.
 *
 * `detail` is usually a plain string (HTTPException(detail="...")), but the
 * indexing/query/legacy-ingest endpoints report pipeline failures as a
 * structured object with an `errors` array (see IndexingResponse/QueryResponse
 * in the backend). Without this, those failures would surface as
 * "[object Object]" instead of the actual error text.
 */
function extractErrorMessage(detail: unknown, status: number): string {
  if (typeof detail === "string" && detail.length > 0) return detail;
  if (detail && typeof detail === "object") {
    const body = detail as Record<string, unknown>;
    if (Array.isArray(body.errors) && body.errors.length > 0) {
      return body.errors.filter((e) => typeof e === "string").join("; ");
    }
    if (typeof body.detail === "string") return body.detail;
  }
  return `HTTP ${status}`;
}

class ApiClientError extends Error {
  status: number;
  code?: string;
  /** The raw, unparsed `detail` field from the response body, for callers
   * that need more than the flattened message (e.g. a full errors[] list). */
  detail: unknown;

  constructor(detail: unknown, status: number, code?: string) {
    super(extractErrorMessage(detail, status));
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
    this.detail = detail;
  }
}

let _getToken: (() => Promise<string | null>) | null = null;

export function setTokenProvider(fn: () => Promise<string | null>) {
  _getToken = fn;
}

async function authHeaders(): Promise<Record<string, string>> {
  if (!_getToken) return {};
  const token = await _getToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

/**
 * The current caller's auth header, for the rare case where a component
 * needs to build its own fetch() (e.g. reading a streaming response body
 * directly) instead of going through apiClient. Keeps token retrieval in
 * one place rather than re-implementing setTokenProvider's consumer logic.
 */
export async function getAuthHeaders(): Promise<Record<string, string>> {
  return authHeaders();
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let body: unknown = undefined;
    try {
      body = await response.json();
    } catch {
      // ignore parse errors; extractErrorMessage falls back to the status
    }
    const detail = (body as { detail?: unknown } | undefined)?.detail ?? body;
    const code = (body as { code?: string } | undefined)?.code;
    throw new ApiClientError(detail, response.status, code);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

/** Exported so callers building their own fetch() (streaming) use the same
 * base-URL resolution as every other request instead of hardcoding it. */
export function buildUrl(path: string, params?: Record<string, string | undefined>): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const url = new URL(`${baseUrl}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) url.searchParams.set(key, value);
    });
  }
  return url.toString();
}

async function getHeaders(
  customHeaders?: Record<string, string>,
): Promise<Record<string, string>> {
  return {
    ...(customHeaders?.ContentType
      ? {}
      : { "Content-Type": "application/json" }),
    ...customHeaders,
    ...(await authHeaders()),
  };
}

export const apiClient = {
  async get<T>(
    path: string,
    params?: Record<string, string | undefined>,
  ): Promise<T> {
    const response = await fetch(buildUrl(path, params), {
      headers: await getHeaders(),
    });
    return handleResponse<T>(response);
  },

  async post<T>(
    path: string,
    body?: unknown,
    customHeaders?: Record<string, string>,
  ): Promise<T> {
    const response = await fetch(buildUrl(path), {
      method: "POST",
      headers: await getHeaders(customHeaders),
      body: body ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async put<T>(
    path: string,
    body?: unknown,
  ): Promise<T> {
    const response = await fetch(buildUrl(path), {
      method: "PUT",
      headers: await getHeaders(),
      body: body ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async patch<T>(
    path: string,
    body?: unknown,
  ): Promise<T> {
    const response = await fetch(buildUrl(path), {
      method: "PATCH",
      headers: await getHeaders(),
      body: body ? JSON.stringify(body) : undefined,
    });
    return handleResponse<T>(response);
  },

  async delete<T>(path: string): Promise<T> {
    const response = await fetch(buildUrl(path), {
      method: "DELETE",
      headers: await getHeaders(),
    });
    return handleResponse<T>(response);
  },
};

export { ApiClientError };
