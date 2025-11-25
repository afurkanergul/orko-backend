"use client";

import * as React from "react";
import useSWR, { mutate } from "swr";
import axios from "axios";

import { TelemetryClient } from "../../components/TelemetryClient";

// ------------------------------------------------------
// CHART.JS (Sparkline)
// ------------------------------------------------------
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip as ChartTooltip,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ChartTooltip,
  Filler
);

// ------------------------------------------------------
// API CONFIG + TYPES
// ------------------------------------------------------
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

import { sendApiLatency } from "../../lib/telemetry";

const axiosFetcher = async <T,>(url: string): Promise<T> => {
  const path = typeof window !== "undefined" ? window.location.pathname : "/";
  const fullUrl = url.startsWith("http") ? url : `${API_BASE_URL}${url}`;

  const start = performance.now();
  let success = true;

  try {
    const res = await axios.get<T>(fullUrl);
    return res.data;
  } catch (err) {
    success = false;
    throw err;
  } finally {
    const durationMs = performance.now() - start;

    sendApiLatency({
      endpoint: url,
      durationMs,
      path,
      success,
    });
  }
};

type BrainKey = "knowledge" | "pattern" | "skill";
type UserRole = "admin" | "user";

type OverviewApiResponse = {
  brains: {
    knowledge: { kpi: number; delta: string };
    pattern: { kpi: number; delta: string };
    skill: { kpi: number; delta: string };
  };
  recentActivity?: {
    id: string;
    title: string;
    desc: string;
    timeAgo: string;
    tag: "Knowledge" | "Pattern" | "Skill" | "System";
  }[];
};

// ------------------------------------------------------
// CARD METRICS
// ------------------------------------------------------
type BrainMetric = {
  value: number;
  delta: number;
  history: number[];
};

// ------------------------------------------------------
// JOURNAL TYPES
// ------------------------------------------------------
type JournalEntry = {
  id: string;
  title: string;
  summary: string;
  brain: "knowledge" | "pattern" | "skill";
  timestamp: string;
  sourceLabel: string;
};

type JournalBookmark = {
  id: string;
  title: string;
  dateLabel: string;
};

type JournalQuickFilter = {
  id: string;
  title: string;
  countLabel: string;
};

// ------------------------------------------------------
// STATIC MOCK DATA
// ------------------------------------------------------
const RECENT_ACTIVITY = [
  {
    id: "a1",
    title: "Knowledge Brain updated dataset",
    desc: "Processed 1,247 new data points.",
    timeAgo: "2 min ago",
    tag: "Knowledge" as const,
  },
  {
    id: "a2",
    title: "Pattern Brain detected anomaly",
    desc: "Detected unusual engagement pattern.",
    timeAgo: "18 min ago",
    tag: "Pattern" as const,
  },
  {
    id: "a3",
    title: "Skill Brain training cycle completed",
    desc: "Accuracy improved by 3.2%.",
    timeAgo: "1 hour ago",
    tag: "Skill" as const,
  },
  {
    id: "a4",
    title: "System health check passed",
    desc: "All systems operating normally.",
    timeAgo: "3 hours ago",
    tag: "System" as const,
  },
];

// ------------------------------------------------------
// JOURNAL STATIC DATA
// ------------------------------------------------------
const JOURNAL_ENTRIES: JournalEntry[] = [
  {
    id: "j1",
    title: "Enhanced Natural Language Processing Capabilities",
    summary:
      "Implemented advanced NLP algorithms that improved context understanding by 23%.",
    brain: "knowledge",
    timestamp: "Today, 10:24 AM",
    sourceLabel: "Data from: /api/journal",
  },
  {
    id: "j2",
    title: "User Behavior Pattern Recognition Breakthrough",
    summary:
      "Pattern Brain identified recurring interaction sequences that predict engagement.",
    brain: "pattern",
    timestamp: "Yesterday, 3:45 PM",
    sourceLabel: "Data from: /api/journal",
  },
  {
    id: "j3",
    title: "Automated Task Execution Optimization",
    summary:
      "Skill Brain refined algorithms, reducing completion time by 18%.",
    brain: "skill",
    timestamp: "Yesterday, 11:20 AM",
    sourceLabel: "Data from: /api/journal",
  },
  {
    id: "j4",
    title: "Cross-Brain Collaboration Framework",
    summary:
      "New communication protocols allow the three brains to share insights in real time.",
    brain: "knowledge",
    timestamp: "2 days ago, 9:15 AM",
    sourceLabel: "Data from: /api/journal",
  },
];

const JOURNAL_BOOKMARKS: JournalBookmark[] = [
  { id: "b1", title: "NLP Processing Milestone", dateLabel: "Saved 2 days ago" },
  { id: "b2", title: "Pattern Recognition Framework", dateLabel: "Saved 5 days ago" },
];

const JOURNAL_QUICK_FILTERS: JournalQuickFilter[] = [
  { id: "q1", title: "High Priority Entries", countLabel: "12 entries" },
  { id: "q2", title: "Recent Breakthroughs", countLabel: "8 entries" },
  { id: "q3", title: "System Optimizations", countLabel: "15 entries" },
];

const JOURNAL_STATS = {
  totalEntries: 247,
  thisWeek: 18,
};

// ------------------------------------------------------
// UI HELPERS
// ------------------------------------------------------
const BrainIcon = ({ emoji }: { emoji: string }) => (
  <div className="w-12 h-12 rounded-[12px] bg-gradient-to-tr from-[var(--orko-accent-start)] to-[var(--orko-accent-end)] flex items-center justify-center text-2xl text-white mb-4">
    {emoji}
  </div>
);

const TopTabButton = ({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
}) => (
  <button
    onClick={onClick}
    className={`relative px-0 pb-3 text-sm font-semibold transition-colors ${
      active ? "text-[#1A1A2E]" : "text-[var(--orko-muted)]"
    }`}
  >
    {children}
    <span
      className={`absolute left-0 right-0 -bottom-[2px] h-[2px] rounded-full bg-gradient-to-r from-[var(--orko-accent-start)] to-[var(--orko-accent-end)] ${
        active ? "opacity-100" : "opacity-0"
      }`}
    />
  </button>
);

// ------------------------------------------------------
// SPARKLINE BUILDER
// ------------------------------------------------------
const makeSparklineConfig = (data: number[]) => ({
  data: {
    labels: data.map((_, i) => i),
    datasets: [
      {
        data,
        borderColor: "#ffffff",
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        backgroundColor: "rgba(255,255,255,0.2)",
        pointRadius: 0,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { x: { display: false }, y: { display: false } },
  },
});

// ------------------------------------------------------
// BRAIN CARD
// ------------------------------------------------------
const BrainCard = ({
  title,
  icon,
  metric,
  loading,
  gradientFrom,
  gradientTo,
}: {
  title: string;
  icon: string;
  metric?: BrainMetric;
  loading: boolean;
  gradientFrom: string;
  gradientTo: string;
}) => {
  const sparkData = metric?.history ?? [0, 0, 0, 0, 0];
  const config = makeSparklineConfig(sparkData);
  const isNegative = metric ? metric.delta < 0 : false;

  return (
    <div
      className="rounded-[20px] p-6 text-white shadow-lg"
      style={{ background: `linear-gradient(135deg, ${gradientFrom}, ${gradientTo})` }}
    >
      <div className="flex justify-between items-start">
        <div>
          <div className="text-[32px]">{icon}</div>
          <div className="text-sm opacity-80 uppercase tracking-wide">{title}</div>

          {loading || !metric ? (
            <div className="mt-3 animate-pulse">
              <div className="h-7 w-20 bg-white/30 rounded mb-2" />
              <div className="h-4 w-14 bg-white/30 rounded" />
            </div>
          ) : (
            <>
              <div className="text-[34px] font-bold mt-2">
                {metric.value.toLocaleString()}
              </div>
              <div
                className={`text-sm font-semibold ${
                  isNegative ? "text-red-200" : "text-green-200"
                }`}
              >
                {isNegative ? "↓" : "↑"} {metric.delta.toFixed(1)}%
              </div>
            </>
          )}
        </div>
      </div>

      <div className="mt-5 h-16">
        <Line {...config} />
      </div>
    </div>
  );
};

// ------------------------------------------------------
// NO ACCESS CARD
// ------------------------------------------------------
function NoAccess({ message }: { message: string }) {
  return (
    <div className="bg-white border border-[#E5E7EB] rounded-[12px] p-6 shadow-sm text-center text-[#6B7280]">
      <div className="text-[32px] mb-3">🔒</div>
      <div className="text-[14px] leading-relaxed">{message}</div>
    </div>
  );
}

// ------------------------------------------------------
// ERROR CARD
// ------------------------------------------------------
function ErrorCard({ message }: { message: string }) {
  return (
    <div className="bg-white border border-[#F0F3F8] rounded-[16px] p-6 shadow-sm text-center">
      <div className="text-[24px] mb-2">⚠️</div>
      <div className="text-[14px] text-[#6B7280]">{message}</div>
    </div>
  );
}

// ------------------------------------------------------
// EVENT MODAL  (Mobile spacing updated)
// ------------------------------------------------------
type ActivityItem = {
  id: string;
  title: string;
  description: string;
  timeAgo: string;
  brain: "knowledge" | "pattern" | "skill" | "system";
};

function EventDetailsModal({
  event,
  onClose,
}: {
  event: ActivityItem | null;
  onClose: () => void;
}) {
  if (!event) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex justify-center items-center z-50">
      <div className="bg-white w-[90%] max-w-[480px] rounded-[16px] p-4 md:p-6 shadow-xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-[18px] font-bold text-[#1A1A2E]">Event Details</h2>
          <button
            className="text-[20px] text-[#6B7280] hover:text-black"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <div className="space-y-3 text-[14px] text-[#6B7280]">
          <p>
            <strong>Title:</strong> {event.title}
          </p>
          <p>
            <strong>Description:</strong> {event.description}
          </p>
          <p>
            <strong>Timestamp:</strong> {event.timeAgo}
          </p>
          <p>
            <strong>Type:</strong> {event.brain}
          </p>
        </div>

        <div className="mt-6 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-[10px] bg-[#6A5AE0] text-white hover:bg-[#5A4FD0]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
// ------------------------------------------------------
// TIMELINE EVENT COMPONENT
// ------------------------------------------------------
type TimelineEventProps = {
  event: ActivityItem;
  setSelectedEvent: (e: ActivityItem) => void;
  approvedEvents: string[];
  setApprovedEvents: React.Dispatch<React.SetStateAction<string[]>>;
  userRole: UserRole;
};

function TimelineEvent({
  event,
  setSelectedEvent,
  approvedEvents,
  setApprovedEvents,
  userRole,
}: TimelineEventProps) {
  const colors = {
    knowledge: { from: "#6A5AE0", to: "#00B3FF" },
    pattern: { from: "#FF7EB3", to: "#FF758C" },
    skill: { from: "#00C6A7", to: "#1E3C72" },
    system: { from: "#6B7280", to: "#9CA3AF" },
  }[event.brain];

  const isApproved = approvedEvents.includes(event.id);

  const handleApprove = () => {
    setApprovedEvents((prev) =>
      prev.includes(event.id) ? prev : [...prev, event.id]
    );
  };

  return (
    <div className="relative pl-10 pb-10">
      <div className="absolute left-[12px] top-0 bottom-0 w-[2px] bg-[#E5E7EB]" />

      <div
        className="absolute left-[4px] top-[4px] w-4 h-4 rounded-full"
        style={{ background: `linear-gradient(135deg, ${colors.from}, ${colors.to})` }}
      />

      <div className="bg-white rounded-[16px] p-4 md:p-5 shadow-md border border-[#F0F3F8]">
        <div className="flex justify-between items-center mb-2">
          <div className="text-[15px] font-semibold text-[#1A1A2E]">
            {event.title}
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[12px] text-[#9CA3AF]">{event.timeAgo}</span>
            {isApproved && (
              <span className="text-[11px] text-green-600 font-semibold">
                ✓ Approved
              </span>
            )}
          </div>
        </div>

        <div className="text-[13px] text-[#6B7280] mb-4">{event.description}</div>

        {userRole === "admin" && (
          <div className="flex gap-3 mb-4">
            <button
              onClick={handleApprove}
              className="px-3 py-1 rounded-[8px] text-[12px] border bg-[#F9FAFB] hover:bg-[#E5E7EB]"
            >
              ✓ Approve
            </button>

            <button
              onClick={() => mutate("/api/dashboard")}
              className="px-3 py-1 rounded-[8px] text-[12px] border bg-[#F9FAFB] hover:bg-[#E5E7EB]"
            >
              ↻ Sync
            </button>

            <button
              onClick={() => setSelectedEvent(event)}
              className="px-3 py-1 rounded-[8px] text-[12px] border bg-[#F9FAFB] hover:bg-[#E5E7EB]"
            >
              → View
            </button>
          </div>
        )}

        <span className="inline-block px-3 py-1 rounded-[8px] text-[12px] bg-[#F0F3F8] text-[#6A5AE0]">
          {event.brain.toUpperCase()}
        </span>
      </div>
    </div>
  );
}

// ------------------------------------------------------
// OVERVIEW TAB
// ------------------------------------------------------
type OverviewTabProps = {
  overview: OverviewApiResponse;
  loading: boolean;
  timelineEvents: ActivityItem[];
  selectedEvent: ActivityItem | null;
  setSelectedEvent: (e: ActivityItem | null) => void;
  userRole: UserRole;
};

const OverviewTab: React.FC<OverviewTabProps> = ({
  overview,
  loading,
  timelineEvents,
  selectedEvent,
  setSelectedEvent,
  userRole,
}) => {
  const [timelineFilter, setTimelineFilter] = React.useState("All");
  const [approvedEvents, setApprovedEvents] = React.useState<string[]>([]);

  const filterOptions =
    userRole === "admin"
      ? ["All", "Knowledge", "Pattern", "Skill", "System"]
      : ["All", "Knowledge", "Pattern", "Skill"];

  const filteredTimeline =
    timelineFilter === "All"
      ? timelineEvents
      : timelineEvents.filter(
          (e) => e.brain.toLowerCase() === timelineFilter.toLowerCase()
        );

  const buildMetric = (kpi: number, delta: string): BrainMetric => ({
    value: kpi,
    delta: parseFloat(delta.replace("%", "").replace("+", "")),
    history: [kpi * 0.85, kpi * 0.9, kpi * 0.95, kpi * 0.97, kpi],
  });

  const brains =
    overview?.brains ??
    ({
      knowledge: { kpi: 0, delta: "0%" },
      pattern: { kpi: 0, delta: "0%" },
      skill: { kpi: 0, delta: "0%" },
    } as OverviewApiResponse["brains"]);

  const km = buildMetric(brains.knowledge?.kpi ?? 0, brains.knowledge?.delta ?? "0%");
  const pm = buildMetric(brains.pattern?.kpi ?? 0, brains.pattern?.delta ?? "0%");
  const sm = buildMetric(brains.skill?.kpi ?? 0, brains.skill?.delta ?? "0%");

  // ---------------------------
  // KPI SKELETONS
  // ---------------------------
  if (loading) {
    return (
      <>
        <div className="mb-6">
          <h1 className="text-[28px] font-bold">ORKO Overview</h1>
          <p className="text-[15px] text-[var(--orko-muted)]">
            Agentic AI Control Center
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-[#F3F4F6] rounded-[16px] h-[160px] animate-pulse"
            />
          ))}
        </div>
      </>
    );
  }

  return (
    <>
      <div className="mb-6">
        <h1 className="text-[28px] font-bold">ORKO Overview</h1>
        <p className="text-[15px] text-[var(--orko-muted)]">
          Agentic AI Control Center
        </p>
      </div>

      {/* KPI CARDS */}
      <div className="grid grid-cols-12 gap-6 mb-10">
        <div className="col-span-12 md:col-span-4">
          <BrainCard
            title="Knowledge Brain"
            icon="🧠"
            metric={km}
            loading={loading}
            gradientFrom="#6A5AE0"
            gradientTo="#00B3FF"
          />
        </div>
        <div className="col-span-12 md:col-span-4">
          <BrainCard
            title="Pattern Brain"
            icon="🔮"
            metric={pm}
            loading={loading}
            gradientFrom="#FF7EB3"
            gradientTo="#FF758C"
          />
        </div>
        <div className="col-span-12 md:col-span-4">
          <BrainCard
            title="Skill Brain"
            icon="⚡"
            metric={sm}
            loading={loading}
            gradientFrom="#00C6A7"
            gradientTo="#1E3C72"
          />
        </div>
      </div>

      {/* TIMELINE + TIPS */}
      <div className="grid grid-cols-12 gap-6 mb-8">
        {/* Timeline */}
        <div className="col-span-12 lg:col-span-7">
          <div className="bg-white rounded-[16px] p-4 md:p-6 shadow-md">
            <h2 className="text-[20px] font-semibold mb-1">🕒 Insights Timeline</h2>

            {userRole !== "admin" && (
              <div className="text-[12px] text-[#9CA3AF] mb-4">
                Limited view — only admins can take actions on insights.
              </div>
            )}

            <div className="flex gap-3 mb-6 flex-wrap">
              {filterOptions.map((label) => (
                <button
                  key={label}
                  onClick={() => setTimelineFilter(label)}
                  className={`px-4 py-2 rounded-[10px] text-sm border ${
                    timelineFilter === label
                      ? "bg-gradient-to-tr from-[#6A5AE0] to-[#00B3FF] text-white"
                      : "bg-white border-[#E5E7EB] text-[#6B7280]"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            {/* Timeline skeletons */}
            <div>
              {loading ? (
                <div className="space-y-6">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="h-[110px] bg-[#F3F4F6] rounded-[16px] animate-pulse"
                    />
                  ))}
                </div>
              ) : filteredTimeline.length === 0 ? (
                <ErrorCard message="No timeline events found." />
              ) : (
                filteredTimeline.map((event) => (
                  <TimelineEvent
                    key={event.id}
                    event={event}
                    setSelectedEvent={setSelectedEvent}
                    approvedEvents={approvedEvents}
                    setApprovedEvents={setApprovedEvents}
                    userRole={userRole}
                  />
                ))
              )}
            </div>
          </div>
        </div>

        {/* Quick Tips */}
        <div className="col-span-12 lg:col-span-5">
          <div className="bg-white rounded-[16px] p-4 md:p-6 shadow-md">
            <h2 className="text-[20px] font-semibold mb-4">💡 Quick Tips / Help</h2>

            <div className="space-y-3">
              <div className="flex gap-3 bg-[#F0F3F8] rounded-[12px] p-3">
                <div className="text-2xl">🎯</div>
                <div>
                  <div className="text-[14px] font-semibold text-[#1A1A2E]">
                    Monitor Your Brains
                  </div>
                  <div className="text-[13px] text-[#6B7280]">
                    Check KPI cards daily to track performance trends.
                  </div>
                </div>
              </div>

              <div className="flex gap-3 bg-[#F0F3F8] rounded-[12px] p-3">
                <div className="text-2xl">🔍</div>
                <div>
                  <div className="text-[14px] font-semibold text-[#1A1A2E]">
                    Use Filters Effectively
                  </div>
                  <div className="text-[13px] text-[#6B7280]">
                    Filter by brain type to focus on specific areas.
                  </div>
                </div>
              </div>

              <div className="flex gap-3 bg-[#F0F3F8] rounded-[12px] p-3">
                <div className="text-2xl">📈</div>
                <div>
                  <div className="text-[14px] font-semibold text-[#1A1A2E]">
                    Track Activity Patterns
                  </div>
                  <div className="text-[13px] text-[#6B7280]">
                    Review daily activity to find trends early.
                  </div>
                </div>
              </div>

              <div className="flex gap-3 bg-[#F0F3F8] rounded-[12px] p-3">
                <div className="text-2xl">⚙️</div>
                <div>
                  <div className="text-[14px] font-semibold text-[#1A1A2E]">
                    Optimize Performance
                  </div>
                  <div className="text-[13px] text-[#6B7280]">
                    Use the Learning Journal to refine coordination.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Admin mini stats */}
      {userRole === "admin" && (
        <div className="grid grid-cols-12 gap-6 mt-4">
          <div className="col-span-12 md:col-span-4">
            <div className="bg-white rounded-[16px] p-4 border border-[#E5E7EB] shadow-sm">
              <h3 className="text-[14px] font-semibold mb-2 text-[#1A1A2E]">
                System Diagnostics
              </h3>
              <p className="text-[13px] text-[#6B7280]">
                All pipelines healthy.
              </p>
            </div>
          </div>

          <div className="col-span-12 md:col-span-4">
            <div className="bg-white rounded-[16px] p-4 border border-[#E5E7EB] shadow-sm">
              <h3 className="text-[14px] font-semibold mb-2 text-[#1A1A2E]">
                Activity Depth
              </h3>
              <p className="text-[13px] text-[#6B7280]">
                Last 24hrs: <span className="font-semibold">57</span> events.
              </p>
            </div>
          </div>

          <div className="col-span-12 md:col-span-4">
            <div className="bg-white rounded-[16px] p-4 border border-[#E5E7EB] shadow-sm">
              <h3 className="text-[14px] font-semibold mb-2 text-[#1A1A2E]">
                Telemetry Summary
              </h3>
              <p className="text-[13px] text-[#6B7280]">
                Average response time: <span className="font-semibold">220ms</span>.
              </p>
            </div>
          </div>
        </div>
      )}

      <EventDetailsModal event={selectedEvent} onClose={() => setSelectedEvent(null)} />
    </>
  );
};

// ------------------------------------------------------
// LEARNING JOURNAL TAB
// ------------------------------------------------------
type LearningJournalTabProps = {
  userRole: UserRole;
  journalLoading?: boolean;
};

const LearningJournalTab: React.FC<LearningJournalTabProps> = ({
  userRole,
  journalLoading = false,
}) => {
  const [activeFilter, setActiveFilter] =
    React.useState<"all" | "knowledge" | "pattern" | "skill">("all");

  const filteredEntries =
    activeFilter === "all"
      ? JOURNAL_ENTRIES
      : JOURNAL_ENTRIES.filter((e) => e.brain === activeFilter);

  return (
    <div className="text-[#6B7280]">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-[28px] font-bold text-[#1A1A2E]">Learning Journal</h1>
        <p className="text-[15px] text-[var(--orko-muted)]">
          Insights from Knowledge, Pattern & Skill Brains
        </p>
      </div>

      {/* Filter Chips */}
      <div className="flex flex-wrap gap-3 mb-8">
        {[
          { key: "all", label: "All" },
          { key: "knowledge", label: "Knowledge" },
          { key: "pattern", label: "Pattern" },
          { key: "skill", label: "Skill" },
        ].map((chip) => (
          <button
            key={chip.key}
            onClick={() => setActiveFilter(chip.key as any)}
            className={`px-5 py-2 rounded-[12px] text-[14px] font-semibold border-2 transition-all ${
              activeFilter === chip.key
                ? "bg-gradient-to-tr from-[#6A5AE0] to-[#00B3FF] text-white border-[#6A5AE0]"
                : "bg-white border-[#E5E7EB] text-[#6B7280]"
            }`}
          >
            {chip.label}
          </button>
        ))}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left: entries */}
        <div className="col-span-12 lg:col-span-7 space-y-4">
          {journalLoading ? (
            <div className="space-y-6">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-[140px] bg-[#F3F4F6] rounded-[16px] animate-pulse"
                />
              ))}
            </div>
          ) : (
            <>
              {(filteredEntries ?? []).map((entry) => (
                <article
                  key={entry.id}
                  className="bg-white rounded-[16px] p-4 md:p-5 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="text-[16px] font-semibold text-[#1A1A2E] mb-1">
                        {entry.title}
                      </h3>
                    </div>
                    <span className="text-[12px] text-[#9CA3AF] whitespace-nowrap">
                      {entry.timestamp}
                    </span>
                  </div>

                  <p className="text-[14px] text-[#6B7280] leading-relaxed mb-3">
                    {entry.summary}
                  </p>

                  <div className="flex justify-between items-center">
                    <span
                      className={[
                        "inline-flex px-3 py-1 rounded-[8px] text-[12px] font-semibold",
                        entry.brain === "knowledge" && "bg-[#DBEAFE] text-[#1E40AF]",
                        entry.brain === "pattern" && "bg-[#FCE7F3] text-[#BE185D]",
                        entry.brain === "skill" && "bg-[#D1FAE5] text-[#065F46]",
                      ]
                        .filter(Boolean)
                        .join(" ")}
                    >
                      {entry.brain === "knowledge" && "Knowledge"}
                      {entry.brain === "pattern" && "Pattern"}
                      {entry.brain === "skill" && "Skill"}
                    </span>

                    <span className="text-[11px] text-[#9CA3AF] italic">
                      {entry.sourceLabel}
                    </span>
                  </div>
                </article>
              ))}

              {filteredEntries.length === 0 && (
                <NoAccess message="No journal entries match this filter yet. Try another brain or check back after ORKO completes more learning cycles." />
              )}
            </>
          )}
        </div>

        {/* Right: sidebar */}
        <div className="col-span-12 lg:col-span-5 space-y-4">
          {/* Bookmarks */}
          <div className="bg-white rounded-[16px] p-4 md:p-5 shadow-md">
            <h3 className="text-[16px] font-semibold text-[#1A1A2E] mb-4">
              📌 Bookmarked Insights
            </h3>
            <div className="space-y-3">
              {JOURNAL_BOOKMARKS.map((b) => (
                <div
                  key={b.id}
                  className="bg-[#F0F3F8] rounded-[10px] px-4 py-3 hover:bg-[#E5E7EB] cursor-pointer transition-all"
                >
                  <div className="text-[13px] font-semibold text-[#1A1A2E] mb-1">
                    {b.title}
                  </div>
                  <div className="text-[11px] text-[#9CA3AF]">{b.dateLabel}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Filters */}
          <div className="bg-white rounded-[16px] p-4 md:p-5 shadow-md">
            <h3 className="text-[16px] font-semibold text-[#1A1A2E] mb-4">
              🔖 Quick Filters
            </h3>
            <div className="space-y-3">
              {JOURNAL_QUICK_FILTERS.map((f) => (
                <div
                  key={f.id}
                  className="bg-[#F0F3F8] rounded-[10px] px-4 py-3 hover:bg-[#E5E7EB] cursor-pointer transition-all"
                >
                  <div className="text-[13px] font-semibold text-[#1A1A2E] mb-1">
                    {f.title}
                  </div>
                  <div className="text-[11px] text-[#9CA3AF]">{f.countLabel}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="bg-white rounded-[16px] p-4 md:p-5 shadow-md">
            <h3 className="text-[16px] font-semibold text-[#1A1A2E] mb-4">
              📊 Journal Statistics
            </h3>

            <div className="space-y-3">
              <div className="bg-[#F0F3F8] rounded-[10px] px-4 py-3">
                <div className="text-[13px] font-semibold text-[#1A1A2E] mb-1">
                  Total Entries
                </div>
                <div className="text-[24px] font-bold text-[#6A5AE0]">
                  {JOURNAL_STATS.totalEntries}
                </div>
              </div>

              <div className="bg-[#F0F3F8] rounded-[10px] px-4 py-3">
                <div className="text-[13px] font-semibold text-[#1A1A2E] mb-1">
                  This Week
                </div>
                <div className="text-[24px] font-bold text-[#00B3FF]">
                  {JOURNAL_STATS.thisWeek}
                </div>
              </div>
            </div>

            {userRole === "admin" && (
              <div className="mt-4">
                <h4 className="text-[13px] font-semibold text-[#1A1A2E] mb-2">
                  Admin-only Insight
                </h4>
                <p className="text-[12px] text-[#6B7280]">
                  Detailed breakdown of journal sources will appear with telemetry.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
// ------------------------------------------------------
// MAIN DASHBOARD PAGE (role gating, tabs, SWR, telemetry)
// ------------------------------------------------------
type DashboardTab = "overview" | "journal" | "system" | "telemetry";

const DashboardPage: React.FC = () => {
  // Today: mock admin
  const [userRole] = React.useState<UserRole>("admin");

  const [activeTab, setActiveTab] =
    React.useState<DashboardTab>("overview");

  const [selectedEvent, setSelectedEvent] =
    React.useState<ActivityItem | null>(null);

  const {
    data,
    error: dashboardError,
  } = useSWR<OverviewApiResponse>("/api/dashboard", axiosFetcher, {
    revalidateOnFocus: false,
  });

  const timelineEvents: ActivityItem[] = (
    data?.recentActivity ?? RECENT_ACTIVITY
  ).map((item) => ({
    id: item.id,
    title: item.title,
    description: item.desc,
    timeAgo: item.timeAgo,
    brain:
      item.tag === "System"
        ? "system"
        : (item.tag.toLowerCase() as ActivityItem["brain"]),
  }));

  const overview: OverviewApiResponse =
    data && data.brains
      ? data
      : {
          brains: {
            knowledge: { kpi: 847, delta: "+12.3%" },
            pattern: { kpi: 623, delta: "+8.7%" },
            skill: { kpi: 1042, delta: "+15.2%" },
          },
          recentActivity: RECENT_ACTIVITY,
        };

  const loading = !data && !dashboardError;

  // ------------------------------------------------------
  // ERROR FALLBACK
  // ------------------------------------------------------
  if (dashboardError) {
    return (
      <main className="p-4 md:p-6">
        <TelemetryClient />
        <div className="mt-6">
          <ErrorCard message="Unable to load dashboard data." />
        </div>
      </main>
    );
  }

  // ------------------------------------------------------
  // REDIRECT NON-ADMINS AWAY FROM SYSTEM / TELEMETRY
  // ------------------------------------------------------
  React.useEffect(() => {
    if (userRole !== "admin" &&
      (activeTab === "system" || activeTab === "telemetry")
    ) {
      setActiveTab("overview");
    }
  }, [userRole, activeTab]);

  // ------------------------------------------------------
  // PAGE RENDER
  // ------------------------------------------------------
  return (
    <main className="p-4 md:p-6">
      <TelemetryClient />

      {/* TOP NAV TABS */}
      <nav className="flex gap-10 mb-6 border-b border-[#E5E7EB]">
        <TopTabButton
          active={activeTab === "overview"}
          onClick={() => setActiveTab("overview")}
        >
          ORKO Overview
        </TopTabButton>

        <TopTabButton
          active={activeTab === "journal"}
          onClick={() => setActiveTab("journal")}
        >
          Learning Journal
        </TopTabButton>

        {/* FUTURE ADMIN TABS
        <TopTabButton
          active={activeTab === "system"}
          onClick={() => userRole === "admin" && setActiveTab("system")}
        >
          <span className={userRole !== "admin" ? "opacity-40 cursor-not-allowed" : ""}>
            System Monitor
          </span>
        </TopTabButton>
        */}
      </nav>

      {/* TABS */}
      {activeTab === "overview" && (
        <OverviewTab
          overview={overview}
          loading={loading}
          timelineEvents={timelineEvents}
          selectedEvent={selectedEvent}
          setSelectedEvent={setSelectedEvent}
          userRole={userRole}
        />
      )}

      {activeTab === "journal" && (
        <LearningJournalTab
          userRole={userRole}
          journalLoading={loading}
        />
      )}

      {/* FUTURE ADMIN-ONLY PANELS */}
      {activeTab === "system" && (
        <>
          {userRole !== "admin" ? (
            <NoAccess message="This section is available only to ORKO admins." />
          ) : (
            <div className="text-[#6B7280]">System Monitor (coming in Day 10)</div>
          )}
        </>
      )}

      {activeTab === "telemetry" && (
        <>
          {userRole !== "admin" ? (
            <NoAccess message="This section is available only to ORKO admins." />
          ) : (
            <div className="text-[#6B7280]">Telemetry Panel (coming in Day 10)</div>
          )}
        </>
      )}
    </main>
  );
};

export default DashboardPage;
