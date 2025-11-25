"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    document.cookie = `orko_auth=true; path=/`;
    router.push("/dashboard");
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-orko-bg text-orko-text">
      <form
        onSubmit={handleSubmit}
        className="bg-orko-surface p-8 rounded-card w-80 shadow-lg border border-white/5"
      >
        <h1 className="text-2xl font-semibold mb-6 text-center text-white">
          Welcome to ORKO ⚡
        </h1>

        <input
          type="email"
          placeholder="Email"
          className="w-full mb-4 p-2 rounded-chip bg-orko-card text-white placeholder-orko-muted border border-white/10 focus:ring-2 focus:ring-orko-accentStart focus:outline-none"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full mb-6 p-2 rounded-chip bg-orko-card text-white placeholder-orko-muted border border-white/10 focus:ring-2 focus:ring-orko-accentEnd focus:outline-none"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          className="w-full py-2 rounded-chip bg-gradient-to-r from-orko-accentStart to-orko-accentEnd text-white font-semibold hover:opacity-90 transition"
        >
          Sign In
        </button>
      </form>
    </main>
  );
}
