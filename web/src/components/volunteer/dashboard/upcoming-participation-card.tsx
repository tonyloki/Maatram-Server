"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { format } from "date-fns";
import {
  Calendar,
  Clock,
  MapPin,
  Video,
  ArrowRight,
  Compass,
} from "lucide-react";
import { RegistrationResponse, RegistrationStatus } from "@/types";

interface UpcomingParticipationCardProps {
  registrations: RegistrationResponse[];
  isLoading: boolean;
}

function getStatusBadge(status: RegistrationStatus) {
  switch (status) {
    case "SELECTED":
      return (
        <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#DCFCE7] text-[#166534] border border-[#BBF7D0]">
          Selected
        </span>
      );
    case "SUBSCRIBED":
      return (
        <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A]">
          Registered
        </span>
      );
    case "WAITLISTED":
      return (
        <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-[#EDE9FE] text-[#6D28D9] border border-[#DDD6FE]">
          Waitlisted
        </span>
      );
    case "DECLINED":
    case "NOT_SELECTED":
      return (
        <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-gray-100 text-gray-700 border border-gray-200">
          Not Selected
        </span>
      );
    case "WITHDRAWN":
      return (
        <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-red-50 text-red-700 border border-red-200">
          Withdrawn
        </span>
      );
    default:
      return (
        <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-gray-100 text-gray-700">
          {status}
        </span>
      );
  }
}

export function UpcomingParticipationCard({
  registrations,
  isLoading,
}: UpcomingParticipationCardProps) {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-base sm:text-lg font-extrabold text-[#1F2421]">
          Your Upcoming Participation
        </h3>
        <Link
          href="/volunteer/activity"
          className="text-xs font-bold text-[#B45309] hover:text-[#946C00] hover:underline flex items-center gap-1 transition-colors"
        >
          <span>All Activity History</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* Content Area */}
      {isLoading ? (
        <div className="bg-white rounded-2xl p-8 border border-[#EFECE6] text-center animate-pulse space-y-4">
          <div className="w-32 h-24 bg-gray-100 rounded-xl mx-auto" />
          <div className="w-48 h-5 bg-gray-100 rounded mx-auto" />
          <div className="w-64 h-4 bg-gray-100 rounded mx-auto" />
        </div>
      ) : registrations.length === 0 ? (
        /* Empty State Matching Reference Dashboard.jpeg */
        <div className="bg-white rounded-2xl p-6 sm:p-8 border border-[#EFECE6] shadow-xs text-center flex flex-col items-center justify-center">
          <div className="w-32 h-24 relative mb-2">
            <Image
              src="/assets/maatram/illustrations/empty-calendar-event.svg"
              alt="No upcoming volunteering registrations"
              fill
              className="object-contain"
            />
          </div>

          <h4 className="text-base sm:text-lg font-extrabold text-[#1F2421] tracking-tight mt-1 mb-1">
            Your next impact starts here
          </h4>
          <p className="text-xs sm:text-sm text-[#6B7280] max-w-sm mb-5 leading-relaxed">
            You have no upcoming registrations yet. Explore published opportunities to get involved.
          </p>

          <Link
            href="/volunteer/events"
            className="inline-flex items-center gap-2 bg-[#F5B817] hover:bg-[#E5A800] active:bg-[#C99200] text-[#1F2421] font-extrabold text-xs sm:text-sm px-5 py-2.5 rounded-full shadow-sm hover:shadow transition-all"
          >
            <Compass className="w-4 h-4" />
            <span>Browse Opportunities</span>
          </Link>
        </div>
      ) : (
        /* List of Upcoming Registrations */
        <div className="space-y-3">
          {registrations.map((reg) => {
            const event = reg.event;
            const startDate = event?.start_time ? new Date(event.start_time) : null;
            const dateStr = startDate ? format(startDate, "d MMM yyyy") : "Upcoming";
            const timeStr = startDate ? format(startDate, "h:mm a") : "";

            return (
              <div
                key={reg.id}
                className="bg-white rounded-2xl p-4 sm:p-5 border border-[#EFECE6] shadow-xs hover:border-[#F5B817]/60 hover:shadow-sm transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-2 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    {getStatusBadge(reg.status)}
                    {event?.category && (
                      <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A]">
                        {event.category}
                      </span>
                    )}
                    {event?.mode && (
                      <span className="text-[11px] font-semibold text-[#6B7280] flex items-center gap-1">
                        {event.mode === "ONLINE" ? (
                          <>
                            <Video className="w-3 h-3 text-blue-500" /> Online
                          </>
                        ) : (
                          <>
                            <MapPin className="w-3 h-3 text-emerald-500" /> Onsite
                          </>
                        )}
                      </span>
                    )}
                  </div>

                  <h4 className="text-sm sm:text-base font-extrabold text-[#1F2421] line-clamp-1">
                    {event?.title || "Volunteering Event"}
                  </h4>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-[#6B7280]">
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
                    {event?.location && (
                      <span className="flex items-center gap-1 truncate max-w-[200px]">
                        <MapPin className="w-3.5 h-3.5 text-[#F5B817]" />
                        {event.location}
                      </span>
                    )}
                  </div>
                </div>

                <Link
                  href={`/volunteer/events/${reg.event_id}`}
                  className="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-xl bg-[#FAF8F5] hover:bg-[#FFF8E7] text-[#1F2421] hover:text-[#946C00] border border-[#EFECE6] text-xs font-bold transition-colors shrink-0"
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

