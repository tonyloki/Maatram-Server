"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import {
  Calendar,
  Clock,
  MapPin,
  CheckCircle2,
  Hourglass,
  UserCheck,
  ChevronRight,
  Award,
  Clock3,
  Coins,
  History,
  AlertCircle,
  Loader2,
  ArrowUpRight,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import {
  RegistrationResponse,
  RegistrationListResponse,
  AttendanceRecordResponse,
  AttendanceListResponse,
  PointLedgerResponse,
  PointTransactionResponse,
} from "@/types";
import { fadeInUp, staggerContainer } from "@/lib/animations";

type ActivityTab = "UPCOMING" | "ONGOING" | "PAST" | "LEDGER";

export default function VolunteerActivityPage() {
  const [activeTab, setActiveTab] = useState<ActivityTab>("UPCOMING");
  const [registrations, setRegistrations] = useState<RegistrationResponse[]>([]);
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecordResponse[]>([]);
  const [ledgerData, setLedgerData] = useState<PointLedgerResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [regRes, attRes, ledRes] = await Promise.all([
        apiClient<RegistrationListResponse>("/registrations/me", { params: { page: 1, page_size: 100 } }).catch(
          () => ({ items: [], total: 0, page: 1, page_size: 100, total_pages: 1 })
        ),
        apiClient<AttendanceListResponse>("/attendance/me", { params: { page: 1, page_size: 100 } }).catch(() => ({
          items: [],
          total: 0,
          page: 1,
          page_size: 100,
          total_pages: 1,
        })),
        apiClient<PointLedgerResponse>("/gamification/ledger", { params: { page: 1, page_size: 50 } }).catch(
          () => null
        ),
      ]);

      setRegistrations(regRes.items || []);
      setAttendanceRecords(attRes.items || []);
      setLedgerData(ledRes);
    } catch (err: unknown) {
      console.error("Failed to load activity", err);
      setError("Unable to load activity history at this time.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const now = Date.now();

  // Categorize registrations
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
    return start < now && end > now;
  });

  const pastRegistrations = registrations.filter((r) => {
    if (["WITHDRAWN", "DECLINED"].includes(r.status)) return false;
    if (!r.event?.end_time) return false;
    return new Date(r.event.end_time).getTime() <= now;
  });

  const getCategoryImage = (category?: string) => {
    switch (category) {
      case "SCHOOL_VISIT":
        return "/images/events/school-visit.png";
      case "MOCK_INTERVIEW":
        return "/images/events/mock-interview.png";
      case "BGV":
      case "BGV_SUPPORT":
        return "/images/events/bgv-support.png";
      default:
        return "/images/events/school-visit.png";
    }
  };

  const formatEventDate = (isoStr?: string) => {
    if (!isoStr) return "";
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });
    } catch {
      return isoStr;
    }
  };

  const formatEventTime = (startIso?: string, endIso?: string) => {
    if (!startIso || !endIso) return "";
    try {
      const s = new Date(startIso);
      const e = new Date(endIso);
      const startTime = s.toLocaleTimeString("en-IN", { hour: "numeric", minute: "2-digit", hour12: true });
      const endTime = e.toLocaleTimeString("en-IN", { hour: "numeric", minute: "2-digit", hour12: true });
      return `${startTime} - ${endTime}`;
    } catch {
      return "";
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "SELECTED":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Selected
          </span>
        );
      case "WAITLISTED":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200">
            <Hourglass className="w-3 h-3 text-amber-600" /> Waitlisted
          </span>
        );
      case "SUBSCRIBED":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md bg-sky-50 text-sky-800 border border-sky-200">
            <UserCheck className="w-3 h-3 text-sky-600" /> Subscribed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md bg-charcoal-100 text-charcoal-700">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Page Title */}
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-charcoal-900 tracking-tight font-serif">
          My Activity
        </h1>
        <p className="text-sm text-charcoal-500 mt-1">
          Review your enrolled events, attendance confirmations, and verified gamification points ledger.
        </p>
      </div>

      {/* Primary Pill Navigation (Matches Reference Screen 3) */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        <button
          onClick={() => setActiveTab("UPCOMING")}
          className={`px-4 py-2 rounded-xl text-xs md:text-sm font-bold transition-all whitespace-nowrap ${
            activeTab === "UPCOMING"
              ? "bg-primary-500 text-charcoal-950 shadow-xs ring-1 ring-primary-500"
              : "bg-white border border-charcoal-200/80 text-charcoal-600 hover:bg-charcoal-50"
          }`}
        >
          Upcoming ({upcomingRegistrations.length})
        </button>
        <button
          onClick={() => setActiveTab("ONGOING")}
          className={`px-4 py-2 rounded-xl text-xs md:text-sm font-bold transition-all whitespace-nowrap ${
            activeTab === "ONGOING"
              ? "bg-primary-500 text-charcoal-950 shadow-xs ring-1 ring-primary-500"
              : "bg-white border border-charcoal-200/80 text-charcoal-600 hover:bg-charcoal-50"
          }`}
        >
          Ongoing ({ongoingRegistrations.length})
        </button>
        <button
          onClick={() => setActiveTab("PAST")}
          className={`px-4 py-2 rounded-xl text-xs md:text-sm font-bold transition-all whitespace-nowrap ${
            activeTab === "PAST"
              ? "bg-primary-500 text-charcoal-950 shadow-xs ring-1 ring-primary-500"
              : "bg-white border border-charcoal-200/80 text-charcoal-600 hover:bg-charcoal-50"
          }`}
        >
          Past ({pastRegistrations.length + attendanceRecords.length})
        </button>
        <button
          onClick={() => setActiveTab("LEDGER")}
          className={`px-4 py-2 rounded-xl text-xs md:text-sm font-bold transition-all whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "LEDGER"
              ? "bg-primary-500 text-charcoal-950 shadow-xs ring-1 ring-primary-500"
              : "bg-white border border-charcoal-200/80 text-charcoal-600 hover:bg-charcoal-50"
          }`}
        >
          <Coins className="w-3.5 h-3.5" />
          Points Ledger
        </button>
      </div>

      {/* Content Area */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-charcoal-200/80">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm font-medium text-charcoal-500 mt-3">Loading your volunteering activity...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center text-red-700">
          <AlertCircle className="w-8 h-8 mx-auto text-red-500 mb-2" />
          <p className="font-semibold">{error}</p>
          <button
            onClick={loadData}
            className="mt-3 px-4 py-1.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      ) : activeTab === "LEDGER" ? (
        /* Financial-Grade Points Ledger View */
        <div className="space-y-6">
          {/* Summary KPIs */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-charcoal-200/80 shadow-xs">
              <span className="text-xs font-bold uppercase text-charcoal-400 tracking-wider">Net Points Balance</span>
              <div className="flex items-center gap-2 mt-2">
                <Coins className="w-6 h-6 text-amber-500" />
                <span className="text-3xl font-extrabold text-charcoal-900">{ledgerData?.net_points ?? 0}</span>
                <span className="text-xs font-semibold text-charcoal-500">pts</span>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-charcoal-200/80 shadow-xs">
              <span className="text-xs font-bold uppercase text-charcoal-400 tracking-wider">Verified Events</span>
              <div className="flex items-center gap-2 mt-2">
                <Award className="w-6 h-6 text-emerald-600" />
                <span className="text-3xl font-extrabold text-charcoal-900">
                  {attendanceRecords.filter((a) => a.status === "ATTENDED").length}
                </span>
                <span className="text-xs font-semibold text-charcoal-500">completed</span>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-charcoal-200/80 shadow-xs">
              <span className="text-xs font-bold uppercase text-charcoal-400 tracking-wider">Total Verified Hours</span>
              <div className="flex items-center gap-2 mt-2">
                <Clock3 className="w-6 h-6 text-primary-600" />
                <span className="text-3xl font-extrabold text-charcoal-900">
                  {attendanceRecords.reduce((acc, a) => acc + Number(a.hours_credited || 0), 0)}
                </span>
                <span className="text-xs font-semibold text-charcoal-500">hours</span>
              </div>
            </div>
          </div>

          {/* Ledger Table */}
          <div className="bg-white rounded-2xl border border-charcoal-200/80 overflow-hidden shadow-xs">
            <div className="p-4 border-b border-charcoal-200/80 flex items-center justify-between">
              <h3 className="font-bold text-charcoal-900 text-sm md:text-base flex items-center gap-2">
                <History className="w-4 h-4 text-primary-600" />
                Point Transactions & Audit Ledger
              </h3>
              <span className="text-xs text-charcoal-400">Strictly append-only canonical ledger</span>
            </div>

            {!ledgerData || ledgerData.items.length === 0 ? (
              <div className="p-12 text-center text-charcoal-500 text-sm">
                No point transactions recorded yet. Complete volunteering events to earn verified points!
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs md:text-sm text-charcoal-700">
                  <thead className="bg-charcoal-50 border-b border-charcoal-200 text-charcoal-500 uppercase tracking-wider text-[11px] font-bold">
                    <tr>
                      <th className="py-3 px-4">Date</th>
                      <th className="py-3 px-4">Activity / Reason</th>
                      <th className="py-3 px-4 text-right">Hours</th>
                      <th className="py-3 px-4 text-right">Event Pts</th>
                      <th className="py-3 px-4 text-right">Hour Pts</th>
                      <th className="py-3 px-4 text-right">Total Net</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-charcoal-100">
                    {ledgerData.items.map((tx) => (
                      <tr key={tx.id} className="hover:bg-charcoal-50/50 transition-colors">
                        <td className="py-3 px-4 whitespace-nowrap text-charcoal-600">
                          {formatEventDate(tx.created_at)}
                        </td>
                        <td className="py-3 px-4 font-semibold text-charcoal-900">
                          {tx.reason || tx.transaction_type.replace("_", " ")}
                        </td>
                        <td className="py-3 px-4 text-right font-medium text-charcoal-600">
                          {tx.hours_credited ? `${tx.hours_credited} hrs` : "—"}
                        </td>
                        <td className="py-3 px-4 text-right font-medium text-emerald-700">
                          +{Number(tx.event_points || 0)}
                        </td>
                        <td className="py-3 px-4 text-right font-medium text-emerald-700">
                          +{Number(tx.hour_points || 0)}
                        </td>
                        <td className="py-3 px-4 text-right font-bold text-charcoal-900">
                          +{Number(tx.total_points || 0)} pts
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Event Cards List (Matching Screen 3) */
        <div>
          {(() => {
            const list =
              activeTab === "UPCOMING"
                ? upcomingRegistrations
                : activeTab === "ONGOING"
                ? ongoingRegistrations
                : pastRegistrations;

            if (list.length === 0) {
              return (
                <div className="bg-white rounded-2xl border border-charcoal-200/80 p-12 text-center">
                  <div className="w-12 h-12 bg-charcoal-100 rounded-full flex items-center justify-center mx-auto text-charcoal-500 mb-3">
                    <Calendar className="w-6 h-6" />
                  </div>
                  <h3 className="text-base font-bold text-charcoal-900">
                    No {activeTab.toLowerCase()} activities
                  </h3>
                  <p className="text-sm text-charcoal-500 mt-1 max-w-sm mx-auto">
                    {activeTab === "UPCOMING"
                      ? "You haven't subscribed to any upcoming events yet. Discover available events and register today!"
                      : activeTab === "ONGOING"
                      ? "You do not have any events currently underway right now."
                      : "You haven't completed any volunteering events yet."}
                  </p>
                  {activeTab === "UPCOMING" && (
                    <Link
                      href="/volunteer/events"
                      className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 bg-primary-500 text-charcoal-950 font-bold rounded-xl text-sm shadow-xs hover:bg-primary-400 transition-colors"
                    >
                      Discover Events <ArrowUpRight className="w-4 h-4" />
                    </Link>
                  )}
                </div>
              );
            }

            return (
              <motion.div
                variants={staggerContainer}
                initial="hidden"
                animate="visible"
                className="space-y-4"
              >
                {list.map((reg) => {
                  const event = reg.event;
                  const eventTitle = event?.title || "Volunteering Initiative";
                  const eventCategory = event?.category || "OTHER";
                  const eventLocation = event?.location || "Chennai";

                  return (
                    <motion.div
                      key={reg.id}
                      variants={fadeInUp}
                      className="bg-white rounded-2xl border border-charcoal-200/70 hover:border-primary-300 p-4 md:p-5 shadow-xs hover:shadow-sm transition-all flex flex-col md:flex-row items-start md:items-center gap-4 md:gap-6 justify-between group"
                    >
                      {/* Left Thumbnail */}
                      <div className="relative w-full md:w-36 h-32 md:h-24 rounded-xl overflow-hidden flex-shrink-0 bg-charcoal-100 border border-charcoal-200/60">
                        <Image
                          src={getCategoryImage(eventCategory)}
                          alt={eventTitle}
                          fill
                          className="object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      </div>

                      {/* Middle Details */}
                      <div className="flex-1 min-w-0 space-y-2">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <h2 className="text-base md:text-lg font-bold text-charcoal-900 tracking-tight group-hover:text-primary-800 transition-colors">
                            {eventTitle}
                          </h2>
                        </div>

                        {/* Date, Time & Location Line */}
                        <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs md:text-sm text-charcoal-600">
                          <span className="flex items-center gap-1.5 font-medium">
                            <Calendar className="w-3.5 h-3.5 text-primary-600" />
                            {formatEventDate(event?.start_time)}
                          </span>
                          <span className="flex items-center gap-1.5 font-medium">
                            <Clock className="w-3.5 h-3.5 text-primary-600" />
                            {formatEventTime(event?.start_time, event?.end_time)}
                          </span>
                          <span className="flex items-center gap-1.5 font-medium">
                            <MapPin className="w-3.5 h-3.5 text-primary-600" />
                            {eventLocation}
                          </span>
                        </div>

                        {/* Status Badge */}
                        <div className="pt-0.5">{getStatusBadge(reg.status)}</div>
                      </div>

                      {/* Right Action */}
                      <div className="w-full md:w-auto flex-shrink-0 pt-2 md:pt-0">
                        <Link
                          href={`/volunteer/events/${reg.event_id}`}
                          className="w-full md:w-auto inline-flex items-center justify-center gap-1.5 px-5 py-2.5 rounded-xl border border-charcoal-200 hover:border-charcoal-400 bg-white hover:bg-charcoal-50 text-charcoal-800 text-sm font-semibold shadow-xs hover:shadow-sm transition-all"
                        >
                          View Details
                          <ChevronRight className="w-4 h-4 text-charcoal-400 group-hover:translate-x-0.5 transition-transform" />
                        </Link>
                      </div>
                    </motion.div>
                  );
                })}
              </motion.div>
            );
          })()}
        </div>
      )}
    </div>
  );
}

