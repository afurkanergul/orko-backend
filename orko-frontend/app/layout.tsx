import "./globals.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";

import { TelemetryClient } from "../components/TelemetryClient";
import { ClientSWRProvider } from "../components/ClientSWRProvider"; // ✅ NEW

export const metadata = {
  title: "ORKO Dashboard",
  description: "ORKO AI Control Center",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-[var(--orko-bg)] text-[var(--orko-text)] antialiased">

        {/* 🔥 Telemetry always runs */}
        <TelemetryClient />

        {/* 🔥 Global SWR refresh 10 min WITHOUT converting layout into client component */}
        <ClientSWRProvider>
          <div className="max-w-[1400px] mx-auto px-8 py-10">
            {children}
          </div>
        </ClientSWRProvider>

      </body>
    </html>
  );
}
