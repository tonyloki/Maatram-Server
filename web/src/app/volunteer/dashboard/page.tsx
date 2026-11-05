"use client";

import React, { useState, useEffect, useCallback } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import {
  VolunteerProfileResponse,
  GamificationSummaryResponse,
  RegistrationListResponse,
  RegistrationResponse,
  EventListResponse,
  EventItem,
} from "@/types";
import { HeroWelcomeBanner } from "@/components/volunteer/dashboard/hero-welcome-banner";
import { ContributionKpiRow } from "@/components/volunteer/dashboard/contribution-kpi-row";
import { UpcomingParticipationCard } from "@/components/volunteer/dashboard/upcoming-participation-card";
import { RecommendedEventsSection } from "@/components/volunteer/dashboard/recommended-events-section";
import { VolunteeringGuideCard } from "@/components/volunteer/dashboard/volunteering-guide-card";
import { ProgressDonutCard } from "@/components/volunteer/dashboard/progress-donut-card";

export default function VolunteerDashboardPage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<VolunteerProfileResponse | null>(null);
  const [summary, setSummary] = useState<GamificationSummaryResponse | null>(null);
  const [upcomingRegs, setUpcomingRegs] = useState<RegistrationResponse[]>([]);
  const [recommendedEvents, setRecommendedEvents] = useState<EventItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Parallel fetches for profile, gamification summary, registrations, and published events
      const [profileData, summaryData, regData, eventsData] = await Promise.allSettled([
        apiClient<VolunteerProfileResponse>("/volunteers/me"),
        apiClient<GamificationSummaryResponse>("/gamification/summary"),
        apiClient<RegistrationListResponse>("/registrations/me", { params: { limit: 5 } }),
        apiClient<EventListResponse>("/events", { params: { limit: 2 } }),
      ]);

      if (profileData.status === "fulfilled") {
        setProfile(profileData.value);
      }
      if (summaryData.status === "fulfilled") {
        setSummary(summaryData.value);
      }
      if (regData.status === "fulfilled") {
        setUpcomingRegs(regData.value.items || []);
      }
      if (eventsData.status === "fulfilled") {
        setRecommendedEvents(eventsData.value.items || []);
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

  const displayName = profile
    ? `${profile.first_name} ${profile.last_name}`.trim()
    : user?.email?.split("@")[0] || "Volunteer";

  const firstName = profile?.first_name || displayName.split(" ")[0];
  const volunteerCategory = profile?.category || user?.role || "STUDENT";
  const userStatus = user?.status || "APPROVED";

  return (
    <div className="space-y-5 sm:space-y-6 animate-in fade-in-50 duration-300">
      {/* Optional Graceful Error Notification */}
      {error && (
        <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 flex items-center justify-between shadow-2xs">
          <div className="flex items-center gap-2.5 text-xs sm:text-sm">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>Some metrics could not be loaded in real time. Showing cached or offline view.</span>
          </div>
          <button
            onClick={() => void loadDashboardData()}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-white border border-amber-300 text-xs font-bold text-amber-900 hover:bg-amber-100 transition-colors shrink-0"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* 1. Curved Golden Welcome / Hero Banner matching Mentor Reference */}
      <HeroWelcomeBanner
        displayName={firstName}
        category={volunteerCategory}
        status={userStatus}
      />

      {/* 2. Your Contribution at a Glance (4-Metric KPI Row) */}
      <ContributionKpiRow summary={summary} isLoading={isLoading} />

      {/* 3. Asymmetric Lower Grid: Left 2/3 (Participation & Opportunities), Right 1/3 (Guide & Progress) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 lg:gap-6 items-start">
        {/* Left 2-Column Span */}
        <div className="lg:col-span-2 space-y-6">
          {/* A. Your Upcoming Participation */}
          <UpcomingParticipationCard
            registrations={upcomingRegs}
            isLoading={isLoading}
          />

          {/* B. Recently Viewed / Recommended Opportunities */}
          <RecommendedEventsSection
            events={recommendedEvents}
            isLoading={isLoading}
          />
        </div>

        {/* Right 1-Column Span */}
        <div className="lg:col-span-1 space-y-5">
          {/* A. Volunteering Guide */}
          <VolunteeringGuideCard />

          {/* B. Your Progress Donut Card */}
          <ProgressDonutCard
            displayName={firstName}
            summary={summary}
          />
        </div>
      </div>
    </div>
  );
}
