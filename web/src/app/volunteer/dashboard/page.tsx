"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { format } from "date-fns";
import {
  Sparkles,
  Trophy,
  Clock,
  Calendar,
  CheckCircle2,
  ArrowRight,
  Compass,
  AlertCircle,
  Video,
  MapPin,
  Award,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import {
  VolunteerProfileResponse,
  GamificationSummaryResponse,
  RegistrationListResponse,
  RegistrationResponse,
} from "@/types";

export default function VolunteerDashboardPage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<VolunteerProfileResponse | null>(null);
  const [summary, setSummary] = useState<GamificationSummaryResponse | null>(null);
  const [upcomingRegs, setUpcomingRegs] = useState<RegistrationResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Parallel fetches for profile, gamification metrics, and user registrations
      const [profileData, summaryData, regData] = await Promise.allSettled([
        apiClient<VolunteerProfileResponse>("/volunteers/me"),
        apiClient<GamificationSummaryResponse>("/gamification/summary"),
        apiClient<RegistrationListResponse>("/registrations/me", { params: { limit: 5 } }),
      ]);

      if (profileData.status === "fulfilled") {
        setProfile(profileData.value);
      }
      if (summaryData.status === "fulfilled") {
        setSummary(summaryData.value);
      }
      if (regData.status === "fulfilled") {
        // Filter upcoming registrations (events with start_time in future or status != WITHDRAWN)
        setUpcomingRegs(regData.value.items || []);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load dashboard metrics.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDashboardData();
  }, [loadDashboardData]);

  const displayName = profile ? `${profile.first_name} ${profile.last_name}` : user?.email?.split("@")[0] || "Volunteer";
  const volunteerCategory = profile?.category || "VOLUNTEER";

  return (
    <div className="space-y-8">
      {/* 1. WELCOME SECTION */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-[#EBE6DD] shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-bold text-[#B45309] uppercase tracking-wider bg-[#FFF8E7] px-3 py-1 rounded-full border border-[#F5B817]/40">
              {volunteerCategory} Volunteer
            </span>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#F0FDF4] text-[#15803D] border border-[#BBF7D0]">
              Status: {user?.status || "APPROVED"}
            </span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1F2421]">
            Welcome back, {displayName}!
          </h1>
          <p className="text-sm text-[#6B7280]">
            Thank you for mentoring scholars and supporting higher education access.
          </p>
        </div>

        <Link href="/volunteer/events">
          <Button variant="primary" size="md" className="font-bold shadow-md shadow-[#F5B817]/25">
            <Compass className="w-4 h-4 mr-2" />
            <span>Discover Opportunities</span>
          </Button>
        </Link>
      </div>

      {/* ERROR NOTICE */}
      {error && (
        <div className="p-4 rounded-2xl bg-[#FEF2F2] border border-[#F87171] text-xs text-[#991B1B] flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <Button variant="outline" size="sm" onClick={() => loadDashboardData()}>
            Retry
          </Button>
        </div>
      )}

      {/* 2. CONTRIBUTION OVERVIEW (KPI CARDS) */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-[#1F2421]">Contribution Overview</h2>
          <span className="text-xs text-[#6B7280]">
            Cycle Year: {summary?.cycle_year || new Date().getFullYear()}
          </span>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((n) => (
              <div key={n} className="bg-white rounded-2xl p-6 border border-[#EBE6DD] animate-pulse space-y-3">
                <div className="h-4 bg-gray-200 rounded w-1/2" />
                <div className="h-8 bg-gray-200 rounded w-3/4" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Points */}
            <Card className="p-5 bg-white border-[#EBE6DD] flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-[#6B7280] block mb-1">
                  Volunteering Points
                </span>
                <span className="text-2xl sm:text-3xl font-extrabold text-[#1F2421]">
                  {summary ? Number(summary.total_points).toFixed(0) : "0"}
                </span>
                <span className="text-[11px] text-[#946C00] font-medium block mt-1">
                  P = (E × 10) + (H × 2)
                </span>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-[#FFF8E7] text-[#946C00] flex items-center justify-center shrink-0 border border-[#F5B817]/30">
                <Trophy className="w-6 h-6" />
              </div>
            </Card>

            {/* Approved Hours */}
            <Card className="p-5 bg-white border-[#EBE6DD] flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-[#6B7280] block mb-1">
                  Approved Hours
                </span>
                <span className="text-2xl sm:text-3xl font-extrabold text-[#1F2421]">
                  {summary ? Number(summary.total_hours).toFixed(1) : "0.0"}
                </span>
                <span className="text-[11px] text-[#15803D] font-medium block mt-1">
                  Verified Service
                </span>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-[#F0FDF4] text-[#15803D] flex items-center justify-center shrink-0 border border-[#86EFAC]/40">
                <Clock className="w-6 h-6" />
              </div>
            </Card>

            {/* Events Attended */}
            <Card className="p-5 bg-white border-[#EBE6DD] flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-[#6B7280] block mb-1">
                  Events Attended
                </span>
                <span className="text-2xl sm:text-3xl font-extrabold text-[#1F2421]">
                  {summary?.completed_events_count || 0}
                </span>
                <span className="text-[11px] text-[#1D4ED8] font-medium block mt-1">
                  Completed Drives
                </span>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-[#EFF6FF] text-[#1D4ED8] flex items-center justify-center shrink-0 border border-[#93C5FD]/40">
                <Calendar className="w-6 h-6" />
              </div>
            </Card>

            {/* Leaderboard Rank */}
            <Card className="p-5 bg-white border-[#EBE6DD] flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-[#6B7280] block mb-1">
                  Current Rank
                </span>
                <span className="text-2xl sm:text-3xl font-extrabold text-[#1F2421]">
                  {summary?.rank ? `#${summary.rank}` : "—"}
                </span>
                <Link
                  href="/volunteer/leaderboard"
                  className="text-[11px] text-[#B45309] font-semibold hover:underline block mt-1"
                >
                  View Leaderboard →
                </Link>
              </div>
              <div className="w-12 h-12 rounded-2xl bg-[#FAF8F3] text-[#B45309] flex items-center justify-center shrink-0 border border-[#EBE6DD]">
                <Award className="w-6 h-6" />
              </div>
            </Card>
          </div>
        )}
      </div>

      {/* 3. UPCOMING PARTICIPATION & ACTIVITY */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Upcoming Registrations */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-[#1F2421]">My Upcoming Participation</h2>
            <Link
              href="/volunteer/activity"
              className="text-xs font-bold text-[#B45309] hover:underline"
            >
              All Activity History →
            </Link>
          </div>

          {isLoading ? (
            <div className="bg-white rounded-2xl p-6 border border-[#EBE6DD] animate-pulse space-y-4">
              <div className="h-6 bg-gray-200 rounded w-1/3" />
              <div className="h-12 bg-gray-100 rounded" />
            </div>
          ) : upcomingRegs.length === 0 ? (
            <Card className="p-8 text-center bg-white border-[#EBE6DD] space-y-3">
              <Calendar className="w-10 h-10 text-[#9CA3AF] mx-auto" />
              <h3 className="text-sm font-bold text-[#1F2421]">No Upcoming Event Registrations</h3>
              <p className="text-xs text-[#6B7280] max-w-sm mx-auto">
                You have not registered for any upcoming volunteering drives yet. Explore published opportunities to start contributing!
              </p>
              <div className="pt-2">
                <Link href="/volunteer/events">
                  <Button variant="primary" size="sm">
                    Browse Opportunities
                  </Button>
                </Link>
              </div>
            </Card>
          ) : (
            <div className="space-y-3">
              {upcomingRegs.map((reg) => {
                const eventInfo = reg.event;
                const statusColor =
                  reg.status === "SELECTED"
                    ? "bg-[#F0FDF4] text-[#15803D] border-[#86EFAC]"
                    : reg.status === "SUBSCRIBED"
                    ? "bg-[#FFF8E7] text-[#946C00] border-[#F5B817]/40"
                    : reg.status === "WAITLISTED"
                    ? "bg-[#EFF6FF] text-[#1D4ED8] border-[#93C5FD]"
                    : "bg-[#F3F4F6] text-[#4B5563] border-[#E5E7EB]";

                return (
                  <Card
                    key={reg.id}
                    className="p-5 bg-white border-[#EBE6DD] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:shadow-xs transition-shadow"
                  >
                    <div className="space-y-1.5 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${statusColor}`}
                        >
                          {reg.status}
                        </span>
                        {eventInfo && (
                          <span className="text-xs text-[#6B7280] font-medium">
                            {eventInfo.category.replace(/_/g, " ")} • {eventInfo.mode}
                          </span>
                        )}
                      </div>

                      <h3 className="text-base font-bold text-[#1F2421]">
                        {eventInfo?.title || "Volunteering Opportunity"}
                      </h3>

                      {eventInfo && (
                        <div className="flex flex-wrap items-center gap-4 text-xs text-[#6B7280]">
                          <div className="flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5 text-[#F5B817]" />
                            <span>
                              {format(new Date(eventInfo.start_time), "dd MMM yyyy, hh:mm a")}
                            </span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            {eventInfo.mode === "ONLINE" ? (
                              <>
                                <Video className="w-3.5 h-3.5 text-[#F5B817]" />
                                <span>Online Session</span>
                              </>
                            ) : (
                              <>
                                <MapPin className="w-3.5 h-3.5 text-[#F5B817]" />
                                <span className="truncate max-w-[200px]">{eventInfo.location}</span>
                              </>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    <Link href={`/volunteer/events/${reg.event_id}`}>
                      <Button variant="outline" size="sm" className="shrink-0 w-full sm:w-auto">
                        <span>Details</span>
                        <ArrowRight className="w-3.5 h-3.5 ml-1" />
                      </Button>
                    </Link>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        {/* Right: Quick Shortcuts & Guidance */}
        <div className="lg:col-span-4 space-y-4">
          <h2 className="text-lg font-bold text-[#1F2421]">Volunteering Guide</h2>

          <Card className="p-6 bg-white border-[#EBE6DD] space-y-4 shadow-xs">
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-[#1F2421]">How Selection Works</h3>
              <p className="text-xs text-[#6B7280] leading-relaxed">
                When you apply for an event, your status is <span className="font-semibold text-[#B45309]">SUBSCRIBED</span>. Event coordinators select attendees based on subject expertise and capacity.
              </p>
            </div>

            <div className="pt-2 border-t border-[#EBE6DD] space-y-2 text-xs">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#15803D] shrink-0 mt-0.5" />
                <span>Selected volunteers receive session coordination via WhatsApp/Email.</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#15803D] shrink-0 mt-0.5" />
                <span>Check-in and check-out are logged digitally at each event.</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-[#15803D] shrink-0 mt-0.5" />
                <span>Points and hours are credited directly to your profile.</span>
              </div>
            </div>

            <div className="pt-2 border-t border-[#EBE6DD]">
              <Link href="/volunteer/profile">
                <Button variant="outline" size="sm" className="w-full justify-between">
                  <span>Manage Profile & Consents</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

