"use client";

import React from "react";
import useSWR from "swr";
import axios from "axios";

// =======================================
// Backend API Base URL + Axios Fetcher
// =======================================
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const axiosFetcher = async <T,>(url: string): Promise<T> => {
  const fullUrl = url.startsWith("http") ? url : `${API_BASE_URL}${url}`;
  const response = await axios.get<T>(fullUrl, {
    timeout: 5000, // Safe timeout
  });
  return response.data;
};

// =======================================
// Dashboard TypeScript Shapes
// =======================================

type BrainMetric = {
  label: string;
  value: number;
  delta: number;
  direction: "up" | "down";
};

type ActivityItem = {
  id: string;
  title: string;
  description: string;
  timeAgo: string;
  brain: "knowledge" | "pattern" | "skill" | "system";
};

type TipItem = {
  id: string;
  title: string;
  text: string;
};

type DashboardResponse = {
  knowledge: BrainMetric;
  pattern: BrainMetric;
  skill: BrainMetric;
  recentActivity: ActivityItem[];
  tips: TipItem[];
};

type JournalEntry = {
  id: string;
  title: string;
  summary: string;
  brain: "knowledge" | "pattern" | "skill";
  timestamp: string;
  sourceLabel: string;
};

type JournalSidebar = {
  totalEntries: number;
  totalThisWeek: number;
  bookmarks: {
    id: string;
    title: string;
    savedLabel: string;
  }[];
  quickFilters: {
    id: string;
    title: string;
    countLabel: string;
  }[];
};

type JournalResponse = {
  entries: JournalEntry[];
  sidebar: JournalSidebar;
};

// =======================================
// SWR Global Options
// =======================================
const swrOptions = {
  revalidateOnFocus: false,
  revalidateOnReconnect: true,
  dedupingInterval: 10 * 60 * 1000, // 10 minutes
};

// =======================================
// EXISTING UI — KEEP AS IS FOR NOW
// =======================================
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center">
      <h1 className="text-4xl font-bold bg-gradient-to-r from-[var(--orko-accent-start)] to-[var(--orko-accent-end)] bg-clip-text text-transparent">
        ORKO is alive ⚡
      </h1>
      <p className="mt-4 text-[color:var(--orko-muted)]">
        Frontend scaffold ready for Sub-Step 2 (Routing & Layout)
      </p>
    </main>
  );
}
