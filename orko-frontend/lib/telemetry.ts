// frontend/lib/telemetry.ts

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export async function sendWebVital(metric: {
  name: string;
  value: number;
  id?: string;
  label?: string;
  path: string;
}) {
  try {
    await fetch(`${API_BASE}/api/telemetry/web-vitals`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        metric_type: "web_vital",
        name: metric.name,
        value: metric.value,
        id: metric.id ?? null,
        label: metric.label ?? null,
        path: metric.path,
        timestamp_ms: Date.now(),
      }),
      keepalive: true,
    });
  } catch (err) {
    console.warn("web-vitals telemetry failed", err);
  }
}

export async function sendApiLatency(metric: {
  endpoint: string;
  durationMs: number;
  path: string;
  success: boolean;
}) {
  try {
    await fetch(`${API_BASE}/api/telemetry/api-latency`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        metric_type: "api_latency",
        endpoint: metric.endpoint,
        duration_ms: metric.durationMs,
        path: metric.path,
        success: metric.success,
        timestamp_ms: Date.now(),
      }),
      keepalive: true,
    });
  } catch (err) {
    console.warn("api latency telemetry failed", err);
  }
}
