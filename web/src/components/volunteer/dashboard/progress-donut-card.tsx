"use client";

import React from "react";
import Link from "next/link";
import { Award, ArrowRight } from "lucide-react";
import { GamificationSummaryResponse } from "@/types";

interface ProgressDonutCardProps {
  displayName: string;
  summary: GamificationSummaryResponse | null;
}

export function ProgressDonutCard({
  displayName,
  summary,
}: ProgressDonutCardProps) {
  // Derive progress strictly from backend completed events count
  const eventsCount = summary?.completed_events_count ?? 0;
  // Next tier target in intervals of 5
  const targetMilestone = Math.max(5, Math.ceil((eventsCount + 1) / 5) * 5);
  const remaining = Math.max(0, targetMilestone - eventsCount);
  const percentage = Math.min(100, Math.round((eventsCount / targetMilestone) * 100));

  // SVG circular geometry
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="bg-white rounded-2xl p-6 border border-[#EFECE6] shadow-xs flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-[#1F2421]">
            <div className="w-8 h-8 rounded-xl bg-[#FFF8E7] text-[#946C00] flex items-center justify-center">
              <Award className="w-4 h-4 text-[#F5B817]" />
            </div>
            <h3 className="text-base font-extrabold tracking-tight">
              Your Progress
            </h3>
          </div>
          <Link
            href="/volunteer/profile"
            className="text-xs font-bold text-[#B45309] hover:text-[#946C00] hover:underline flex items-center gap-1 transition-colors"
          >
            <span>View Details</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Circular Donut Progress Ring */}
        <div className="flex flex-col items-center justify-center py-2">
          <div className="relative w-28 h-28 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              {/* Background Track */}
              <circle
                cx="50"
                cy="50"
                r={radius}
                className="text-[#FEF3C7]"
                strokeWidth="10"
                stroke="currentColor"
                fill="transparent"
              />
              {/* Filled Progress Arc */}
              <circle
                cx="50"
                cy="50"
                r={radius}
                className="text-[#F5B817] transition-all duration-700 ease-out"
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
              />
            </svg>
            {/* Center Percentage Display */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-xl font-black text-[#1F2421]">
                {percentage}%
              </span>
            </div>
          </div>

          {/* Dynamic Authentic Copy */}
          <p className="text-xs text-[#4B5563] text-center mt-3 mb-2 leading-relaxed max-w-xs">
            {eventsCount === 0 ? (
              <>
                Welcome, <span className="font-bold text-[#1F2421]">{displayName}</span>! Participate in your first volunteering drive to earn impact points.
              </>
            ) : (
              <>
                Keep going, <span className="font-bold text-[#1F2421]">{displayName}</span>! You&apos;ve completed {eventsCount} drives and are making a difference in the community.
              </>
            )}
          </p>
        </div>
      </div>

      {/* Milestone Celebration Banner */}
      <div className="mt-4 p-3 rounded-xl bg-[#FEF3C7] border border-[#FDE68A] text-xs font-bold text-[#78350F] text-center flex items-center justify-center gap-1.5 shadow-2xs">
        <span>
          {remaining === 1
            ? "1 more event to reach the next milestone 🎉"
            : `${remaining} more events to reach the next milestone tier 🎉`}
        </span>
      </div>
    </div>
  );
}
