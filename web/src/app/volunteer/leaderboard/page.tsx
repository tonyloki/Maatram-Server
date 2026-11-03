"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import {
  Trophy,
  Crown,
  Medal,
  Award,
  ChevronRight,
  Shield,
  Loader2,
  AlertCircle,
  User,
  Sparkles,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { LeaderboardResponse, LeaderboardItem, VolunteerProfileResponse } from "@/types";
import { fadeInUp, staggerContainer } from "@/lib/animations";

const CATEGORIES = [
  { id: "ALL", label: "Overall" },
  { id: "STUDENT", label: "Students" },
  { id: "ALUMNI", label: "Alumni" },
  { id: "CORPORATE", label: "Corporate" },
];

export default function VolunteerLeaderboardPage() {
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [selectedYear, setSelectedYear] = useState(2025);
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardResponse | null>(null);
  const [currentVolunteer, setCurrentVolunteer] = useState<VolunteerProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadLeaderboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [boardRes, profileRes] = await Promise.all([
        apiClient<LeaderboardResponse>("/gamification/leaderboard", {
          params: {
            category: selectedCategory,
            cycle_year: selectedYear,
            page: 1,
            page_size: 50,
          },
        }),
        apiClient<VolunteerProfileResponse>("/volunteers/me").catch(() => null),
      ]);

      setLeaderboardData(boardRes);
      setCurrentVolunteer(profileRes);
    } catch (err: unknown) {
      console.error("Failed to load leaderboard", err);
      setError("Unable to load leaderboard rankings at this time.");
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory, selectedYear]);

  useEffect(() => {
    loadLeaderboard();
  }, [loadLeaderboard]);

  const items = leaderboardData?.items || [];
  const top1 = items[0] || null;
  const top2 = items[1] || null;
  const top3 = items[2] || null;
  const restItems = items.slice(3);

  // Check if item belongs to current user
  const isCurrentUser = (item: LeaderboardItem) => {
    if (!currentVolunteer) return false;
    if (item.volunteer_profile_id && item.volunteer_profile_id === currentVolunteer.id) return true;
    const currentFullName = `${currentVolunteer.first_name} ${currentVolunteer.last_name}`.trim();
    return item.volunteer_name.toLowerCase() === currentFullName.toLowerCase();
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-16">
      {/* Header & Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-charcoal-900 tracking-tight font-serif flex items-center gap-2.5">
            Leaderboard
          </h1>
          <p className="text-sm text-charcoal-500 mt-1">
            Recognizing dedicated volunteers across mentorship, interviews, and community initiatives.
          </p>
        </div>

        {/* Year Dropdown */}
        <div className="flex items-center gap-2 self-start sm:self-auto bg-white border border-charcoal-200/80 rounded-xl px-3 py-1.5 shadow-xs">
          <span className="text-xs text-charcoal-500 font-semibold uppercase tracking-wider">Year:</span>
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="bg-transparent text-sm font-bold text-charcoal-800 focus:outline-none cursor-pointer"
          >
            <option value={2026}>2026</option>
            <option value={2025}>2025</option>
            <option value={2024}>2024</option>
          </select>
        </div>
      </div>

      {/* Category Filter Pills (Matching Screen 5) */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        {CATEGORIES.map((cat) => {
          const active = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-xl text-xs md:text-sm font-bold transition-all whitespace-nowrap ${
                active
                  ? "bg-primary-500 text-charcoal-950 shadow-xs ring-1 ring-primary-500"
                  : "bg-white border border-charcoal-200/80 text-charcoal-600 hover:bg-charcoal-50"
              }`}
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      {/* Main Content */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-charcoal-200/80">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm font-medium text-charcoal-500 mt-3">Computing verified rankings...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center text-red-700">
          <AlertCircle className="w-8 h-8 mx-auto text-red-500 mb-2" />
          <p className="font-semibold">{error}</p>
          <button
            onClick={loadLeaderboard}
            className="mt-3 px-4 py-1.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      ) : items.length === 0 ? (
        <div className="bg-white rounded-3xl border border-charcoal-200/80 p-12 text-center">
          <Trophy className="w-12 h-12 text-charcoal-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-charcoal-900">No rankings available for this selection</h3>
          <p className="text-sm text-charcoal-500 mt-1 max-w-sm mx-auto">
            Points will be updated once volunteering attendance is confirmed and verified.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Top 3 Podium Cards (Screen 5 Visual Match) */}
          <div className="bg-gradient-to-b from-primary-50/50 via-white to-white rounded-3xl border border-charcoal-200/80 p-6 md:p-10 shadow-xs">
            <div className="grid grid-cols-3 gap-2 sm:gap-6 items-end max-w-2xl mx-auto pt-6 pb-2">
              {/* 2nd Place (Left) */}
              {top2 ? (
                <div className="flex flex-col items-center text-center">
                  <div className="relative mb-2">
                    <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full overflow-hidden bg-slate-100 ring-4 ring-slate-300 shadow-sm flex items-center justify-center text-slate-700 font-bold text-xl relative">
                      {top2.avatar_url && !top2.is_anonymous ? (
                        <Image src={top2.avatar_url} alt={top2.volunteer_name} fill className="object-cover" />
                      ) : (
                        <User className="w-8 h-8 text-slate-400" />
                      )}
                    </div>
                    <span className="absolute -bottom-2.5 left-1/2 -translate-x-1/2 bg-slate-600 text-white text-[11px] font-black w-6 h-6 rounded-full flex items-center justify-center shadow-xs">
                      2
                    </span>
                  </div>
                  <h4 className="font-bold text-charcoal-900 text-xs sm:text-sm mt-3 truncate max-w-[100px] sm:max-w-[140px]">
                    {top2.is_anonymous ? "Anonymous" : top2.volunteer_name}
                  </h4>
                  <p className="text-xs sm:text-sm font-extrabold text-primary-700 mt-0.5">
                    {Number(top2.total_points || 0)} pts
                  </p>
                </div>
              ) : (
                <div className="opacity-0" />
              )}

              {/* 1st Place (Center, Elevated) */}
              {top1 ? (
                <div className="flex flex-col items-center text-center -translate-y-4">
                  <div className="flex items-center justify-center mb-1 animate-bounce text-amber-500">
                    <Crown className="w-8 h-8 fill-amber-400 text-amber-500 drop-shadow-sm" />
                  </div>
                  <div className="relative mb-2">
                    <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full overflow-hidden bg-amber-50 ring-4 ring-amber-400 shadow-md flex items-center justify-center text-amber-800 font-bold text-2xl relative">
                      {top1.avatar_url && !top1.is_anonymous ? (
                        <Image src={top1.avatar_url} alt={top1.volunteer_name} fill className="object-cover" />
                      ) : (
                        <User className="w-10 h-10 text-amber-500" />
                      )}
                    </div>
                    <span className="absolute -bottom-3 left-1/2 -translate-x-1/2 bg-amber-500 text-charcoal-950 text-xs font-black w-7 h-7 rounded-full flex items-center justify-center shadow-sm">
                      1
                    </span>
                  </div>
                  <h4 className="font-black text-charcoal-950 text-sm sm:text-base mt-3.5 truncate max-w-[120px] sm:max-w-[160px]">
                    {top1.is_anonymous ? "Anonymous" : top1.volunteer_name}
                  </h4>
                  <p className="text-sm sm:text-base font-extrabold text-primary-800 mt-0.5">
                    {Number(top1.total_points || 0)} pts
                  </p>
                </div>
              ) : null}

              {/* 3rd Place (Right) */}
              {top3 ? (
                <div className="flex flex-col items-center text-center">
                  <div className="relative mb-2">
                    <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full overflow-hidden bg-amber-900/10 ring-4 ring-amber-700/60 shadow-sm flex items-center justify-center text-amber-900 font-bold text-xl relative">
                      {top3.avatar_url && !top3.is_anonymous ? (
                        <Image src={top3.avatar_url} alt={top3.volunteer_name} fill className="object-cover" />
                      ) : (
                        <User className="w-8 h-8 text-amber-800/60" />
                      )}
                    </div>
                    <span className="absolute -bottom-2.5 left-1/2 -translate-x-1/2 bg-amber-800 text-white text-[11px] font-black w-6 h-6 rounded-full flex items-center justify-center shadow-xs">
                      3
                    </span>
                  </div>
                  <h4 className="font-bold text-charcoal-900 text-xs sm:text-sm mt-3 truncate max-w-[100px] sm:max-w-[140px]">
                    {top3.is_anonymous ? "Anonymous" : top3.volunteer_name}
                  </h4>
                  <p className="text-xs sm:text-sm font-extrabold text-primary-700 mt-0.5">
                    {Number(top3.total_points || 0)} pts
                  </p>
                </div>
              ) : (
                <div className="opacity-0" />
              )}
            </div>
          </div>

          {/* Ranked Table (Matches Screen 5) */}
          <div className="bg-white rounded-2xl border border-charcoal-200/80 overflow-hidden shadow-xs">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs md:text-sm text-charcoal-700">
                <thead className="bg-charcoal-50/80 border-b border-charcoal-200 text-charcoal-500 uppercase tracking-wider text-[11px] font-bold">
                  <tr>
                    <th className="py-3 px-4 w-16 text-center">#</th>
                    <th className="py-3 px-4">Volunteer</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4 text-right">Points</th>
                    <th className="py-3 px-4 text-right">Hours</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-charcoal-100">
                  {items.map((item) => {
                    const isSelf = isCurrentUser(item);
                    return (
                      <tr
                        key={`${item.rank}-${item.volunteer_name}`}
                        className={`transition-colors ${
                          isSelf
                            ? "bg-primary-50/90 font-semibold border-l-4 border-l-primary-500"
                            : "hover:bg-charcoal-50/50"
                        }`}
                      >
                        <td className="py-3.5 px-4 text-center font-bold text-charcoal-800">
                          {item.rank <= 3 ? (
                            <span
                              className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-black ${
                                item.rank === 1
                                  ? "bg-amber-400 text-charcoal-950"
                                  : item.rank === 2
                                  ? "bg-slate-300 text-charcoal-950"
                                  : "bg-amber-700 text-white"
                              }`}
                            >
                              {item.rank}
                            </span>
                          ) : (
                            item.rank
                          )}
                        </td>
                        <td className="py-3.5 px-4">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-full bg-charcoal-100 flex items-center justify-center text-charcoal-600 font-bold text-xs flex-shrink-0">
                              {item.avatar_url && !item.is_anonymous ? (
                                <Image
                                  src={item.avatar_url}
                                  alt={item.volunteer_name}
                                  width={32}
                                  height={32}
                                  className="rounded-full object-cover"
                                />
                              ) : (
                                <User className="w-4 h-4 text-charcoal-400" />
                              )}
                            </div>
                            <div>
                              <span className="font-bold text-charcoal-900">
                                {isSelf
                                  ? `You (${item.is_anonymous ? "Anonymous" : item.volunteer_name})`
                                  : item.is_anonymous
                                  ? "Anonymous Volunteer"
                                  : item.volunteer_name}
                              </span>
                              {isSelf && (
                                <span className="ml-2 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-primary-200 text-charcoal-950">
                                  You
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td className="py-3.5 px-4">
                          <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-charcoal-100 text-charcoal-700">
                            {item.category}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-right font-extrabold text-charcoal-900">
                          {Number(item.total_points || 0)}
                        </td>
                        <td className="py-3.5 px-4 text-right font-semibold text-charcoal-600">
                          {Number(item.total_hours || 0)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Privacy Note / DPDP Option (Screen 5/6 connection) */}
          <div className="bg-charcoal-50 rounded-2xl border border-charcoal-200/80 p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-charcoal-600">
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-charcoal-500 flex-shrink-0" />
              <span>
                Want to hide your name on the public leaderboard? You can toggle anonymity at any time in your Privacy &
                Consents settings.
              </span>
            </div>
            <Link
              href="/volunteer/profile?tab=consents"
              className="font-bold text-primary-800 hover:text-primary-900 hover:underline flex items-center gap-1 flex-shrink-0"
            >
              Manage Consents <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

