import type { ApiError } from "@/types/common";

class ApiClientError extends Error {
  status: number;
  code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
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

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let error: ApiError = { detail: `HTTP ${response.status}` };
    try {
      error = (await response.json()) as ApiError;
    } catch {
      // ignore parse errors
    }
    throw new ApiClientError(error.detail, response.status, error.code);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

function buildUrl(path: string, params?: Record<string, string | undefined>): string {
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
