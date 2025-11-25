// frontend/components/TelemetryClient.tsx
"use client";

import { useEffect } from "react";
import { sendWebVital } from "../lib/telemetry";

export function TelemetryClient() {
  useEffect(() => {
    // Dynamically import web-vitals only in the browser
    import("web-vitals").then(({ onCLS, onLCP, onINP }) => {
      const path = window.location.pathname;

      const handler = (metric: any) => {
        sendWebVital({
          name: metric.name,
          value: metric.value,
          id: metric.id,
          label: metric.rating,
          path,
        });
      };

      onLCP(handler);
      onCLS(handler);
      onINP(handler);
    });
  }, []);

  // This component renders nothing visible.
  return null;
}
