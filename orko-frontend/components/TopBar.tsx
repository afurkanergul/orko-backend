"use client";
import { useRouter } from "next/navigation";

export default function TopBar() {
  const router = useRouter();

  function handleLogout() {
    document.cookie = "orko_auth=; Max-Age=0; path=/";
    router.push("/login");
  }

  return (
    <header className="flex items-center justify-between h-14 px-6 border-b border-white/10 bg-gradient-to-r from-orko-accentStart to-orko-accentEnd">
      <h1 className="font-bold text-white tracking-wide text-lg">
        ORKO AI Dashboard
      </h1>

      <nav className="space-x-4 text-sm text-white/90">
        <a href="/dashboard" className="hover:text-white transition">
          Dashboard
        </a>
        <button
          onClick={handleLogout}
          className="hover:text-white transition"
        >
          Logout
        </button>
      </nav>
    </header>
  );
}
