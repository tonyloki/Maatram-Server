# MAATRAM VOLUNTEERING & GAMIFICATION PORTAL
## Loading Experience & Network Reliability Architecture Report

**Date**: November 15, 2026  
**Status**: APPROVED & IMPLEMENTED  
**Scope**: Web Frontend (Next.js), Mobile App (Flutter), and Backend Interaction Layer

---

## 1. Core Principles of Loading Experience

The Maatram Portal and Mobile Application follow strict principles to guarantee that users experience smooth, predictable, and resilient state handling regardless of network fluctuations:

1. **No Arbitrary Failure Timers**:
   - The UI never surfaces an error state merely because an arbitrary 5-second or 10-second timer elapsed.
   - Requests are given the full, agreed-upon operational budget (30s for standard operations, 60s for report generation or large file uploads) before timing out.

2. **Persistent Visual Continuity**:
   - Active loaders, spinners, or skeletons remain visible as long as an HTTP request is in-flight.
   - Refreshes do not wipe existing page data; previously loaded information remains displayed while fresh background requests resolve (Stale-While-Revalidate).

3. **Multi-Stage Progressive Loading**:
   - Initial page loads render lightweight skeleton screens (`Skeleton`, `AdminDashboardSkeleton`, `EventCardSkeleton`, `ProfileSkeleton`).
   - Independent data components (e.g., Volunteer KPI metrics vs. Activity Feeds) resolve independently, avoiding blocking waterfalls.

4. **Slow Connection Transparency**:
   - When requests remain pending past 5,000ms, the system transitions to an informative "slow connection" state rather than failing.
   - Users are reassured that their request is still processing.

5. **Safe Idempotent Retries**:
   - Bounded exponential backoff with jitter is applied exclusively to read-only `GET` operations.
   - Mutating actions (`POST`, `PUT`, `PATCH`, `DELETE`) are never automatically retried, guarding against accidental double-submissions, duplicate registrations, and race conditions.

---

## 2. Web Frontend Implementation Details

### 2.1 Configurable API Client (`web/src/lib/api-client.ts`)
The unified `apiClient` enforces:
- **`DEFAULT_TIMEOUT_MS = 30000`**: Configurable via `NEXT_PUBLIC_API_TIMEOUT_MS`.
- **`DEFAULT_UPLOAD_TIMEOUT_MS = 60000`**: Configurable via `NEXT_PUBLIC_API_UPLOAD_TIMEOUT_MS`.
- **`SLOW_CONNECTION_THRESHOLD_MS = 5000`**: Configurable via `NEXT_PUBLIC_API_SLOW_WARNING_MS`.

### 2.2 Slow Connection Detection Hook
```typescript
import { useState, useEffect } from "react";
import { onSlowConnectionChange } from "@/lib/api-client";

export function useSlowConnection() {
  const [isSlow, setIsSlow] = useState(false);
  const [slowCount, setSlowCount] = useState(0);

  useEffect(() => {
    return onSlowConnectionChange((slow, count) => {
      setIsSlow(slow);
      setSlowCount(count);
    });
  }, []);

  return { isSlow, slowCount };
}
```

### 2.3 Bounded Exponential Backoff on GET Requests
```typescript
for (let attempt = 0; attempt <= maxRetries; attempt++) {
  try {
    return await executeSingleAttempt();
  } catch (err: unknown) {
    lastError = err;
    if (attempt < maxRetries && isRetryableError(err)) {
      // 1000ms * 2^attempt + jitter (0-300ms)
      const backoffDelay = Math.min(1000 * Math.pow(2, attempt) + Math.random() * 300, 5000);
      await new Promise((res) => setTimeout(res, backoffDelay));
      continue;
    }
    throw lastError;
  }
}
```

---

## 3. Flutter Mobile Implementation Details

### 3.1 Dio Client Configuration (`mobile/lib/core/network/api_client.dart`)
- **Connection Timeout**: 10 seconds (`connectTimeout = Duration(seconds: 10)`)
- **Receive Timeout**: 30 seconds (`receiveTimeout = Duration(seconds: 30)`)
- **Automatic Retry**:
  ```dart
  Future<Response<T>> get<T>(String path, {int maxRetries = 2}) async {
    int attempts = 0;
    while (true) {
      try {
        return await dio.get<T>(path);
      } on DioException catch (e) {
        attempts++;
        final isRetryable = attempts <= maxRetries &&
            (e.type == DioExceptionType.connectionTimeout ||
             e.type == DioExceptionType.receiveTimeout ||
             e.type == DioExceptionType.connectionError ||
             e.response?.statusCode == 408 ||
             e.response?.statusCode == 503 ||
             e.response?.statusCode == 504);
        if (isRetryable) {
          await Future.delayed(Duration(milliseconds: 1000 * attempts));
          continue;
        }
        throw _parseDioError(e);
      }
    }
  }
  ```

---

## 4. Manual Retry & Error Recovery

When requests fail due to non-retryable causes (e.g., complete network loss, unresolvable server 500 error):
1. The error boundary catches the exception and renders an `EmptyState` or `ErrorCard` with explicit user context.
2. A clear, high-contrast **"Try Again"** button allows the user to re-invoke the failed operation without refreshing the entire web page or restarting the mobile app.
3. Form states and input field values are preserved in memory so user input is never lost upon error recovery.

