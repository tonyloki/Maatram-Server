/**
 * Robust, Typed FastAPI Client Architecture.
 * - Browser security: Strictly relies on HttpOnly cookies + in-memory access token.
 * - Zero tokens stored in localStorage or sessionStorage.
 * - Double-Submit CSRF header injection (`X-CSRF-Token`).
 * - Single-flight deduplicated silent token refresh (/api/v1/auth/refresh).
 * - Full timeout handling (AbortController) & network error mapping.
 * - Streaming Excel binary download support (apiDownload).
 * - Cloudinary & multipart upload support (apiUpload).
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Strictly in-memory token store (Never persisted in browser storage)
let inMemoryAccessToken: string | null = null;
let tokenRefreshPromise: Promise<string | null> | null = null;
let sessionExpiredCallback: (() => void) | null = null;

// In-flight GET request deduplication map
const inFlightGetRequests = new Map<string, Promise<unknown>>();

// Short-lived in-memory response cache for read-only GET queries
interface CacheEntry {
  data: unknown;
  expiresAt: number;
}
const responseMemoryCache = new Map<string, CacheEntry>();

/**
 * Clear all in-memory cached responses and in-flight deduplication promises.
 * Called on logout, session expiration, or account switching.
 */
export function clearApiCache(): void {
  responseMemoryCache.clear();
  inFlightGetRequests.clear();
}

/**
 * Invalidate cached GET queries matching specified path prefixes.
 */
export function invalidateMatchingCache(prefixes: string[]): void {
  for (const key of responseMemoryCache.keys()) {
    const endpointPart = key.split("::")[0];
    if (prefixes.some((p) => endpointPart.includes(p))) {
      responseMemoryCache.delete(key);
    }
  }
}

function invalidateCacheForMutation(endpoint: string): void {
  const norm = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  if (norm.startsWith("/applications")) {
    invalidateMatchingCache(["/applications", "/admin/dashboard"]);
  } else if (norm.startsWith("/events")) {
    invalidateMatchingCache(["/events", "/registrations", "/admin/dashboard"]);
  } else if (norm.startsWith("/registrations")) {
    invalidateMatchingCache(["/registrations", "/events", "/admin/dashboard", "/gamification"]);
  } else if (norm.startsWith("/attendance")) {
    invalidateMatchingCache(["/attendance", "/gamification", "/admin/dashboard"]);
  } else if (norm.startsWith("/consent")) {
    invalidateMatchingCache(["/consent", "/volunteers"]);
  } else if (norm.startsWith("/volunteers")) {
    invalidateMatchingCache(["/volunteers", "/users/me"]);
  } else if (norm.startsWith("/gamification")) {
    invalidateMatchingCache(["/gamification", "/admin/dashboard"]);
  } else {
    invalidateMatchingCache(["/admin/dashboard"]);
  }
}

export function setAccessToken(token: string | null): void {
  if (token !== inMemoryAccessToken) {
    clearApiCache();
  }
  inMemoryAccessToken = token;
}

export function getAccessToken(): string | null {
  return inMemoryAccessToken;
}

export function onSessionExpired(callback: () => void): void {
  sessionExpiredCallback = callback;
}

/**
 * Read readable CSRF token cookie set by backend.
 */
function getCsrfTokenFromCookie(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp("(^|;\\s*)csrf_token=([^;]*)"));
  return match ? decodeURIComponent(match[2]) : null;
}

export interface ApiRequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | null | undefined>;
  skipAuthRefresh?: boolean;
  timeoutMs?: number;
  bearerTokenOverride?: string; // For explicit external non-browser client use
  skipCache?: boolean;
  forceFresh?: boolean;
  cacheTtlMs?: number;
}

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, message: string, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

/**
 * Execute typed API request against FastAPI backend with request deduplication and in-memory SWR cache.
 */
export async function apiClient<T>(endpoint: string, options: ApiRequestOptions = {}): Promise<T> {
  const method = (options.method || "GET").toUpperCase();
  const isGet = method === "GET";
  const shouldDedupeAndCache = isGet && !options.skipCache && !options.forceFresh;

  const authKey = options.bearerTokenOverride || inMemoryAccessToken || "anon";
  const cacheKey = `${endpoint}::${JSON.stringify(options.params || {})}::${authKey}`;

  if (shouldDedupeAndCache) {
    const cached = responseMemoryCache.get(cacheKey);
    if (cached && cached.expiresAt > Date.now()) {
      return cached.data as T;
    }
    const inFlight = inFlightGetRequests.get(cacheKey);
    if (inFlight) {
      return inFlight as Promise<T>;
    }
  }

  const executeRequest = async (): Promise<T> => {
    const {
      params,
      headers: customHeaders,
      skipAuthRefresh,
      timeoutMs = 15000,
      bearerTokenOverride,
      signal: userSignal,
      ...fetchOptions
    } = options;

    let url = `${API_BASE}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

    // Attach query parameters
    if (params) {
      const searchParams = new URLSearchParams();
      for (const [key, val] of Object.entries(params)) {
        if (val !== undefined && val !== null && val !== "") {
          searchParams.append(key, String(val));
        }
      }
      const queryString = searchParams.toString();
      if (queryString) {
        url += (url.includes("?") ? "&" : "?") + queryString;
      }
    }

    // Build request headers
    const headers = new Headers(customHeaders);
    if (!headers.has("Content-Type") && !(fetchOptions.body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
    }

    // Authorization: prioritize override, then in-memory token
    const tokenToUse = bearerTokenOverride || inMemoryAccessToken;
    if (tokenToUse && !headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${tokenToUse}`);
    }

    // Attach CSRF token on mutating requests
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
      const csrf = getCsrfTokenFromCookie();
      if (csrf && !headers.has("X-CSRF-Token")) {
        headers.set("X-CSRF-Token", csrf);
      }
    }

    // Set up timeout controller
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    // Link user signal if provided
    if (userSignal) {
      userSignal.addEventListener("abort", () => controller.abort());
    }

    let response: Response;
    try {
      response = await fetch(url, {
        ...fetchOptions,
        headers,
        credentials: "include", // Strictly send HttpOnly refresh_token and cookies
        signal: controller.signal,
      });
    } catch (err: unknown) {
      clearTimeout(timeoutId);
      if (err instanceof Error && err.name === "AbortError") {
        throw new ApiError(408, `Request timeout: Backend did not respond within ${timeoutMs / 1000}s`);
      }
      throw new ApiError(0, "Network error: Unable to connect to Maatram API backend.", err);
    } finally {
      clearTimeout(timeoutId);
    }

    // Handle 401 Unauthorized with single-flight silent token rotation
    if (response.status === 401 && !skipAuthRefresh) {
      const newAccessToken = await attemptTokenRefresh();
      if (newAccessToken) {
        headers.set("Authorization", `Bearer ${newAccessToken}`);
        return apiClient<T>(endpoint, {
          ...options,
          skipAuthRefresh: true,
        });
      } else {
        // Session expired completely
        if (sessionExpiredCallback) {
          sessionExpiredCallback();
        }
      }
    }

    if (!response.ok) {
      let errorData: unknown;
      try {
        errorData = await response.json();
      } catch {
        errorData = await response.text();
      }
      const message =
        typeof errorData === "object" && errorData && "message" in errorData
          ? String((errorData as { message: unknown }).message)
          : `Request failed with status ${response.status}`;

      throw new ApiError(response.status, message, errorData);
    }

    // 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return (await response.json()) as T;
  };

  if (shouldDedupeAndCache) {
    const promise = executeRequest()
      .then((data) => {
        const defaultTtl =
          endpoint.includes("/users/me") ? 15000 :
          endpoint.includes("/unread-count") ? 15000 :
          endpoint.includes("/volunteers/me") ? 30000 :
          endpoint.includes("/consent/me") ? 30000 :
          endpoint.includes("/summary") ? 20000 :
          endpoint.includes("/achievements") ? 60000 : 10000;
        const ttlMs = options.cacheTtlMs ?? defaultTtl;
        responseMemoryCache.set(cacheKey, { data, expiresAt: Date.now() + ttlMs });
        return data;
      })
      .finally(() => {
        inFlightGetRequests.delete(cacheKey);
      });

    inFlightGetRequests.set(cacheKey, promise);
    return promise;
  }

  const result = await executeRequest();
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    invalidateCacheForMutation(endpoint);
  }
  return result;
}

/**
 * Handle concurrent 401s with single-flight deduplicated refresh promise.
 */
async function attemptTokenRefresh(): Promise<string | null> {
  if (tokenRefreshPromise) {
    return tokenRefreshPromise;
  }

  tokenRefreshPromise = (async () => {
    try {
      const csrf = getCsrfTokenFromCookie();
      const refreshHeaders: Record<string, string> = { "Content-Type": "application/json" };
      if (csrf) {
        refreshHeaders["X-CSRF-Token"] = csrf;
      }
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: refreshHeaders,
        credentials: "include", // Browser automatically transmits HttpOnly refresh_token cookie
      });
      if (res.ok) {
        const data = await res.json();
        setAccessToken(data.access_token);
        return data.access_token as string;
      }
    } catch {
      // Refresh failed or network offline
    } finally {
      tokenRefreshPromise = null;
    }
    setAccessToken(null);
    return null;
  })();

  return tokenRefreshPromise;
}

/**
 * Stream binary files (e.g. Excel .xlsx reports) with auto-triggered browser download.
 */
export async function apiDownload(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<{ blob: Blob; filename: string }> {
  const { headers: customHeaders, timeoutMs = 30000, ...fetchOptions } = options;

  const url = `${API_BASE}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const headers = new Headers(customHeaders);
  if (inMemoryAccessToken && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${inMemoryAccessToken}`);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
      credentials: "include",
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new ApiError(response.status, `Download failed with status ${response.status}`);
    }

    // Extract filename from Content-Disposition header if available
    let filename = "download.xlsx";
    const disposition = response.headers.get("Content-Disposition");
    if (disposition && disposition.includes("filename=")) {
      const match = disposition.match(/filename="?([^";]+)"?/);
      if (match && match[1]) {
        filename = match[1];
      }
    }

    const blob = await response.blob();
    return { blob, filename };
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Multipart file upload for Cloudinary direct uploads or evidence documents.
 */
export async function apiUpload<T>(
  endpoint: string,
  formData: FormData,
  options: ApiRequestOptions = {}
): Promise<T> {
  return apiClient<T>(endpoint, {
    ...options,
    method: "POST",
    body: formData,
    // Note: Do not set Content-Type header so browser populates boundary
  });
}

// Convenience methods on apiClient
apiClient.get = function <T>(endpoint: string, options: ApiRequestOptions = {}): Promise<{ data: T }> {
  return apiClient<T>(endpoint, { ...options, method: "GET" }).then((data) => ({ data }));
};

apiClient.post = function <T>(endpoint: string, body?: unknown, options: ApiRequestOptions = {}): Promise<{ data: T }> {
  return apiClient<T>(endpoint, {
    ...options,
    method: "POST",
    body: body !== undefined ? JSON.stringify(body) : undefined,
    headers: {
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  }).then((data) => ({ data }));
};

apiClient.patch = function <T>(endpoint: string, body?: unknown, options: ApiRequestOptions = {}): Promise<{ data: T }> {
  return apiClient<T>(endpoint, {
    ...options,
    method: "PATCH",
    body: body !== undefined ? JSON.stringify(body) : undefined,
    headers: {
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  }).then((data) => ({ data }));
};

apiClient.delete = function <T>(endpoint: string, options: ApiRequestOptions = {}): Promise<{ data: T }> {
  return apiClient<T>(endpoint, { ...options, method: "DELETE" }).then((data) => ({ data }));
};

apiClient.download = function (endpoint: string, options: ApiRequestOptions = {}): Promise<Response> {
  const url = `${API_BASE}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  return fetch(url, {
    ...options,
    credentials: "include",
    headers: {
      ...(inMemoryAccessToken ? { Authorization: `Bearer ${inMemoryAccessToken}` } : {}),
      ...options.headers,
    },
  });
};

