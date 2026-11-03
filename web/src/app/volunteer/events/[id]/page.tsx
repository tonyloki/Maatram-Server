"use client";

import React, { useState, useEffect, useCallback, Suspense, use } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
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
  ClockAlert,
  Loader2,
  Check,
  Building,
  UserCheck,
  Info,
} from "lucide-react";
import { apiClient, ApiError } from "@/lib/api-client";
import { EventItem, RegistrationResponse, RegistrationListResponse } from "@/types";

interface PageProps {
  params: Promise<{ id: string }>;
}

function EventDetailContent({ eventId }: { eventId: string }) {
  const router = useRouter();

  const [event, setEvent] = useState<EventItem | null>(null);
  const [activeRegistration, setActiveRegistration] = useState<RegistrationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Active tab
  const [activeTab, setActiveTab] = useState<"about" | "requirements" | "location" | "organizer">("about");

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
      console.error("Failed to load event details", err);
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
    loadEventAndRegistration();
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
      setActionSuccessMessage("You have successfully registered for this event!");
      // Reload event data to reflect updated counts
      loadEventAndRegistration();
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
      loadEventAndRegistration();
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
          title: event?.title || "Maatram Volunteering Event",
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
      const durationHours = Math.max(1, Math.round((e.getTime() - s.getTime()) / (1000 * 60 * 60)));
      return `${startTime} - ${endTime} (${durationHours} hours)`;
    } catch {
      return "";
    }
  };

  const formatDeadline = (isoStr?: string) => {
    if (!isoStr) return "";
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      });
    } catch {
      return isoStr;
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 bg-white rounded-2xl border border-charcoal-200">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
        <p className="text-sm font-medium text-charcoal-500 mt-3">Loading event details...</p>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="bg-white rounded-2xl border border-charcoal-200 p-12 text-center max-w-xl mx-auto space-y-4">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
        <h2 className="text-xl font-bold text-charcoal-900">{error || "Event unavailable"}</h2>
        <Link
          href="/volunteer/events"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-500 text-charcoal-950 font-bold rounded-xl shadow-xs hover:bg-primary-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Discover Events
        </Link>
      </div>
    );
  }

  const isRegistrationClosed =
    event.status === "REGISTRATION_CLOSED" ||
    event.status === "COMPLETED" ||
    event.status === "CANCELLED" ||
    new Date(event.registration_deadline).getTime() < Date.now();

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-16">
      {/* Top Navigation Row */}
      <div className="flex items-center justify-between">
        <Link
          href="/volunteer/events"
          className="inline-flex items-center gap-2 text-sm font-bold text-charcoal-600 hover:text-charcoal-950 transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
          Back to Events
        </Link>

        <button
          type="button"
          onClick={handleShare}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-charcoal-200 hover:border-charcoal-300 bg-white text-xs font-semibold text-charcoal-700 hover:text-charcoal-950 shadow-xs transition-colors"
        >
          {copiedLink ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-600" /> Copied Link
            </>
          ) : (
            <>
              <Share2 className="w-3.5 h-3.5 text-charcoal-500" /> Share Event
            </>
          )}
        </button>
      </div>

      {/* Event Header & Badges */}
      <div className="space-y-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-md bg-sage-50 text-sage-800 border border-sage-200">
            {event.category.replace("_", " ")}
          </span>
          <span
            className={`text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-md border ${
              event.mode === "ONLINE"
                ? "bg-sky-50 text-sky-800 border-sky-200"
                : "bg-coral-50 text-coral-800 border-coral-200"
            }`}
          >
            {event.mode}
          </span>
          {event.status !== "PUBLISHED" && (
            <span className="text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-md bg-charcoal-100 text-charcoal-700">
              {event.status.replace("_", " ")}
            </span>
          )}
        </div>
        <h1 className="text-2xl md:text-3xl lg:text-4xl font-extrabold text-charcoal-900 tracking-tight font-serif">
          {event.title}
        </h1>
      </div>

      {/* Action Banners */}
      <AnimatePresence>
        {actionSuccessMessage && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-semibold flex items-center gap-2.5"
          >
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            {actionSuccessMessage}
          </motion.div>
        )}
        {actionErrorMessage && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm font-semibold flex items-center gap-2.5"
          >
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            {actionErrorMessage}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Event Showcase Card */}
      <div className="bg-white rounded-3xl border border-charcoal-200/80 p-5 md:p-8 shadow-sm space-y-8">
        {/* Top Half: Image & Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
          {/* Hero Image */}
          <div className="md:col-span-7 relative h-64 md:h-80 w-full rounded-2xl overflow-hidden bg-charcoal-100 border border-charcoal-200">
            <Image
              src={getCategoryImage(event.category)}
              alt={event.title}
              fill
              priority
              className="object-cover"
            />
          </div>

          {/* Key Facts List */}
          <div className="md:col-span-5 space-y-4">
            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-primary-50 text-primary-700 flex items-center justify-center flex-shrink-0">
                <Calendar className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-charcoal-400 uppercase tracking-wider">Date</p>
                <p className="text-sm md:text-base font-bold text-charcoal-900">{formatEventDate(event.start_time)}</p>
              </div>
            </div>

            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-primary-50 text-primary-700 flex items-center justify-center flex-shrink-0">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-charcoal-400 uppercase tracking-wider">Time</p>
                <p className="text-sm md:text-base font-bold text-charcoal-900">
                  {formatEventTime(event.start_time, event.end_time)}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-primary-50 text-primary-700 flex items-center justify-center flex-shrink-0">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-charcoal-400 uppercase tracking-wider">Location / Venue</p>
                <p className="text-sm md:text-base font-bold text-charcoal-900">
                  {event.mode === "ONLINE"
                    ? event.meeting_url
                      ? "Online (Link shared upon selection)"
                      : "Online / Google Meet"
                    : event.location || "Government School / Venue in Chennai"}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-primary-50 text-primary-700 flex items-center justify-center flex-shrink-0">
                <Users className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-charcoal-400 uppercase tracking-wider">Capacity Needed</p>
                <p className="text-sm md:text-base font-bold text-charcoal-900">
                  {event.capacity} volunteers needed ({event.selected_count || 0} selected)
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center flex-shrink-0">
                <ClockAlert className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-charcoal-400 uppercase tracking-wider">Registration Deadline</p>
                <p className="text-sm font-bold text-charcoal-900">{formatDeadline(event.registration_deadline)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Divider */}
        <hr className="border-charcoal-200" />

        {/* Bottom Half: Tabs & Content */}
        <div className="space-y-6">
          {/* Tab Navigation */}
          <div className="flex items-center gap-6 border-b border-charcoal-200 text-sm font-semibold">
            <button
              type="button"
              onClick={() => setActiveTab("about")}
              className={`pb-3 relative transition-colors ${
                activeTab === "about" ? "text-charcoal-950 font-bold" : "text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              About
              {activeTab === "about" && (
                <motion.div layoutId="detailTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
              )}
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("requirements")}
              className={`pb-3 relative transition-colors ${
                activeTab === "requirements" ? "text-charcoal-950 font-bold" : "text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              Requirements
              {activeTab === "requirements" && (
                <motion.div layoutId="detailTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
              )}
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("location")}
              className={`pb-3 relative transition-colors ${
                activeTab === "location" ? "text-charcoal-950 font-bold" : "text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              Location
              {activeTab === "location" && (
                <motion.div layoutId="detailTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
              )}
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("organizer")}
              className={`pb-3 relative transition-colors ${
                activeTab === "organizer" ? "text-charcoal-950 font-bold" : "text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              Organizer
              {activeTab === "organizer" && (
                <motion.div layoutId="detailTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
              )}
            </button>
          </div>

          {/* Tab Panes */}
          <div className="min-h-[140px] text-sm md:text-base text-charcoal-700 leading-relaxed">
            {activeTab === "about" && (
              <div className="space-y-4">
                <p>
                  {event.description ||
                    "Interact with school students, share your higher education journey, and inspire them to pursue career opportunities with confidence. Volunteers will facilitate group mentoring sessions, conduct mock interviews, and help students identify their aspirations."}
                </p>
                <div className="p-4 rounded-xl bg-primary-50/60 border border-primary-200/70 text-xs md:text-sm text-charcoal-800 space-y-1">
                  <p className="font-bold flex items-center gap-1.5 text-primary-900">
                    <Info className="w-4 h-4 text-primary-700" /> Verified Volunteer Hours Credited
                  </p>
                  <p>
                    Participating volunteers will receive official hours credited to their profile upon verified check-in
                    and check-out by the event coordinator.
                  </p>
                </div>
              </div>
            )}

            {activeTab === "requirements" && (
              <ul className="space-y-2.5 list-disc pl-5">
                <li>Arrive 15 minutes before scheduled start time for the coordinator briefing.</li>
                <li>Wear neat formal or smart casual attire (Maatram T-shirt or volunteer badge provided on arrival).</li>
                <li>Bring a valid government or college photo ID card for gate entry.</li>
                <li>Familiarize yourself with the mentorship guide sent via email prior to the session.</li>
                <li>Respect confidentiality and safeguarding guidelines for all participating school students.</li>
              </ul>
            )}

            {activeTab === "location" && (
              <div className="space-y-3">
                <p className="font-semibold text-charcoal-900">
                  {event.mode === "ONLINE" ? "Virtual Meeting Coordinates" : "Physical Venue Address"}
                </p>
                <p className="text-charcoal-600">
                  {event.mode === "ONLINE"
                    ? "This is an online event conducted via Google Meet / Zoom. The secure meeting invite link and access pass will be unlocked for selected volunteers."
                    : event.location || "Government Higher Secondary School, Saidapet, Chennai, Tamil Nadu 600015."}
                </p>
                {event.mode === "OFFLINE" && (
                  <p className="text-xs text-charcoal-500">
                    Nearest landmark: Metro Station / Bus Depot. Ample two-wheeler parking available inside the campus.
                  </p>
                )}
              </div>
            )}

            {activeTab === "organizer" && (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center text-primary-800 font-bold">
                    MF
                  </div>
                  <div>
                    <h4 className="font-bold text-charcoal-900">Maatram Foundation</h4>
                    <p className="text-xs text-charcoal-500">Volunteer Operations & Student Mentorship Team</p>
                  </div>
                </div>
                <p className="text-sm text-charcoal-600">
                  For queries or urgent updates regarding this event, please reach out to the volunteer coordination
                  desk at <span className="font-semibold text-charcoal-800">events@maatramfoundation.com</span>.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Registration Action Bar */}
        <div className="pt-6 border-t border-charcoal-200 flex flex-col sm:flex-row items-center justify-between gap-4 bg-charcoal-50/60 -mx-5 md:-mx-8 -mb-5 md:-mb-8 p-5 md:p-8 rounded-b-3xl">
          {activeRegistration ? (
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between w-full gap-4">
              <div className="flex items-center gap-3">
                {activeRegistration.status === "SELECTED" ? (
                  <div className="w-9 h-9 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0">
                    <CheckCircle2 className="w-5 h-5" />
                  </div>
                ) : activeRegistration.status === "WAITLISTED" ? (
                  <div className="w-9 h-9 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center flex-shrink-0">
                    <Hourglass className="w-5 h-5" />
                  </div>
                ) : (
                  <div className="w-9 h-9 rounded-full bg-sky-100 text-sky-700 flex items-center justify-center flex-shrink-0">
                    <UserCheck className="w-5 h-5" />
                  </div>
                )}
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-charcoal-500">Your Status:</span>
                    <span
                      className={`text-xs font-extrabold uppercase px-2.5 py-0.5 rounded-full ${
                        activeRegistration.status === "SELECTED"
                          ? "bg-emerald-100 text-emerald-800"
                          : activeRegistration.status === "WAITLISTED"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-sky-100 text-sky-800"
                      }`}
                    >
                      {activeRegistration.status}
                    </span>
                  </div>
                  <p className="text-xs text-charcoal-500 mt-0.5">
                    {activeRegistration.status === "SELECTED"
                      ? "Congratulations! You have been selected. Please arrive on time."
                      : activeRegistration.status === "WAITLISTED"
                      ? "You are on the waitlist. You will be notified automatically if a spot opens up."
                      : "You have subscribed. Admins will review selections prior to the deadline."}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setShowWithdrawDialog(true)}
                className="w-full sm:w-auto px-4 py-2 text-xs md:text-sm font-semibold rounded-xl text-red-700 hover:text-red-800 hover:bg-red-50 border border-red-200 transition-colors"
              >
                Withdraw Registration
              </button>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between w-full gap-4">
              <div>
                <p className="text-xs text-charcoal-500">Interested in joining this initiative?</p>
                <p className="text-sm font-bold text-charcoal-900">
                  {isRegistrationClosed
                    ? "Registration for this event has closed."
                    : "Spots are filled on a verified merit and category basis."}
                </p>
              </div>

              <button
                type="button"
                disabled={isRegistrationClosed || isRegistering}
                onClick={handleRegister}
                className="w-full sm:w-auto px-8 py-3 rounded-xl bg-primary-500 hover:bg-primary-400 text-charcoal-950 font-bold text-sm md:text-base shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
              >
                {isRegistering ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Registering...
                  </>
                ) : isRegistrationClosed ? (
                  "Registration Closed"
                ) : (
                  "Register for this Event"
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Confirmation Dialog for Withdrawal */}
      <AnimatePresence>
        {showWithdrawDialog && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-950/50 backdrop-blur-xs">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-3xl max-w-md w-full p-6 shadow-xl border border-charcoal-200 space-y-4"
            >
              <h3 className="text-lg font-bold text-charcoal-900">Withdraw Registration?</h3>
              <p className="text-sm text-charcoal-600">
                Are you sure you want to withdraw your registration for{" "}
                <span className="font-semibold text-charcoal-900">{event.title}</span>? Your spot may be immediately
                reallocated to a waitlisted volunteer.
              </p>
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowWithdrawDialog(false)}
                  className="px-4 py-2 text-sm font-semibold rounded-xl text-charcoal-600 hover:bg-charcoal-100 transition-colors"
                >
                  Keep Registration
                </button>
                <button
                  type="button"
                  disabled={isWithdrawing}
                  onClick={handleWithdraw}
                  className="px-4 py-2 text-sm font-semibold rounded-xl bg-red-600 hover:bg-red-700 text-white transition-colors flex items-center gap-1.5"
                >
                  {isWithdrawing && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  Yes, Withdraw
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

function EventDetailLoader({ params }: PageProps) {
  const unwrappedParams = use(params);
  return <EventDetailContent eventId={unwrappedParams.id} />;
}

export default function VolunteerEventDetailPage({ params }: PageProps) {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-2xl border border-charcoal-200">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm font-medium text-charcoal-500 mt-3">Loading event details...</p>
        </div>
      }
    >
      <EventDetailLoader params={params} />
    </Suspense>
  );
}
