"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Users,
  ClockAlert,
  Calendar,
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  AlertCircle,
  Loader2,
  Activity,
  UserCheck,
  Award,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { AdminDashboardResponse } from "@/types";
import { fadeInUp, staggerContainer } from "@/lib/animations";

export default function AdminDashboardPage() {
  const [data, setData] = useState<AdminDashboardResponse | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(2025);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    setError(null);
    try {
      const res = await apiClient<AdminDashboardResponse>("/admin/dashboard");
      setData(res);
    } catch (err: unknown) {
      console.error("Failed to load admin dashboard", err);
      setError("Unable to retrieve operational metrics. Please verify backend connection.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const formatRelativeTime = (isoString: string) => {
    try {
      const diffSec = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
      if (diffSec < 60) return "Just now";
      if (diffSec < 3600) return `${Math.floor(diffSec / 60)} mins ago`;
      if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} hours ago`;
      return new Date(isoString).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
      });
    } catch {
      return isoString;
    }
  };

  const studentCount = data?.volunteers.by_category?.STUDENT ?? 0;
  const alumniCount = data?.volunteers.by_category?.ALUMNI ?? 0;
  const corporateCount = data?.volunteers.by_category?.CORPORATE ?? 0;
  const totalVolunteers = data?.volunteers.total_volunteers || (studentCount + alumniCount + corporateCount) || 1;

  const studentPct = Math.round((studentCount / totalVolunteers) * 100) || 0;
  const alumniPct = Math.round((alumniCount / totalVolunteers) * 100) || 0;
  const corporatePct = Math.round((corporateCount / totalVolunteers) * 100) || 0;

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16">
      {/* Page Header with Year Dropdown (Reference Screen 7 Match) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-charcoal-900 tracking-tight font-serif flex items-center gap-2.5">
            Dashboard
          </h1>
          <p className="text-sm text-charcoal-500 mt-1">
            Real-time operations, onboarding pipeline, event milestones, and verified volunteerism metrics.
          </p>
        </div>

        {/* Year Dropdown */}
        <div className="flex items-center gap-2 self-start sm:self-auto bg-white border border-charcoal-200/80 rounded-xl px-3.5 py-1.5 shadow-2xs">
          <span className="text-xs text-charcoal-500 font-bold uppercase tracking-wider">Year:</span>
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="bg-transparent text-sm font-extrabold text-charcoal-800 focus:outline-none cursor-pointer"
          >
            <option value={2026}>2026</option>
            <option value={2025}>2025</option>
            <option value={2024}>2024</option>
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-charcoal-200/80 shadow-2xs">
          <Loader2 className="w-8 h-8 text-[#F5B817] animate-spin" />
          <p className="text-sm font-semibold text-charcoal-600 mt-3">Loading administrative metrics...</p>
        </div>
      ) : error || !data ? (
        <div className="bg-red-50 border border-red-200 rounded-3xl p-8 text-center text-red-800 space-y-3">
          <AlertCircle className="w-10 h-10 text-red-500 mx-auto" />
          <h3 className="text-base font-bold">{error || "Failed to load dashboard"}</h3>
          <button
            onClick={() => {
              setIsLoading(true);
              void loadDashboard();
            }}
            className="px-5 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-bold shadow-2xs transition-colors"
          >
            Retry
          </button>
        </div>
      ) : (
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="space-y-8"
        >
          {/* Top 4 KPI Cards (Screen 7 Visual Match) */}
          <motion.div variants={fadeInUp} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
            {/* Total Volunteers */}
            <div className="bg-white rounded-3xl border border-charcoal-200/80 p-6 shadow-2xs hover:shadow-xs transition-shadow">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-charcoal-500">
                  Total Volunteers
                </span>
                <div className="w-10 h-10 rounded-2xl bg-amber-50 text-[#F5B817] flex items-center justify-center">
                  <Users className="w-5 h-5 text-amber-600" />
                </div>
              </div>
              <div className="mt-4">
                <h3 className="text-3xl font-extrabold text-charcoal-900 tracking-tight">
                  {data.volunteers.total_volunteers.toLocaleString("en-IN")}
                </h3>
                <p className="text-xs font-semibold text-charcoal-400 mt-1">
                  {data.volunteers.active_volunteers.toLocaleString("en-IN")} Active Volunteers
                </p>
              </div>
            </div>

            {/* Pending Approvals */}
            <Link
              href="/admin/applications?status=PENDING"
              className="bg-white rounded-3xl border border-charcoal-200/80 hover:border-[#F5B817] p-6 shadow-2xs hover:shadow-xs transition-all group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-charcoal-500">
                  Pending Approvals
                </span>
                <div className="w-10 h-10 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                  <ClockAlert className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4">
                <h3 className="text-3xl font-extrabold text-amber-700 tracking-tight">
                  {data.applications.pending.toLocaleString("en-IN")}
                </h3>
                <p className="text-xs font-bold text-amber-600 mt-1 flex items-center gap-1">
                  Awaiting Application Review <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                </p>
              </div>
            </Link>

            {/* Total Events */}
            <Link
              href="/admin/events"
              className="bg-white rounded-3xl border border-charcoal-200/80 hover:border-charcoal-400 p-6 shadow-2xs hover:shadow-xs transition-all group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-charcoal-500">
                  Total Events
                </span>
                <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                  <Calendar className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4">
                <h3 className="text-3xl font-extrabold text-charcoal-900 tracking-tight">
                  {data.events.total_events.toLocaleString("en-IN")}
                </h3>
                <p className="text-xs font-semibold text-charcoal-400 mt-1">
                  {data.events.completed_events} Completed • {data.events.by_status?.PUBLISHED ?? 0} Published
                </p>
              </div>
            </Link>

            {/* Verified Hours */}
            <div className="bg-white rounded-3xl border border-charcoal-200/80 p-6 shadow-2xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-charcoal-500">
                  Verified Hours
                </span>
                <div className="w-10 h-10 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4">
                <h3 className="text-3xl font-extrabold text-charcoal-900 tracking-tight">
                  {data.engagement.total_hours_credited}
                </h3>
                <p className="text-xs font-semibold text-charcoal-400 mt-1">
                  {data.engagement.total_points_allocated} Points Awarded
                </p>
              </div>
            </div>
          </motion.div>

          {/* Middle Row: Volunteer Participation & Action Required (Screen 7 Visual Match) */}
          <motion.div variants={fadeInUp} className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Card: Volunteer Participation */}
            <div className="lg:col-span-6 bg-white rounded-3xl border border-charcoal-200/80 p-6 md:p-8 shadow-2xs space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="font-extrabold text-charcoal-900 text-base md:text-lg">
                  Volunteer Participation
                </h3>
                <span className="text-xs font-bold text-charcoal-400">By Category</span>
              </div>

              {/* Graphic Ring & Summary */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-8 py-4">
                {/* Visual Ring Representation */}
                <div className="relative w-36 h-36 rounded-full border-8 border-primary-500 flex flex-col items-center justify-center bg-primary-50/40 shadow-inner">
                  <span className="text-2xl font-black text-charcoal-900">{totalVolunteers}</span>
                  <span className="text-[10px] font-bold text-charcoal-500 uppercase tracking-wider">Volunteers</span>
                </div>

                {/* Legend & Breakdown */}
                <div className="space-y-3.5 w-full sm:w-auto">
                  <div className="flex items-center justify-between sm:justify-start gap-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3.5 h-3.5 rounded-full bg-primary-500 flex-shrink-0" />
                      <span className="text-sm font-bold text-charcoal-800">Students</span>
                    </div>
                    <span className="text-xs font-extrabold text-charcoal-600 sm:ml-auto">
                      {studentPct}% ({studentCount})
                    </span>
                  </div>

                  <div className="flex items-center justify-between sm:justify-start gap-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3.5 h-3.5 rounded-full bg-emerald-500 flex-shrink-0" />
                      <span className="text-sm font-bold text-charcoal-800">Alumni</span>
                    </div>
                    <span className="text-xs font-extrabold text-charcoal-600 sm:ml-auto">
                      {alumniPct}% ({alumniCount})
                    </span>
                  </div>

                  <div className="flex items-center justify-between sm:justify-start gap-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3.5 h-3.5 rounded-full bg-sky-500 flex-shrink-0" />
                      <span className="text-sm font-bold text-charcoal-800">Corporate</span>
                    </div>
                    <span className="text-xs font-extrabold text-charcoal-600 sm:ml-auto">
                      {corporatePct}% ({corporateCount})
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Card: Action Required */}
            <div className="lg:col-span-6 bg-white rounded-3xl border border-charcoal-200/80 p-6 md:p-8 shadow-2xs space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-extrabold text-charcoal-900 text-base md:text-lg flex items-center gap-2">
                  <ClockAlert className="w-5 h-5 text-amber-600" /> Action Required
                </h3>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                  Priority Tasks
                </span>
              </div>

              <div className="space-y-3 pt-2">
                <Link
                  href="/admin/applications?status=PENDING"
                  className="flex items-center justify-between p-3.5 rounded-2xl bg-amber-50/70 hover:bg-amber-100/70 border border-amber-200 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <UserCheck className="w-5 h-5 text-amber-700" />
                    <span className="text-xs md:text-sm font-bold text-charcoal-900">
                      {data.applications.pending} volunteer applications awaiting review
                    </span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-amber-700 group-hover:translate-x-1 transition-transform" />
                </Link>

                <Link
                  href="/admin/events"
                  className="flex items-center justify-between p-3.5 rounded-2xl bg-charcoal-50 hover:bg-charcoal-100/80 border border-charcoal-200 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-charcoal-700" />
                    <span className="text-xs md:text-sm font-bold text-charcoal-900">
                      Manage published events & participant rosters
                    </span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-charcoal-700 group-hover:translate-x-1 transition-transform" />
                </Link>

                <Link
                  href="/admin/attendance"
                  className="flex items-center justify-between p-3.5 rounded-2xl bg-charcoal-50 hover:bg-charcoal-100/80 border border-charcoal-200 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-charcoal-700" />
                    <span className="text-xs md:text-sm font-bold text-charcoal-900">
                      Attendance verification and hours audit
                    </span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-charcoal-700 group-hover:translate-x-1 transition-transform" />
                </Link>

                <Link
                  href="/admin/operations"
                  className="flex items-center justify-between p-3.5 rounded-2xl bg-charcoal-50 hover:bg-charcoal-100/80 border border-charcoal-200 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <Activity className="w-5 h-5 text-charcoal-700" />
                    <span className="text-xs md:text-sm font-bold text-charcoal-900">
                      Inspect transactional outbox communication queue
                    </span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-charcoal-700 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>
          </motion.div>

          {/* Bottom Section: Recent Activity (Screen 7 Visual Match) */}
          <motion.div variants={fadeInUp} className="bg-white rounded-3xl border border-charcoal-200/80 p-6 md:p-8 shadow-2xs space-y-4">
            <div className="flex items-center justify-between border-b border-charcoal-100 pb-4">
              <h3 className="font-extrabold text-charcoal-900 text-base md:text-lg flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary-600" />
                Recent System Activity
              </h3>
              <span className="text-xs font-semibold text-charcoal-400">Canonical Audit Stream</span>
            </div>

            {data.recent_activity.length === 0 ? (
              <div className="p-8 text-center text-charcoal-400 text-sm">
                No recent system activity recorded yet.
              </div>
            ) : (
              <div className="divide-y divide-charcoal-100">
                {data.recent_activity.slice(0, 7).map((act) => (
                  <div key={act.id} className="py-3 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-8 h-8 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center flex-shrink-0 text-xs font-bold">
                        {act.action.includes("LOGIN") ? (
                          <ShieldCheck className="w-4 h-4 text-emerald-600" />
                        ) : act.action.includes("EVENT") ? (
                          <Calendar className="w-4 h-4 text-sky-600" />
                        ) : (
                          <Award className="w-4 h-4 text-amber-600" />
                        )}
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs md:text-sm font-bold text-charcoal-900 truncate">
                          {act.action.replace(/_/g, " ")}
                        </p>
                        <p className="text-[11px] text-charcoal-500 truncate">
                          Actor: {act.actor_email || "System Processor"} • Target: {act.resource_type}
                        </p>
                      </div>
                    </div>
                    <span className="text-[11px] font-semibold text-charcoal-400 whitespace-nowrap">
                      {formatRelativeTime(act.created_at)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}

