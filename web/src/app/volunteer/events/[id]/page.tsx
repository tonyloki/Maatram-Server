"use client";

import React, { useState, useEffect, useCallback, use } from "react";
import Link from "next/link";
import Image from "next/image";
import { format } from "date-fns";
import {
  ArrowLeft,
  Share2,
  Calendar,
  Clock,
  MapPin,
  Users,
  AlertCircle,
  CheckCircle2,
  Hourglass,
  Loader2,
  Check,
  Building,
  UserCheck,
  Info,
  Video,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { apiClient, ApiError } from "@/lib/api-client";
import { EventItem, RegistrationResponse, RegistrationListResponse } from "@/types";

interface PageProps {
  params: Promise<{ id: string }>;
}

function getCategoryPhoto(category?: string): string {
  if (!category) return "/assets/maatram/photography/community-engagement.jpg";
  const cat = category.toUpperCase();
  if (cat.includes("SCHOOL")) return "/assets/maatram/photography/school-visit.jpg";
  if (cat.includes("MOCK")) return "/assets/maatram/photography/mock-interview.jpg";
  if (cat.includes("BGV") || cat.includes("VERIF")) return "/assets/maatram/photography/bgv-support.jpg";
  if (cat.includes("ADMISSION")) return "/assets/maatram/photography/admissions-guidance.jpg";
  if (cat.includes("PANEL")) return "/assets/maatram/photography/panel-interview.jpg";
  return "/assets/maatram/photography/community-engagement.jpg";
}

function EventDetailContent({ eventId }: { eventId: string }) {
  const [event, setEvent] = useState<EventItem | null>(null);
  const [activeRegistration, setActiveRegistration] = useState<RegistrationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Active tab
  const [activeTab, setActiveTab] = useState<"about" | "guidelines" | "location">("about");

  // Action states
  const [isRegistering, setIsRegistering] = useState(false);
  const [isWithdrawing, setIsWithdrawing] = useState(false);
  const [showWithdrawDialog, setShowWithdrawDialog] = useState(false);
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);
  const [actionErrorMessage, setActionErrorMessage] = useState<string | null>(null);
  const [copiedLink, setCopiedLink] = useState(false);

  const loadEventAndRegistration = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [evtData, regData] = await Promise.all([
        apiClient<EventItem>(`/events/${eventId}`),
        apiClient<RegistrationListResponse>("/registrations/me", { params: { page: 1, page_size: 100 } }).catch(() => ({
          items: [],
          total: 0,
          page: 1,
          page_size: 100,
          total_pages: 1,
        })),
      ]);

      setEvent(evtData);
      const existing = (regData.items || []).find(
        (r) => r.event_id === eventId && !["WITHDRAWN", "DECLINED"].includes(r.status)
      );
      setActiveRegistration(existing || null);
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setError("The requested event was not found or has been removed.");
      } else {
        setError("Unable to load event details at this time.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [eventId]);

  useEffect(() => {
    void loadEventAndRegistration();
  }, [loadEventAndRegistration]);

  const handleRegister = async () => {
    setIsRegistering(true);
    setActionErrorMessage(null);
    setActionSuccessMessage(null);
    try {
      const reg = await apiClient<RegistrationResponse>(`/events/${eventId}/register`, {
        method: "POST",
      });
      setActiveRegistration(reg);
      setActionSuccessMessage("You have successfully registered for this volunteering drive!");
      void loadEventAndRegistration();
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setActionErrorMessage(err.message || "Failed to register for event.");
      } else {
        setActionErrorMessage("An unexpected error occurred during registration.");
      }
    } finally {
      setIsRegistering(false);
    }
  };

  const handleWithdraw = async () => {
    if (!activeRegistration) return;
    setIsWithdrawing(true);
    setActionErrorMessage(null);
    setActionSuccessMessage(null);
    try {
      await apiClient(`/registrations/${activeRegistration.id}/withdraw`, {
        method: "POST",
        body: JSON.stringify({ reason: "Volunteer requested withdrawal via web portal" }),
      });
      setShowWithdrawDialog(false);
      setActiveRegistration(null);
      setActionSuccessMessage("Registration withdrawn successfully.");
      void loadEventAndRegistration();
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setActionErrorMessage(err.message || "Failed to withdraw registration.");
      } else {
        setActionErrorMessage("An unexpected error occurred during withdrawal.");
      }
    } finally {
      setIsWithdrawing(false);
    }
  };

  const handleShare = async () => {
    if (typeof window === "undefined") return;
    const url = window.location.href;
    if (navigator.share) {
      try {
        await navigator.share({
          title: event?.title || "Maatram Volunteering Opportunity",
          text: `Join me in volunteering for ${event?.title} with Maatram Foundation!`,
          url,
        });
        return;
      } catch {
        // Fallback to clipboard
      }
    }
    await navigator.clipboard.writeText(url);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2500);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-[#EFECE6] shadow-xs">
        <Loader2 className="w-8 h-8 text-[#F5B817] animate-spin" />
        <p className="text-sm font-bold text-[#6B7280] mt-3">Loading opportunity details...</p>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="bg-white rounded-3xl border border-[#EFECE6] p-10 text-center max-w-xl mx-auto space-y-4 shadow-sm">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
        <h2 className="text-xl font-extrabold text-[#1F2421]">{error || "Opportunity unavailable"}</h2>
        <Link
          href="/volunteer/events"
          className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#F5B817] text-[#1F2421] font-bold rounded-full shadow-sm hover:bg-[#E5A800] transition-colors text-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Discover Events
        </Link>
      </div>
    );
  }

  const startDate = event.start_time ? new Date(event.start_time) : null;
  const endDate = event.end_time ? new Date(event.end_time) : null;
  const dateStr = startDate ? format(startDate, "EEEE, d MMMM yyyy") : "";
  const timeStr = startDate && endDate ? `${format(startDate, "h:mm a")} – ${format(endDate, "h:mm a")}` : "";
  const isOnline = event.mode === "ONLINE";
  const photoSrc = getCategoryPhoto(event.category);

  const isRegistrationClosed =
    event.status === "REGISTRATION_CLOSED" ||
    event.status === "COMPLETED" ||
    event.status === "CANCELLED" ||
    (event.registration_deadline && new Date(event.registration_deadline).getTime() < Date.now());

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-16 animate-in fade-in-50 duration-300">
      {/* Top Navigation Row */}
      <div className="flex items-center justify-between">
        <Link
          href="/volunteer/events"
          className="inline-flex items-center gap-2 text-xs sm:text-sm font-bold text-[#4B5563] hover:text-[#1F2421] transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span>Back to Discover Events</span>
        </Link>

        <button
          type="button"
          onClick={handleShare}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border border-[#EFECE6] bg-white text-xs font-bold text-[#4B5563] hover:text-[#1F2421] hover:border-[#F5B817] shadow-2xs transition-colors"
        >
          {copiedLink ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span>Copied Link</span>
            </>
          ) : (
            <>
              <Share2 className="w-3.5 h-3.5 text-[#F5B817]" />
              <span>Share Event</span>
            </>
          )}
        </button>
      </div>

      {/* Success / Error Notification Banners */}
      {actionSuccessMessage && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs sm:text-sm font-bold flex items-center gap-2 shadow-2xs">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{actionSuccessMessage}</span>
        </div>
      )}
      {actionErrorMessage && (
        <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-red-900 text-xs sm:text-sm font-bold flex items-center gap-2 shadow-2xs">
          <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
          <span>{actionErrorMessage}</span>
        </div>
      )}

      {/* Hero Header Area */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-[#EFECE6] shadow-xs space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A]">
            {event.category.replace("_", " ")}
          </span>
          <span
            className={`text-xs font-bold px-3 py-1 rounded-full border ${
              isOnline
                ? "bg-[#EDE9FE] text-[#6D28D9] border-[#DDD6FE]"
                : "bg-[#DCFCE7] text-[#166534] border-[#BBF7D0]"
            }`}
          >
            {isOnline ? "Online Session" : "Onsite Drive"}
          </span>
          {activeRegistration && (
            <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Registered ({activeRegistration.status})
            </span>
          )}
        </div>

        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-[#1F2421] tracking-tight leading-snug">
          {event.title}
        </h1>

        {/* Quick Metadata Chips */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs sm:text-sm text-[#4B5563]">
          <div className="flex items-center gap-2.5 p-3 rounded-xl bg-[#FAF8F5] border border-[#EFECE6]">
            <Calendar className="w-4 h-4 text-[#F5B817] shrink-0" />
            <div className="truncate">
              <p className="text-[11px] font-bold text-[#6B7280]">Date</p>
              <p className="font-extrabold text-[#1F2421] truncate">{dateStr}</p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 p-3 rounded-xl bg-[#FAF8F5] border border-[#EFECE6]">
            <Clock className="w-4 h-4 text-[#F5B817] shrink-0" />
            <div className="truncate">
              <p className="text-[11px] font-bold text-[#6B7280]">Time & Duration</p>
              <p className="font-extrabold text-[#1F2421] truncate">{timeStr}</p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 p-3 rounded-xl bg-[#FAF8F5] border border-[#EFECE6]">
            {isOnline ? (
              <Video className="w-4 h-4 text-blue-500 shrink-0" />
            ) : (
              <MapPin className="w-4 h-4 text-emerald-500 shrink-0" />
            )}
            <div className="truncate">
              <p className="text-[11px] font-bold text-[#6B7280]">Format & Venue</p>
              <p className="font-extrabold text-[#1F2421] truncate">
                {isOnline ? "Virtual Google Meet" : event.location || "Onsite Field"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Two-Column Grid: Left Content (2/3), Right Registration & Support (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 items-start">
        {/* Left Column (2/3 width) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Featured Photographic Banner */}
          <div className="relative h-64 sm:h-80 w-full rounded-3xl overflow-hidden shadow-xs border border-[#EFECE6] bg-gray-100">
            <Image
              src={photoSrc}
              alt={event.title}
              fill
              priority
              sizes="(max-width: 1024px) 100vw, 66vw"
              className="object-cover object-center"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent pointer-events-none" />
            <div className="absolute bottom-4 left-4 right-4 text-white text-xs sm:text-sm font-semibold flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#F5B817]" />
              <span>Official Maatram Volunteering Drive — Verified service hours & credits granted</span>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-[#EFECE6] shadow-xs space-y-6">
            <div className="flex items-center gap-2 border-b border-[#EFECE6] pb-3 text-xs sm:text-sm font-bold">
              <button
                onClick={() => setActiveTab("about")}
                className={`px-4 py-2 rounded-xl transition-all ${
                  activeTab === "about"
                    ? "bg-[#FFF8E7] text-[#946C00] shadow-2xs border-b-2 border-[#F5B817]"
                    : "text-[#6B7280] hover:text-[#1F2421]"
                }`}
              >
                About Opportunity
              </button>
              <button
                onClick={() => setActiveTab("guidelines")}
                className={`px-4 py-2 rounded-xl transition-all ${
                  activeTab === "guidelines"
                    ? "bg-[#FFF8E7] text-[#946C00] shadow-2xs border-b-2 border-[#F5B817]"
                    : "text-[#6B7280] hover:text-[#1F2421]"
                }`}
              >
                Volunteer Guidelines
              </button>
              <button
                onClick={() => setActiveTab("location")}
                className={`px-4 py-2 rounded-xl transition-all ${
                  activeTab === "location"
                    ? "bg-[#FFF8E7] text-[#946C00] shadow-2xs border-b-2 border-[#F5B817]"
                    : "text-[#6B7280] hover:text-[#1F2421]"
                }`}
              >
                Venue & Logistics
              </button>
            </div>

            {/* Tab 1: About */}
            {activeTab === "about" && (
              <div className="space-y-4 text-sm text-[#4B5563] leading-relaxed">
                <h3 className="text-base font-extrabold text-[#1F2421]">Opportunity Overview</h3>
                <p>
                  {event.description ||
                    "This initiative brings passionate volunteers together with deserving students to provide structured mentoring, career orientation, and academic encouragement."}
                </p>
                <div className="p-4 rounded-2xl bg-[#FAF8F5] border border-[#EFECE6] space-y-2">
                  <h4 className="text-xs font-bold text-[#1F2421] uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-[#F5B817]" /> Impact on Scholars
                  </h4>
                  <p className="text-xs text-[#6B7280]">
                    Volunteers provide firsthand guidance that demystifies college admissions, corporate hiring expectations, and vocational pathways for first-generation learners.
                  </p>
                </div>
              </div>
            )}

            {/* Tab 2: Guidelines */}
            {activeTab === "guidelines" && (
              <div className="space-y-4 text-sm text-[#4B5563] leading-relaxed">
                <h3 className="text-base font-extrabold text-[#1F2421]">Participation Guidelines</h3>
                <ul className="space-y-2.5 text-xs sm:text-sm">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[#F5B817] shrink-0 mt-0.5" />
                    <span>Please arrive or log in at least 15 minutes before the scheduled start time.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[#F5B817] shrink-0 mt-0.5" />
                    <span>Maintain respectful, constructive, and child-safe interactions aligned with Maatram ethical standards.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[#F5B817] shrink-0 mt-0.5" />
                    <span>Attendance check-in and check-out must be verified on the portal to earn impact points and certified hours.</span>
                  </li>
                </ul>
              </div>
            )}

            {/* Tab 3: Location */}
            {activeTab === "location" && (
              <div className="space-y-4 text-sm text-[#4B5563] leading-relaxed">
                <h3 className="text-base font-extrabold text-[#1F2421]">Venue & Accessibility</h3>
                <p>
                  {isOnline
                    ? "This is a virtual opportunity. A verified Google Meet link will be displayed on this page after your registration is confirmed by event coordinators."
                    : `This event takes place in-person at: ${event.location || "Government High School / College Campus in Chennai"}. Local coordination details will be messaged to selected participants.`}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column (1/3 width): Registration & Support Card */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl p-6 border border-[#EFECE6] shadow-xs space-y-5">
            <h3 className="text-base font-extrabold text-[#1F2421]">Participation Status</h3>

            {activeRegistration ? (
              /* Already Registered State */
              <div className="space-y-4">
                <div className="p-4 rounded-2xl bg-[#DCFCE7] border border-[#BBF7D0] text-[#166534] space-y-1.5">
                  <div className="flex items-center gap-2 font-extrabold text-sm">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>You are registered!</span>
                  </div>
                  <p className="text-xs">Status: <strong>{activeRegistration.status}</strong></p>
                  <p className="text-[11px] text-[#166534]/80">
                    Coordinators will notify you regarding batch assignments and briefing materials.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => setShowWithdrawDialog(true)}
                  disabled={isWithdrawing}
                  className="w-full py-2.5 rounded-full border border-red-200 bg-red-50 hover:bg-red-100 text-red-700 text-xs font-bold transition-colors"
                >
                  Withdraw Registration
                </button>
              </div>
            ) : isRegistrationClosed ? (
              /* Closed Registration State */
              <div className="p-4 rounded-2xl bg-gray-100 border border-gray-200 text-gray-700 text-xs font-bold text-center">
                Registration is currently closed for this opportunity.
              </div>
            ) : (
              /* Open for Registration */
              <div className="space-y-4">
                <div className="space-y-2 text-xs text-[#6B7280]">
                  <div className="flex items-center justify-between">
                    <span>Volunteers Needed:</span>
                    <strong className="text-[#1F2421]">{event.capacity || "Flexible"}</strong>
                  </div>
                  {event.registration_deadline && (
                    <div className="flex items-center justify-between">
                      <span>Deadline:</span>
                      <strong className="text-[#1F2421]">
                        {format(new Date(event.registration_deadline), "d MMM, h:mm a")}
                      </strong>
                    </div>
                  )}
                </div>

                <button
                  type="button"
                  onClick={handleRegister}
                  disabled={isRegistering}
                  className="w-full py-3 rounded-full bg-[#F5B817] hover:bg-[#E5A800] active:bg-[#C99200] text-[#1F2421] font-extrabold text-sm shadow-md shadow-[#F5B817]/30 transition-all flex items-center justify-center gap-2"
                >
                  {isRegistering ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Registering...</span>
                    </>
                  ) : (
                    <span>Register for Opportunity</span>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Volunteer Helpdesk Support Chip */}
          <div className="bg-white rounded-3xl p-5 border border-[#EFECE6] shadow-xs text-xs text-[#6B7280] space-y-2">
            <h4 className="font-extrabold text-[#1F2421] flex items-center gap-1.5">
              <Info className="w-4 h-4 text-[#F5B817]" /> Questions or Assistance?
            </h4>
            <p>
              Reach out to the volunteer coordination team for queries about travel, timing, or briefing details.
            </p>
            <a
              href="mailto:volunteers@maatramfoundation.org"
              className="text-[#946C00] font-bold hover:underline block"
            >
              volunteers@maatramfoundation.org
            </a>
          </div>
        </div>
      </div>

      {/* Confirmation Modal for Withdrawal */}
      {showWithdrawDialog && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 border border-[#EFECE6] shadow-2xl space-y-4">
            <h3 className="text-lg font-extrabold text-[#1F2421]">Confirm Withdrawal</h3>
            <p className="text-xs sm:text-sm text-[#6B7280] leading-relaxed">
              Are you sure you want to withdraw your registration for <strong>{event.title}</strong>? Your spot will be released to volunteers on the waitlist.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowWithdrawDialog(false)}
                className="px-4 py-2 rounded-full border border-[#EFECE6] text-xs font-bold text-[#6B7280] hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleWithdraw}
                disabled={isWithdrawing}
                className="px-5 py-2 rounded-full bg-red-600 hover:bg-red-700 text-white text-xs font-bold shadow-xs"
              >
                {isWithdrawing ? "Withdrawing..." : "Yes, Withdraw"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function VolunteerEventDetailPage({ params }: PageProps) {
  const resolvedParams = use(params);
  return <EventDetailContent eventId={resolvedParams.id} />;
}
