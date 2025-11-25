// frontend/lib/api.ts
import { sendApiLatency } from "./telemetry";

export async function fetchJson<T>(endpoint: string): Promise<T> {
  const path = typeof window !== "undefined" ? window.location.pathname : "/";
  const start = performance.now();

  let success = true;

  try {
    const res = await fetch(endpoint, {
      credentials: "include",
    });

    if (!res.ok) {
      success = false;
      throw new Error(`Request failed with ${res.status}`);
    }

    return (await res.json()) as T;

  } finally {
    const durationMs = performance.now() - start;

    // Fire-and-forget telemetry
    sendApiLatency({
      endpoint,
      durationMs,
      path,
      success,
    });
  }
}
