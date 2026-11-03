"use client";

import React, { useState, useEffect, useCallback, Suspense } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { format } from "date-fns";
import {
  Calendar,
  Clock,
  MapPin,
  Video,
  Users,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Lock,
} from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import { EventItem } from "@/types";

function EventDetailContent() {
  const params = useParams();
  const eventId = params?.id as string;

  const { isAuthenticated, user, isLoading: authLoading } = useAuth();
  const [event, setEvent] = useState<EventItem | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Registration state
  const [isRegistering, setIsRegistering] = useState<boolean>(false);
  const [registerSuccess, setRegisterSuccess] = useState<boolean>(false);
  const [registerError, setRegisterError] = useState<string | null>(null);

  const fetchEvent = useCallback(async () => {
    if (!isAuthenticated || !eventId) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const data = await apiClient<EventItem>(`/events/${eventId}`);
      setEvent(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load event details.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, eventId]);

  useEffect(() => {
    let isMounted = true;
    if (authLoading || !isAuthenticated || !eventId) {
      return;
    }

    async function loadInitialEvent() {
      try {
        const data = await apiClient<EventItem>(`/events/${eventId}`);
        if (isMounted) {
          setEvent(data);
          setIsLoading(false);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : "Failed to load event details.";
          setError(msg);
          setIsLoading(false);
        }
      }
    }

    void loadInitialEvent();

    return () => {
      isMounted = false;
    };
  }, [authLoading, isAuthenticated, eventId]);

  const handleRegister = async () => {
    if (!user || user.status !== "APPROVED") {
      setRegisterError(
        "Only approved volunteers may register for events. Your account status is: " +
          (user?.status || "PENDING")
      );
      return;
    }

    setIsRegistering(true);
    setRegisterError(null);
    try {
      await apiClient(`/events/${eventId}/register`, {
        method: "POST",
        body: JSON.stringify({ notes: "Web volunteer registration" }),
      });
      setRegisterSuccess(true);
      fetchEvent();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Registration request failed.";
      setRegisterError(msg);
    } finally {
      setIsRegistering(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="volunteer" />

      <main className="flex-1 py-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          {/* Back link */}
          <Link
            href="/events"
            className="inline-flex items-center gap-2 text-xs font-semibold text-[#6B7280] hover:text-[#1F2421] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Opportunities</span>
          </Link>

          {/* Not authenticated state */}
          {!authLoading && !isAuthenticated && (
            <Card className="p-8 sm:p-12 text-center bg-white border-[#EBE6DD] space-y-4 shadow-sm">
              <div className="w-12 h-12 rounded-2xl bg-[#FFF8E7] border border-[#F5B817]/40 flex items-center justify-center text-[#B45309] mx-auto">
                <Lock className="w-6 h-6" />
              </div>
              <h2 className="text-2xl font-bold text-[#1F2421]">
                Authentication Required
              </h2>
              <p className="text-sm text-[#6B7280] max-w-md mx-auto leading-relaxed">
                Please log in with your verified volunteer account to view complete event coordinates, registration deadlines, and participate.
              </p>
              <div className="pt-2 flex justify-center gap-3">
                <Link href={`/login?redirect=/events/${eventId}`}>
                  <Button variant="primary">Login to Continue</Button>
                </Link>
                <Link href="/register">
                  <Button variant="outline">Register New Account</Button>
                </Link>
              </div>
            </Card>
          )}

          {/* Loading */}
          {isAuthenticated && isLoading && (
            <div className="bg-white rounded-3xl p-8 border border-[#EBE6DD] animate-pulse space-y-4">
              <div className="h-6 bg-gray-200 rounded w-1/4" />
              <div className="h-8 bg-gray-200 rounded w-3/4" />
              <div className="h-32 bg-gray-100 rounded" />
            </div>
          )}

          {/* Error */}
          {isAuthenticated && error && !isLoading && (
            <div className="bg-[#FEF2F2] border border-[#F87171] rounded-2xl p-6 text-center space-y-3">
              <AlertCircle className="w-6 h-6 text-[#DC2626] mx-auto" />
              <p className="text-sm font-semibold text-[#991B1B]">{error}</p>
              <Button variant="outline" size="sm" onClick={() => fetchEvent()}>
                Retry
              </Button>
            </div>
          )}

          {/* Event Content */}
          {isAuthenticated && !isLoading && !error && event && (
            <div className="bg-white rounded-3xl p-6 sm:p-10 border border-[#EBE6DD] shadow-sm space-y-8">
              {/* Header section */}
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant={event.mode === "ONLINE" ? "brand" : "neutral"}>
                    {event.category.replace(/_/g, " ")}
                  </Badge>
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#FAF8F3] text-[#4B5563] border border-[#EBE6DD]">
                    {event.mode}
                  </span>
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#F0FDF4] text-[#15803D] border border-[#BBF7D0]">
                    {event.status}
                  </span>
                </div>

                <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1F2421]">
                  {event.title}
                </h1>
              </div>

              {/* Grid with Key Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-4 border-y border-[#F3F4F6] text-xs">
                <div className="flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-[#F5B817] shrink-0" />
                  <div>
                    <span className="text-[#6B7280] block">Date</span>
                    <span className="font-semibold text-[#1F2421]">
                      {format(new Date(event.start_time), "EEEE, dd MMMM yyyy")}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-[#F5B817] shrink-0" />
                  <div>
                    <span className="text-[#6B7280] block">Time & Duration</span>
                    <span className="font-semibold text-[#1F2421]">
                      {format(new Date(event.start_time), "hh:mm a")} – {format(new Date(event.end_time), "hh:mm a")}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {event.mode === "ONLINE" ? (
                    <>
                      <Video className="w-5 h-5 text-[#F5B817] shrink-0" />
                      <div>
                        <span className="text-[#6B7280] block">Meeting Format</span>
                        <span className="font-semibold text-[#1F2421]">Online Video Conference</span>
                      </div>
                    </>
                  ) : (
                    <>
                      <MapPin className="w-5 h-5 text-[#F5B817] shrink-0" />
                      <div>
                        <span className="text-[#6B7280] block">Venue</span>
                        <span className="font-semibold text-[#1F2421]">{event.location || "Location to be shared upon selection"}</span>
                      </div>
                    </>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <Users className="w-5 h-5 text-[#F5B817] shrink-0" />
                  <div>
                    <span className="text-[#6B7280] block">Capacity</span>
                    <span className="font-semibold text-[#1F2421]">
                      {event.capacity} volunteers needed ({event.registered_count} applied)
                    </span>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-3">
                <h2 className="text-base font-bold text-[#1F2421]">Event Overview & Details</h2>
                <div className="text-sm text-[#4B5563] leading-relaxed whitespace-pre-line bg-[#FAF8F3] p-5 rounded-2xl border border-[#EBE6DD]">
                  {event.description || "Detailed agenda will be coordinated via the volunteer WhatsApp and email channels prior to the session."}
                </div>
              </div>

              {/* Registration Deadline Alert */}
              <div className="text-xs text-[#6B7280] flex items-center justify-between p-3.5 rounded-xl bg-[#FFF8E7] border border-[#F5B817]/30">
                <span className="font-medium text-[#946C00]">
                  Registration Closes: {format(new Date(event.registration_deadline), "dd MMM yyyy, hh:mm a")}
                </span>
                <span className="text-gray-500">Subject to coordinator selection</span>
              </div>

              {/* Action Area */}
              <div className="pt-2">
                {registerSuccess ? (
                  <div className="p-4 rounded-xl bg-[#F0FDF4] border border-[#86EFAC] text-[#15803D] flex items-center gap-3 text-sm font-semibold">
                    <CheckCircle2 className="w-5 h-5 shrink-0" />
                    <span>Your registration request has been submitted! Event coordinators will review applications and confirm selection.</span>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {registerError && (
                      <div className="p-3.5 rounded-xl bg-[#FEF2F2] border border-[#FCA5A5] text-[#991B1B] text-xs flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 shrink-0" />
                        <span>{registerError}</span>
                      </div>
                    )}

                    <Button
                      variant="primary"
                      size="lg"
                      className="w-full sm:w-auto px-8"
                      disabled={isRegistering || event.status !== "PUBLISHED"}
                      onClick={handleRegister}
                    >
                      {isRegistering ? "Submitting Application..." : "Register for this Event"}
                    </Button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      <PublicFooter />
    </div>
  );
}

export default function EventDetailPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex flex-col bg-[#FAF8F3]">
          <PublicHeader activeNav="volunteer" />
          <div className="max-w-4xl mx-auto px-4 py-16 text-center animate-pulse space-y-4 w-full">
            <div className="h-6 bg-gray-200 rounded w-1/4" />
            <div className="h-32 bg-white rounded-3xl border border-[#EBE6DD]" />
          </div>
          <PublicFooter />
        </div>
      }
    >
      <EventDetailContent />
    </Suspense>
  );
}
