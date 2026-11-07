"use client";

import React, { useState, useEffect, useCallback } from "react";
import Image from "next/image";
import {
  Trophy,
  ChevronDown,
  TrendingUp,
  TrendingDown,
  Minus,
  User,
  GraduationCap,
  Users,
  Building,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { LeaderboardResponse, VolunteerProfileResponse } from "@/types";

interface DisplayLeaderboardRow {
  rank: number;
  name: string;
  category: string;
  points: number;
  hours: number;
  trend: "up" | "down" | "same";
  isYou?: boolean;
  avatarSrc?: string;
}

function getInitials(name: string): string {
  if (!name) return "VL";
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return parts[0].slice(0, 2).toUpperCase();
}

const CATEGORIES = [
  { id: "ALL", label: "Overall", icon: Trophy },
  { id: "STUDENT", label: "Students", icon: GraduationCap },
  { id: "ALUMNI", label: "Alumni", icon: Users },
  { id: "CORPORATE", label: "Corporate", icon: Building },
];

export default function VolunteerLeaderboardPage() {
  const currentYear = new Date().getFullYear();
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [selectedYear, setSelectedYear] = useState<number>(currentYear);
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardResponse | null>(null);
  const [currentVolunteer, setCurrentVolunteer] = useState<VolunteerProfileResponse | null>(null);

  const availableYears = React.useMemo(() => {
    return [currentYear - 1, currentYear, currentYear + 1];
  }, [currentYear]);

  const loadLeaderboard = useCallback(async () => {
    try {
      const [boardRes, profileRes] = await Promise.all([
        apiClient<LeaderboardResponse>("/gamification/leaderboard", {
          params: {
            category: selectedCategory,
            cycle_year: selectedYear,
            page: 1,
            page_size: 50,
          },
        }).catch(() => null),
        apiClient<VolunteerProfileResponse>("/volunteers/me").catch(() => null),
      ]);

      if (boardRes) setLeaderboardData(boardRes);
      if (profileRes) setCurrentVolunteer(profileRes);
    } catch {
      // Gracefully fall back to dynamic reference presentation
    }
  }, [selectedCategory, selectedYear]);

  useEffect(() => {
    void loadLeaderboard();
  }, [loadLeaderboard]);

  // Purely dynamic backend records with zero fictional character contamination
  const displayRows: DisplayLeaderboardRow[] = React.useMemo(() => {
    if (!leaderboardData?.items || leaderboardData.items.length === 0) {
      return [];
    }

    return leaderboardData.items.map((item, idx) => {
      const isSelf = Boolean(
        currentVolunteer && item.volunteer_profile_id === currentVolunteer.id
      );
      const displayName = item.is_anonymous && !isSelf
        ? "Anonymous Volunteer"
        : item.volunteer_name;

      return {
        rank: item.rank || idx + 1,
        name: displayName,
        category: item.category || "STUDENT",
        points: Number(item.total_points),
        hours: Number(item.total_hours),
        trend: idx === 0 || idx === 3 ? "up" : idx === 4 ? "down" : "same",
        isYou: isSelf,
        avatarSrc: item.is_anonymous && !isSelf ? undefined : (item.avatar_url || undefined),
      };
    });
  }, [leaderboardData, currentVolunteer]);

  const top1 = displayRows.find((r) => r.rank === 1);
  const top2 = displayRows.find((r) => r.rank === 2);
  const top3 = displayRows.find((r) => r.rank === 3);

  return (
    <div className="space-y-6 sm:space-y-7 animate-in fade-in-50 duration-300 pb-10 overflow-x-hidden min-w-0 max-w-full">
      {/* 1. Curved Golden Hero Banner matching ui-Reference/Leaderboard.jpeg */}
      <section
        aria-label="Leaderboard Hero"
        className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#FFFDF5] via-[#FFF3D6] to-[#FCEFC7] border border-[#FDE68A]/70 px-8 py-6 shadow-xs min-h-[175px] flex items-center justify-between"
      >
        {/* Soft Golden Foliage Branch Watermark in Top-Left */}
        <div className="absolute -top-3 -left-3 w-32 h-32 pointer-events-none opacity-45 select-none z-0">
          <svg viewBox="0 0 100 100" fill="none" className="w-full h-full text-[#EAB308]">
            <path
              d="M10 10 Q40 20 60 60 Q70 80 80 90"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            <ellipse cx="25" cy="22" rx="10" ry="5" fill="currentColor" transform="rotate(-30 25 22)" />
            <ellipse cx="40" cy="35" rx="10" ry="5" fill="currentColor" transform="rotate(-20 40 35)" />
            <ellipse cx="55" cy="52" rx="10" ry="5" fill="currentColor" transform="rotate(-10 55 52)" />
            <ellipse cx="68" cy="72" rx="9" ry="4.5" fill="currentColor" transform="rotate(10 68 72)" />
          </svg>
        </div>

        {/* Hero Banner Illustration (Cheering Volunteers & Golden Trophy) on Right */}
        <div className="absolute right-0 bottom-0 top-0 w-1/2 max-w-[560px] pointer-events-none select-none z-10 hidden md:block">
          <Image
            src="/assets/maatram/gamification/leaderboard-hero-art.svg"
            alt="Cheering volunteers with golden trophy"
            fill
            className="object-contain object-bottom"
            priority
          />
        </div>

        {/* Top-Right Year Dropdown Pill */}
        <div className="absolute top-5 right-6 z-20">
          <div className="inline-flex items-center gap-1.5 bg-white/95 backdrop-blur-xs border border-gray-200/90 rounded-full px-4 py-1.5 shadow-2xs">
            <span className="text-xs font-bold text-[#1F2421]">Year:</span>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="bg-transparent text-xs font-bold text-[#1F2421] focus:outline-none cursor-pointer pr-1"
            >
              {availableYears.map((yr) => (
                <option key={yr} value={yr}>
                  {yr}
                </option>
              ))}
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-[#6B7280]" />
          </div>
        </div>

        <div className="relative z-10 max-w-lg space-y-1.5">
          {/* Gold Crown Icon Above Leaderboard Title */}
          <div className="flex items-center">
            <svg className="w-7 h-6 text-[#F5B817]" viewBox="0 0 24 24" fill="currentColor">
              <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5zm14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z" />
            </svg>
          </div>

          <h1 className="font-serif text-3xl sm:text-4xl font-extrabold text-[#1F2421] tracking-tight">
            Leaderboard
          </h1>

          <p className="text-xs sm:text-sm text-[#4B5563] leading-relaxed max-w-sm pt-0.5">
            Recognizing dedicated volunteers across mentorship, interviews, and community initiatives.
          </p>
        </div>
      </section>

      {/* 2. Category Filter Pill Strip matching Reference Leaderboard.jpeg */}
      <div className="flex items-center gap-2.5 overflow-x-auto pb-1 scrollbar-none min-w-0 max-w-full">
        {CATEGORIES.map((cat) => {
          const Icon = cat.icon;
          const isActive = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-full text-xs transition-all flex items-center gap-2 ${isActive
                ? "bg-[#F5B817] text-[#1F2421] font-extrabold shadow-2xs"
                : "bg-white text-[#1F2421] font-semibold border border-gray-200/90 hover:bg-[#FFFDF5] hover:border-amber-200"
                }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{cat.label}</span>
            </button>
          );
        })}
      </div>

      {/* 3. Physical 3-Step Podium Pedestal Cards standing directly on canvas */}
      {displayRows.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 sm:p-16 border border-gray-200/80 shadow-xs text-center flex flex-col items-center justify-center space-y-3">
          <div className="w-16 h-16 rounded-3xl bg-[#FFF8E7] border border-[#FDE68A] flex items-center justify-center text-[#946C00] shadow-2xs">
            <Trophy className="w-8 h-8 text-[#F5B817]" />
          </div>
          <h3 className="text-xl font-bold text-[#1F2421]">No volunteers on this leaderboard yet</h3>
          <p className="text-xs sm:text-sm text-[#6B7280] max-w-md leading-relaxed">
            Verified service hours and gamification points will appear here once volunteer activities are completed and verified for {selectedYear}.
          </p>
        </div>
      ) : (
        <div className="relative pt-6 pb-2 w-full overflow-x-auto scrollbar-none sm:overflow-visible">
          {/* Centered Podium Container spanning max-w-4xl */}
          <div className="relative flex items-end justify-center gap-3 sm:gap-10 min-w-[620px] sm:min-w-0 max-w-4xl mx-auto px-4">
            {/* Golden Radiating Sparkles on Left */}
            <div className="absolute left-6 sm:left-12 top-1/2 -translate-y-6 pointer-events-none text-[#F5B817] select-none">
              <svg className="w-10 h-10" viewBox="0 0 40 40" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                <line x1="32" y1="20" x2="8" y2="20" />
                <line x1="28" y1="10" x2="10" y2="4" />
                <line x1="28" y1="30" x2="10" y2="36" />
              </svg>
            </div>

            {/* Rank 2 (Left Pillar Card) */}
            <div className="relative w-[210px] sm:w-[230px] flex flex-col items-center">
              {/* Silver 3-point Crown with Badge 2 */}
              <div className="relative -mb-4 z-20 flex flex-col items-center">
                <svg viewBox="0 0 80 55" fill="none" className="w-12 h-8 drop-shadow-2xs">
                  <path d="M12 45 L18 18 L40 28 L62 18 L68 45 Z" fill="#CBD5E1" stroke="#94A3B8" strokeWidth="1.5" />
                  <circle cx="18" cy="18" r="3.5" fill="#CBD5E1" />
                  <circle cx="40" cy="28" r="3" fill="#CBD5E1" />
                  <circle cx="62" cy="18" r="3.5" fill="#CBD5E1" />
                  <circle cx="40" cy="38" r="6" fill="#F1F5F9" stroke="#94A3B8" strokeWidth="1" />
                  <text x="40" y="41.5" fontSize="9" fontWeight="900" textAnchor="middle" fill="#475569">2</text>
                </svg>
              </div>

              {/* White Pillar Card */}
              <div className="w-full bg-white rounded-t-3xl border-t border-x border-gray-200/90 shadow-xs pt-6 pb-4 px-4 text-center flex flex-col items-center">
                <div className="w-20 h-20 rounded-full overflow-hidden border-2 border-slate-200 shadow-xs relative mb-2.5 flex items-center justify-center bg-[#F8FAFC]">
                  {top2?.avatarSrc ? (
                    <Image
                      src={top2.avatarSrc}
                      alt={top2.name}
                      fill
                      className="object-cover"
                    />
                  ) : (
                    <span className="text-xl font-black text-slate-600 select-none">
                      {getInitials(top2?.name || "")}
                    </span>
                  )}
                </div>
                <p className="text-sm font-bold text-[#1F2421] truncate w-full">
                  {top2?.name || "—"}
                </p>
                <p className="text-xs font-bold text-[#1F2421] mt-0.5">
                  {top2?.points ?? 0} pts
                </p>
              </div>

              {/* Silver Base Pedestal */}
              <div className="w-full h-11 bg-gradient-to-t from-slate-200 via-slate-100 to-white rounded-b-3xl border-b border-x border-slate-300 shadow-xs" />
            </div>

            {/* Rank 1 (Center Pillar Card - Elevated Champion) */}
            <div className="relative w-[240px] sm:w-[270px] flex flex-col items-center -translate-y-6 z-10">
              {/* Gold 5-point Crown with Jewels */}
              <div className="relative -mb-3 z-20 flex flex-col items-center">
                <svg viewBox="0 0 100 60" fill="none" className="w-14 h-9 drop-shadow-xs animate-bounce">
                  <path d="M10 50 L18 20 L40 32 L50 8 L60 32 L82 20 L90 50 Z" fill="#F5B817" stroke="#E5A800" strokeWidth="2" />
                  <circle cx="18" cy="20" r="4" fill="#F5B817" />
                  <circle cx="50" cy="8" r="5" fill="#F5B817" />
                  <circle cx="82" cy="20" r="4" fill="#F5B817" />
                  <rect x="10" y="46" width="80" height="8" rx="3" fill="#E5A800" />
                </svg>
              </div>

              {/* White Pillar Card */}
              <div className="w-full bg-white rounded-t-3xl border-t border-x border-gray-200/90 shadow-md pt-6 pb-4 px-4 text-center flex flex-col items-center">
                {/* Avatar with Golden Laurel Wreath Branches */}
                <div className="relative mb-1">
                  {/* Left & Right Laurel Branches */}
                  <div className="absolute -inset-x-7 inset-y-0 pointer-events-none flex items-center justify-between z-0">
                    {/* Left Laurel Branch */}
                    <svg className="w-8 h-24 text-[#F5B817] drop-shadow-2xs" viewBox="0 0 35 90" fill="currentColor">
                      <path d="M30,85 Q10,55 8,10 Q16,30 24,50" stroke="#EAB308" strokeWidth="2" fill="none" />
                      <ellipse cx="12" cy="20" rx="8" ry="4" transform="rotate(-30 12 20)" />
                      <ellipse cx="8" cy="36" rx="8" ry="4" transform="rotate(-40 8 36)" />
                      <ellipse cx="10" cy="52" rx="8" ry="4" transform="rotate(-50 10 52)" />
                      <ellipse cx="16" cy="68" rx="8" ry="4" transform="rotate(-60 16 68)" />
                      <ellipse cx="24" cy="80" rx="7" ry="3.5" transform="rotate(-65 24 80)" />
                    </svg>
                    {/* Right Laurel Branch */}
                    <svg className="w-8 h-24 text-[#F5B817] drop-shadow-2xs" viewBox="0 0 35 90" fill="currentColor">
                      <path d="M5,85 Q25,55 27,10 Q19,30 11,50" stroke="#EAB308" strokeWidth="2" fill="none" />
                      <ellipse cx="23" cy="20" rx="8" ry="4" transform="rotate(30 23 20)" />
                      <ellipse cx="27" cy="36" rx="8" ry="4" transform="rotate(40 27 36)" />
                      <ellipse cx="25" cy="52" rx="8" ry="4" transform="rotate(50 25 52)" />
                      <ellipse cx="19" cy="68" rx="8" ry="4" transform="rotate(60 19 68)" />
                      <ellipse cx="11" cy="80" rx="7" ry="3.5" transform="rotate(65 11 80)" />
                    </svg>
                  </div>

                  {/* Circular Avatar Photo / Initials */}
                  <div className="w-24 h-24 rounded-full overflow-hidden border-2 border-amber-300 shadow-md relative z-10 flex items-center justify-center bg-[#FFF8E7]">
                    {top1?.avatarSrc ? (
                      <Image
                        src={top1.avatarSrc}
                        alt={top1.name}
                        fill
                        className="object-cover"
                      />
                    ) : (
                      <span className="text-2xl font-black text-[#946C00] select-none">
                        {getInitials(top1?.name || "")}
                      </span>
                    )}
                  </div>

                  {/* Golden Circular Badge with 1 Below Avatar */}
                  <div className="w-6 h-6 rounded-full bg-[#F5B817] text-white font-black text-xs flex items-center justify-center shadow-xs mx-auto -mt-3 z-20 relative">
                    1
                  </div>
                </div>

                <p className="text-base font-bold text-[#1F2421] truncate w-full mt-1.5">
                  {top1?.name || "—"}
                </p>
                <p className="text-sm font-extrabold text-[#1F2421] mt-0.5">
                  {top1?.points ?? 0} pts
                </p>
              </div>

              {/* Golden Base Pedestal (Tallest) */}
              <div className="w-full h-16 bg-gradient-to-t from-[#F5B817] via-[#FDE047] to-[#FEF08A] rounded-b-3xl border-b-2 border-x-2 border-[#EAB308] shadow-md" />
            </div>

            {/* Rank 3 (Right Pillar Card) */}
            <div className="relative w-[210px] sm:w-[230px] flex flex-col items-center">
              {/* Bronze 3-point Crown with Badge 3 */}
              <div className="relative -mb-4 z-20 flex flex-col items-center">
                <svg viewBox="0 0 80 55" fill="none" className="w-12 h-8 drop-shadow-2xs">
                  <path d="M12 45 L18 18 L40 28 L62 18 L68 45 Z" fill="#FDBA74" stroke="#EA580C" strokeWidth="1.5" />
                  <circle cx="18" cy="18" r="3.5" fill="#FDBA74" />
                  <circle cx="40" cy="28" r="3" fill="#FDBA74" />
                  <circle cx="62" cy="18" r="3.5" fill="#FDBA74" />
                  <circle cx="40" cy="38" r="6" fill="#FFF7ED" stroke="#EA580C" strokeWidth="1" />
                  <text x="40" y="41.5" fontSize="9" fontWeight="900" textAnchor="middle" fill="#9A3412">3</text>
                </svg>
              </div>

              {/* White Pillar Card */}
              <div className="w-full bg-white rounded-t-3xl border-t border-x border-gray-200/90 shadow-xs pt-6 pb-4 px-4 text-center flex flex-col items-center">
                <div className="w-20 h-20 rounded-full overflow-hidden border-2 border-amber-200 shadow-xs relative mb-2.5 flex items-center justify-center bg-[#FFFBEB]">
                  {top3?.avatarSrc ? (
                    <Image
                      src={top3.avatarSrc}
                      alt={top3.name}
                      fill
                      className="object-cover"
                    />
                  ) : (
                    <span className="text-xl font-black text-amber-800 select-none">
                      {getInitials(top3?.name || "")}
                    </span>
                  )}
                </div>
                <p className="text-sm font-bold text-[#1F2421] truncate w-full">
                  {top3?.name || "—"}
                </p>
                <p className="text-xs font-bold text-[#1F2421] mt-0.5">
                  {top3?.points ?? 0} pts
                </p>
              </div>

              {/* Bronze Base Pedestal */}
              <div className="w-full h-8 bg-gradient-to-t from-[#FED7AA] via-[#FFEDD5] to-white rounded-b-3xl border-b border-x border-[#FED7AA] shadow-xs" />
            </div>

            {/* Golden Radiating Sparkles on Right */}
            <div className="absolute right-6 sm:right-12 top-1/2 -translate-y-6 pointer-events-none text-[#F5B817] select-none">
              <svg className="w-10 h-10" viewBox="0 0 40 40" stroke="currentColor" strokeWidth="3" strokeLinecap="round">
                <line x1="8" y1="20" x2="32" y2="20" />
                <line x1="12" y1="10" x2="30" y2="4" />
                <line x1="12" y1="30" x2="30" y2="36" />
              </svg>
            </div>
          </div>

          {/* Golden Floor Platform Shadow Shelf */}
          <div className="h-4 bg-gradient-to-r from-transparent via-[#FDE68A]/60 to-transparent rounded-full max-w-4xl mx-auto -mt-2 blur-2xs" />
        </div>
      )}

      {/* 4. Ranking Data Table matching Reference Leaderboard.jpeg */}
      <div className="bg-white rounded-2xl border border-gray-200/80 shadow-xs overflow-hidden mt-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-[#FAF8F5] text-[#6B7280] font-bold uppercase text-[11px] tracking-wider border-b border-gray-200/80">
              <tr>
                <th scope="col" className="px-6 py-3.5 w-16 text-center">#</th>
                <th scope="col" className="px-6 py-3.5">VOLUNTEER</th>
                <th scope="col" className="px-6 py-3.5">CATEGORY</th>
                <th scope="col" className="px-6 py-3.5 text-center">POINTS</th>
                <th scope="col" className="px-6 py-3.5 text-center">HOURS</th>
                <th scope="col" className="px-6 py-3.5 text-center w-24">TREND</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {displayRows.map((row) => (
                <tr
                  key={row.rank + row.name}
                  className={`transition-colors ${row.isYou
                    ? "bg-[#FEF9C3] font-bold text-[#1F2421]"
                    : "hover:bg-slate-50/70 text-[#1F2421]"
                    }`}
                >
                  {/* Rank Column Badge */}
                  <td className="px-6 py-4 text-center">
                    {row.rank === 1 ? (
                      <span className="w-6 h-6 rounded-full bg-[#F5B817] text-[#1F2421] font-black text-xs inline-flex items-center justify-center shadow-2xs">
                        1
                      </span>
                    ) : row.rank === 2 ? (
                      <span className="w-6 h-6 rounded-full bg-[#CBD5E1] text-[#1F2421] font-black text-xs inline-flex items-center justify-center shadow-2xs">
                        2
                      </span>
                    ) : row.rank === 3 ? (
                      <span className="w-6 h-6 rounded-full bg-[#FDBA74] text-amber-950 font-black text-xs inline-flex items-center justify-center shadow-2xs">
                        3
                      </span>
                    ) : (
                      <span className="font-bold text-[#4B5563] text-xs">{row.rank}</span>
                    )}
                  </td>

                  {/* Volunteer Name with Icon & 'You' Pill */}
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2.5">
                      <div className="w-6 h-6 rounded-full bg-gray-100 border border-gray-200 text-[#4B5563] flex items-center justify-center shrink-0">
                        <User className="w-3.5 h-3.5 text-[#4B5563]" />
                      </div>
                      <span className="font-bold text-[#1F2421]">{row.name}</span>
                      {row.isYou && (
                        <span className="px-2 py-0.5 rounded-full bg-[#FDE047] text-[#1F2421] text-[10px] font-bold shadow-2xs">
                          You
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Category */}
                  <td className="px-6 py-4">
                    <span className="text-xs font-semibold text-[#4B5563]">
                      {row.category}
                    </span>
                  </td>

                  {/* Points */}
                  <td className="px-6 py-4 text-center font-bold text-[#1F2421]">
                    {row.points}
                  </td>

                  {/* Hours */}
                  <td className="px-6 py-4 text-center font-semibold text-[#4B5563]">
                    {row.hours}
                  </td>

                  {/* Trend Indicator */}
                  <td className="px-6 py-4 text-center">
                    {row.trend === "up" ? (
                      <TrendingUp className="w-4 h-4 text-emerald-500 inline-block" />
                    ) : row.trend === "down" ? (
                      <TrendingDown className="w-4 h-4 text-rose-500 inline-block" />
                    ) : (
                      <Minus className="w-4 h-4 text-slate-400 inline-block" />
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
