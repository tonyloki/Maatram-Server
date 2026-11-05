"use client";

import React from "react";
import Link from "next/link";
import {
  BarChart3,
  Star,
  Clock,
  Calendar,
  Trophy,
  ChevronDown,
  ArrowRight,
  Check,
} from "lucide-react";
import { GamificationSummaryResponse } from "@/types";

interface ContributionKpiRowProps {
  summary: GamificationSummaryResponse | null;
  isLoading: boolean;
}

export function ContributionKpiRow({
  summary,
  isLoading,
}: ContributionKpiRowProps) {
  const cycleYear = summary?.cycle_year || new Date().getFullYear();
  const totalPoints = summary?.total_points ?? 0;
  const totalHours = Number(summary?.total_hours || 0).toFixed(1);
  const eventsCount = summary?.completed_events_count ?? 0;
  const currentRank = summary?.rank ? `#${summary.rank}` : "—";

  return (
    <section aria-label="Volunteer Contribution at a Glance" className="space-y-3.5">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-[#1F2421]">
          <BarChart3 className="w-5 h-5 text-[#F5B817]" />
          <h2 className="text-lg sm:text-xl font-extrabold tracking-tight">
            Your Contribution at a Glance
          </h2>
        </div>

        {/* Cycle Year Selector Chip */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-white border border-[#EFECE6] text-xs font-bold text-[#4B5563] shadow-2xs">
          <span>Cycle Year: {cycleYear}</span>
          <ChevronDown className="w-3.5 h-3.5 text-[#9CA3AF]" />
        </div>
      </div>

      {/* 4-Card Responsive Metric Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4">
        {/* Metric 1: Volunteering Points */}
        <div className="bg-white rounded-2xl p-4 sm:p-4.5 border border-[#EFECE6] shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow group">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs sm:text-sm font-bold text-[#6B7280]">
              Volunteering Points
            </span>
            <div className="w-8.5 h-8.5 rounded-full bg-[#FEF3C7] text-[#D97706] flex items-center justify-center shadow-2xs group-hover:scale-105 transition-transform">
              <Star className="w-4.5 h-4.5 fill-[#F5B817] text-[#D97706]" />
            </div>
          </div>

          <div className="space-y-0.5">
            <div className="text-2xl sm:text-3xl font-extrabold text-[#1F2421] tracking-tight">
              {isLoading ? (
                <div className="w-16 h-8 bg-gray-100 rounded-md animate-pulse" />
              ) : (
                totalPoints
              )}
            </div>
            <p className="text-[11px] font-semibold text-[#6B7280]">
              Events × 10 + Hours × 2
            </p>
          </div>
        </div>

        {/* Metric 2: Approved Hours */}
        <div className="bg-white rounded-2xl p-4 sm:p-4.5 border border-[#EFECE6] shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow group">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs sm:text-sm font-bold text-[#6B7280]">
              Approved Hours
            </span>
            <div className="w-8.5 h-8.5 rounded-full bg-[#DCFCE7] text-[#16A34A] flex items-center justify-center shadow-2xs group-hover:scale-105 transition-transform">
              <Clock className="w-4.5 h-4.5" />
            </div>
          </div>

          <div className="space-y-0.5">
            <div className="text-2xl sm:text-3xl font-extrabold text-[#1F2421] tracking-tight">
              {isLoading ? (
                <div className="w-16 h-8 bg-gray-100 rounded-md animate-pulse" />
              ) : (
                totalHours
              )}
            </div>
            <p className="text-[11px] font-bold text-[#16A34A] flex items-center gap-1">
              <Check className="w-3 h-3" /> Verified service
            </p>
          </div>
        </div>

        {/* Metric 3: Events Attended */}
        <div className="bg-white rounded-2xl p-4 sm:p-4.5 border border-[#EFECE6] shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow group">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs sm:text-sm font-bold text-[#6B7280]">
              Events Attended
            </span>
            <div className="w-8.5 h-8.5 rounded-full bg-[#E0F2FE] text-[#0284C7] flex items-center justify-center shadow-2xs group-hover:scale-105 transition-transform">
              <Calendar className="w-4.5 h-4.5" />
            </div>
          </div>

          <div className="space-y-0.5">
            <div className="text-2xl sm:text-3xl font-extrabold text-[#1F2421] tracking-tight">
              {isLoading ? (
                <div className="w-16 h-8 bg-gray-100 rounded-md animate-pulse" />
              ) : (
                eventsCount
              )}
            </div>
            <p className="text-[11px] font-semibold text-[#6B7280]">
              Completed drives
            </p>
          </div>
        </div>

        {/* Metric 4: Current Rank */}
        <div className="bg-white rounded-2xl p-4 sm:p-4.5 border border-[#EFECE6] shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow group">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs sm:text-sm font-bold text-[#6B7280]">
              Current Rank
            </span>
            <div className="w-8.5 h-8.5 rounded-full bg-[#FFEDD5] text-[#EA580C] flex items-center justify-center shadow-2xs group-hover:scale-105 transition-transform">
              <Trophy className="w-4.5 h-4.5" />
            </div>
          </div>

          <div className="space-y-0.5">
            <div className="text-2xl sm:text-3xl font-extrabold text-[#1F2421] tracking-tight">
              {isLoading ? (
                <div className="w-16 h-8 bg-gray-100 rounded-md animate-pulse" />
              ) : (
                currentRank
              )}
            </div>
            <Link
              href="/volunteer/leaderboard"
              className="text-[11px] font-bold text-[#B45309] hover:underline flex items-center gap-1 group-hover:text-[#D97706]"
            >
              <span>View leaderboard</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

