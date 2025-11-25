"use client";

import { SWRConfig } from "swr";
import { fetchJson } from "../lib/api";

export function ClientSWRProvider({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        fetcher: (url: string) => fetchJson(url),
        refreshInterval: 10 * 60 * 1000, // 10 minutes
        revalidateOnFocus: true,
      }}
    >
      {children}
    </SWRConfig>
  );
}
