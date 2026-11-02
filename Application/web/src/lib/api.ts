import { getToken } from "./session";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
  token?: string | null;
  auth?: boolean;
  headers?: Record<string, string>;
}

function describeDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((entry) => {
        if (typeof entry === "string") return entry;
        if (entry && typeof entry === "object") {
          const record = entry as { loc?: unknown[]; msg?: string };
          const field = Array.isArray(record.loc) ? record.loc.slice(1).join(".") : "";
          return field ? `${field}: ${record.msg ?? "invalid value"}` : record.msg ?? "invalid value";
        }
        return "invalid value";
      })
      .join("; ");
  }
  return "Request failed";
}

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json", ...options.headers };
  const isForm = typeof FormData !== "undefined" && options.body instanceof FormData;
  if (options.body !== undefined && !isForm) headers["Content-Type"] = "application/json";

  const token = options.token !== undefined
    ? options.token
    : options.auth === false
      ? null
      : getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method: options.method ?? (options.body !== undefined ? "POST" : "GET"),
      headers,
      body:
        options.body === undefined
          ? undefined
          : isForm
            ? (options.body as FormData)
            : JSON.stringify(options.body),
      cache: "no-store",
    });
  } catch {
    throw new ApiError(
      "Cannot reach the Usiri API. Check that the backend is running on port 8000.",
      0,
    );
  }

  if (response.status === 204) return undefined as T;

  const text = await response.text();
  let payload: unknown = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!response.ok) {
    const record = (payload ?? {}) as { detail?: unknown; code?: string };
    throw new ApiError(
      describeDetail(record.detail),
      response.status,
      typeof record.code === "string" ? record.code : undefined,
    );
  }

  return payload as T;
}

export function idempotencyKey(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
