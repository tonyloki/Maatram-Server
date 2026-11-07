"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import Image from "next/image";
import { format } from "date-fns";
import {
  Calendar,
  Clock,
  MapPin,
  Video,
  CheckCircle2,
  Star,
  BarChart2,
  Search,
  ArrowRight,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import {
  RegistrationResponse,
  RegistrationListResponse,
  AttendanceRecordResponse,
  AttendanceListResponse,
  PointLedgerResponse,
} from "@/types";

type ActivityTab = "UPCOMING" | "ONGOING" | "PAST" | "LEDGER";

export default function VolunteerActivityPage() {
  const [activeTab, setActiveTab] = useState<ActivityTab>("UPCOMING");
  const [registrations, setRegistrations] = useState<RegistrationResponse[]>([]);
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecordResponse[]>([]);
  const [ledgerData, setLedgerData] = useState<PointLedgerResponse | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [regRes, attRes, ledRes] = await Promise.all([
        apiClient<RegistrationListResponse>("/registrations/me", { params: { page: 1, page_size: 100 } }),
        apiClient<AttendanceListResponse>("/attendance/me", { params: { page: 1, page_size: 100 } }),
        apiClient<PointLedgerResponse>("/gamification/ledger", { params: { page: 1, page_size: 50 } }),
      ]);

      setRegistrations(regRes.items || []);
      setAttendanceRecords(attRes.items || []);
      setLedgerData(ledRes);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Unable to retrieve your volunteering activity.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const now = Date.now();

  const upcomingRegistrations = registrations.filter((r) => {
    if (["WITHDRAWN", "DECLINED"].includes(r.status)) return false;
    if (!r.event?.start_time) return true;
    return new Date(r.event.start_time).getTime() >= now;
  });

  const ongoingRegistrations = registrations.filter((r) => {
    if (["WITHDRAWN", "DECLINED"].includes(r.status)) return false;
    if (!r.event?.start_time || !r.event?.end_time) return false;
    const start = new Date(r.event.start_time).getTime();
    const end = new Date(r.event.end_time).getTime();
    return start <= now && end >= now;
  });

  const pastRegistrations = registrations.filter((r) => {
    if (["WITHDRAWN", "DECLINED"].includes(r.status)) return false;
    if (!r.event?.end_time) return false;
    return new Date(r.event.end_time).getTime() < now;
  });

  const currentList =
    activeTab === "UPCOMING"
      ? upcomingRegistrations
      : activeTab === "ONGOING"
      ? ongoingRegistrations
      : pastRegistrations;

  return (
    <div className="space-y-6 sm:space-y-7 animate-in fade-in-50 duration-300 pb-10 overflow-x-hidden min-w-0 max-w-full">
      {/* 1. Curved Golden Hero Banner */}
      <section
        aria-label="My Activity Hero"
        className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#FFFDF5] via-[#FFF3D6] to-[#FCEFC7] border border-[#FDE68A]/70 px-8 py-6 shadow-xs min-h-[175px] flex items-center justify-between"
      >
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

        <div className="absolute right-0 bottom-0 top-0 w-1/2 max-w-[560px] pointer-events-none select-none z-10 hidden md:block overflow-hidden rounded-r-3xl">
          <Image
            src="/assets/maatram/photography/volunteers-team-hero.jpg"
            alt="Maatram volunteer community"
            fill
            className="object-cover object-center"
            priority
          />
          <div className="absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-[#FFF3D6] to-transparent z-10" />
        </div>

        <div className="relative z-10 max-w-lg space-y-1.5">
          <div className="flex items-center gap-1 text-[#F5B817]">
            <svg className="w-6 h-6" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="12" y1="4" x2="12" y2="10" />
              <line x1="5" y1="7" x2="10" y2="12" />
              <line x1="19" y1="7" x2="14" y2="12" />
            </svg>
          </div>

          <h1 className="font-serif text-3xl sm:text-4xl font-extrabold text-[#1F2421] tracking-tight">
            My Activity
          </h1>

          <p className="text-xs sm:text-sm text-[#4B5563] leading-relaxed max-w-md pt-0.5">
            Track your registered volunteering drives, service attendance records and points history.
          </p>
        </div>
      </section>

      {/* 2. Horizontal Activity Tabs */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
          <button
            onClick={() => setActiveTab("UPCOMING")}
            className={`px-5 py-2.5 rounded-full text-xs transition-all flex items-center gap-2 ${
              activeTab === "UPCOMING"
                ? "bg-[#F5B817] text-[#1F2421] font-extrabold shadow-2xs"
                : "bg-white text-[#1F2421] font-semibold border border-gray-200/90 hover:bg-[#FFFDF5] hover:border-amber-200"
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>Upcoming {!isLoading && `(${upcomingRegistrations.length})`}</span>
          </button>

          <button
            onClick={() => setActiveTab("ONGOING")}
            className={`px-5 py-2.5 rounded-full text-xs transition-all flex items-center gap-2 ${
              activeTab === "ONGOING"
                ? "bg-[#F5B817] text-[#1F2421] font-extrabold shadow-2xs"
                : "bg-white text-[#1F2421] font-semibold border border-gray-200/90 hover:bg-[#FFFDF5] hover:border-amber-200"
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Ongoing {!isLoading && `(${ongoingRegistrations.length})`}</span>
          </button>

          <button
            onClick={() => setActiveTab("PAST")}
            className={`px-5 py-2.5 rounded-full text-xs transition-all flex items-center gap-2 ${
              activeTab === "PAST"
                ? "bg-[#F5B817] text-[#1F2421] font-extrabold shadow-2xs"
                : "bg-white text-[#1F2421] font-semibold border border-gray-200/90 hover:bg-[#FFFDF5] hover:border-amber-200"
            }`}
          >
            <Star className="w-3.5 h-3.5" />
            <span>Past {!isLoading && `(${pastRegistrations.length})`}</span>
          </button>

          <button
            onClick={() => setActiveTab("LEDGER")}
            className={`px-5 py-2.5 rounded-full text-xs transition-all flex items-center gap-2 ${
              activeTab === "LEDGER"
                ? "bg-[#F5B817] text-[#1F2421] font-extrabold shadow-2xs"
                : "bg-white text-[#1F2421] font-semibold border border-gray-200/90 hover:bg-[#FFFDF5] hover:border-amber-200"
            }`}
          >
            <BarChart2 className="w-3.5 h-3.5" />
            <span>Points Ledger</span>
          </button>
        </div>

        <button
          onClick={() => void loadData()}
          disabled={isLoading}
          className="p-2.5 rounded-full bg-white border border-gray-200/90 text-charcoal-700 hover:text-charcoal-900 shadow-2xs transition-all"
          title="Refresh activities"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* 3. Main Content Display Area: Loading / Error / Empty / Populated */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-white rounded-2xl p-6 border border-gray-200/80 animate-pulse space-y-3"
            >
              <div className="flex gap-2">
                <div className="h-5 w-24 bg-gray-200 rounded-full" />
                <div className="h-5 w-20 bg-gray-200 rounded-full" />
              </div>
              <div className="h-6 w-1/2 bg-gray-200 rounded" />
              <div className="h-4 w-1/3 bg-gray-100 rounded" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="bg-white rounded-2xl p-8 border border-rose-200 text-center space-y-4 shadow-xs">
          <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h3 className="text-base font-bold text-charcoal-900">Failed to Load Activity</h3>
            <p className="text-xs text-charcoal-600">{error}</p>
          </div>
          <button
            onClick={() => void loadData()}
            className="px-5 py-2 rounded-xl bg-[#F5B817] text-charcoal-950 font-bold text-xs hover:bg-[#E5AA10] transition-colors"
          >
            Try Again
          </button>
        </div>
      ) : activeTab === "LEDGER" ? (
        /* POINTS LEDGER VIEW */
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-gray-200/80 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 pb-4">
              <div>
                <h3 className="text-base sm:text-lg font-bold text-[#1F2421]">
                  Canonical Gamification Ledger
                </h3>
                <p className="text-xs text-[#6B7280]">
                  Points are computed exclusively from database records: Events × 10 + Approved Hours × 2
                </p>
              </div>
              <div className="px-4 py-2 rounded-2xl bg-[#FFF8E7] border border-[#FDE68A] text-xs font-bold text-[#946C00]">
                P = (E × 10) + (H × 2)
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
              <div className="p-4 rounded-xl bg-[#FAF8F5] border border-gray-200/80">
                <span className="text-xs font-semibold text-[#6B7280]">Total Balance</span>
                <p className="text-2xl font-black text-[#1F2421] mt-1">
                  {ledgerData?.net_points ?? "0.00"} pts
                </p>
              </div>
              <div className="p-4 rounded-xl bg-[#FAF8F5] border border-gray-200/80">
                <span className="text-xs font-semibold text-[#6B7280]">Events Points (E × 10)</span>
                <p className="text-2xl font-black text-[#1F2421] mt-1">
                  {ledgerData?.items?.reduce((sum, tx) => sum + Number(tx.event_points || 0), 0).toFixed(2) ?? "0.00"} pts
                </p>
              </div>
              <div className="p-4 rounded-xl bg-[#FAF8F5] border border-gray-200/80">
                <span className="text-xs font-semibold text-[#6B7280]">Hours Points (H × 2)</span>
                <p className="text-2xl font-black text-[#1F2421] mt-1">
                  {ledgerData?.items?.reduce((sum, tx) => sum + Number(tx.hour_points || 0), 0).toFixed(2) ?? "0.00"} pts
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 sm:p-8 border border-gray-200/80 shadow-xs space-y-4">
            <h4 className="text-sm font-bold text-[#1F2421] uppercase tracking-wider">
              Point Transaction Ledger
            </h4>

            {!ledgerData?.items || ledgerData.items.length === 0 ? (
              <p className="text-xs text-[#6B7280] py-6 text-center">
                No point transactions recorded yet. Complete an event to earn your first points!
              </p>
            ) : (
              <div className="divide-y divide-gray-100">
                {ledgerData.items.map((tx) => (
                  <div key={tx.id} className="py-3.5 flex items-center justify-between text-xs sm:text-sm">
                    <div>
                      <p className="font-bold text-[#1F2421]">
                        {tx.event_id ? "Event Completion Credit" : (tx.reason || "Service Hours Adjustment")}
                      </p>
                      <p className="text-[11px] text-[#6B7280]">
                        {format(new Date(tx.created_at), "d MMM yyyy, h:mm a")}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-[#15803D]">
                        +{Number(tx.total_points || 0)} pts
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : currentList.length === 0 ? (
        /* Empty State */
        <div className="bg-white rounded-3xl border border-gray-200/80 shadow-xs p-12 sm:p-16 text-center flex flex-col items-center justify-center relative overflow-hidden min-h-[420px]">
          <div className="absolute -bottom-16 -left-16 w-56 h-56 rounded-full bg-[#FFF8E7]/60 pointer-events-none" />
          <div className="absolute -bottom-16 -right-16 w-56 h-56 rounded-full bg-[#FFF8E7]/60 pointer-events-none" />

          <div className="relative z-10 w-72 h-44 mb-4">
            <Image
              src="/assets/maatram/illustrations/activity-calendar-clock.svg"
              alt="No activities recorded"
              fill
              className="object-contain"
              priority
            />
          </div>

          <h3 className="relative z-10 text-xl sm:text-2xl font-bold text-[#1F2421] tracking-tight mb-2">
            {activeTab === "UPCOMING"
              ? "No upcoming activities"
              : activeTab === "ONGOING"
              ? "No ongoing activities"
              : "No past activities"}
          </h3>

          <p className="relative z-10 text-xs sm:text-sm text-[#6B7280] max-w-md mb-6 leading-relaxed">
            {activeTab === "UPCOMING"
              ? "You haven't registered for any upcoming events yet. Discover events and start volunteering today!"
              : activeTab === "ONGOING"
              ? "There are no volunteer drives in progress right now. Check back when your scheduled events begin."
              : "You have not completed any volunteering events yet. Your service history will be recorded here."}
          </p>

          <Link
            href="/volunteer/events"
            className="relative z-10 inline-flex items-center gap-2 bg-[#F5B817] hover:bg-[#E5A800] text-[#1F2421] font-bold text-xs sm:text-sm px-6 py-2.5 rounded-full shadow-2xs transition-all transform hover:-translate-y-0.5"
          >
            <Search className="w-4 h-4" />
            <span>Discover Events</span>
            <span>→</span>
          </Link>
        </div>
      ) : (
        /* Registered Activity Cards */
        <div className="space-y-4">
          {currentList.map((reg) => {
            const evt = reg.event;
            const startDate = evt?.start_time ? new Date(evt.start_time) : null;
            const dateStr = startDate ? format(startDate, "d MMM yyyy") : "Scheduled";
            const timeStr = startDate ? format(startDate, "h:mm a") : "";
            const isOnline = evt?.mode === "ONLINE";
            const attendance = attendanceRecords.find((a) => a.event_id === reg.event_id);

            return (
              <div
                key={reg.id}
                className="bg-white rounded-2xl p-5 sm:p-6 border border-gray-200/80 shadow-xs hover:border-[#F5B817]/60 hover:shadow-md transition-all flex flex-col md:flex-row items-stretch md:items-center justify-between gap-5 group"
              >
                <div className="space-y-2.5 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A]">
                      {evt?.category || "VOLUNTEERING"}
                    </span>
                    <span
                      className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                        isOnline
                          ? "bg-[#EDE9FE] text-[#6D28D9] border-[#DDD6FE]"
                          : "bg-[#DCFCE7] text-[#166534] border-[#BBF7D0]"
                      }`}
                    >
                      {isOnline ? "Online" : "Onsite"}
                    </span>
                    <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                      Registration: {reg.status}
                    </span>
                    {attendance && (
                      <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-sky-50 text-sky-800 border border-sky-200">
                        Attendance: {attendance.status} ({attendance.hours_credited} hrs)
                      </span>
                    )}
                  </div>

                  <h3 className="text-base sm:text-lg font-bold text-[#1F2421] group-hover:text-[#946C00] transition-colors">
                    {evt?.title || "Volunteering Drive"}
                  </h3>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-[#6B7280]">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3.5 h-3.5 text-[#F5B817]" />
                      {dateStr}
                    </span>
                    {timeStr && (
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-[#F5B817]" />
                        {timeStr}
                      </span>
                    )}
                    <span className="flex items-center gap-1 truncate max-w-[220px]">
                      {isOnline ? (
                        <>
                          <Video className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                          <span>Google Meet</span>
                        </>
                      ) : (
                        <>
                          <MapPin className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                          <span>{evt?.location || "Chennai Venue"}</span>
                        </>
                      )}
                    </span>
                  </div>
                </div>

                <Link
                  href={`/volunteer/events/${reg.event_id}`}
                  className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-full bg-[#F5B817] hover:bg-[#E5A800] text-[#1F2421] text-xs font-bold shadow-2xs transition-colors shrink-0"
                >
                  <span>View Details</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
