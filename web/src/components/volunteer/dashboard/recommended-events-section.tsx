"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { format } from "date-fns";
import { Flame, ArrowRight, Calendar, MapPin, Video } from "lucide-react";
import { EventItem } from "@/types";

interface RecommendedEventsSectionProps {
  events: EventItem[];
  isLoading: boolean;
}

export function RecommendedEventsSection({
  events,
  isLoading,
}: RecommendedEventsSectionProps) {
  // Fallback curated drives matching the mentor's reference visual cards
  const fallbackDrives = [
    {
      id: "school-visit-curated",
      title: "Government High School Mentoring Drive",
      category: "School Visit",
      mode: "OFFLINE",
      date: "26 Oct 2026",
      location: "Chennai Rural GHS",
      description:
        "Career guidance and scholarship counseling for 10th and 12th standard students in government schools.",
      imageSrc: "/assets/maatram/photography/school-visit.jpg",
      modePill: { label: "Onsite", bg: "bg-[#DCFCE7] text-[#166534] border-[#BBF7D0]" },
      categoryPill: { label: "School Visit", bg: "bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]" },
    },
    {
      id: "mock-interview-curated",
      title: "College Scholar Mock Interview Series",
      category: "Mock Interview",
      mode: "ONLINE",
      date: "28 Oct 2026",
      location: "Google Meet",
      description:
        "Practice interviews, resume critique, and communication coaching for graduating scholarship recipients.",
      imageSrc: "/assets/maatram/photography/mock-interview.jpg",
      modePill: { label: "Online", bg: "bg-[#EDE9FE] text-[#6D28D9] border-[#DDD6FE]" },
      categoryPill: { label: "Mock Interview", bg: "bg-[#E0F2FE] text-[#0369A1] border-[#BAE6FD]" },
    },
  ];

  // If live events are returned from API, map them to cards
  const displayCards =
    events && events.length >= 2
      ? events.slice(0, 2).map((ev, idx) => {
          const startDate = ev.start_time ? new Date(ev.start_time) : null;
          const dateStr = startDate ? format(startDate, "d MMM yyyy") : "Upcoming";
          const isOnline = ev.mode === "ONLINE";
          const imageSrc =
            idx === 0
              ? "/assets/maatram/photography/school-visit.jpg"
              : "/assets/maatram/photography/mock-interview.jpg";

          return {
            id: ev.id,
            title: ev.title,
            category: ev.category,
            mode: ev.mode,
            date: dateStr,
            location: ev.location || (isOnline ? "Virtual Meet" : "Field Location"),
            description:
              ev.description ||
              "Engage with motivated scholars and make an enduring impact through Maatram volunteering.",
            imageSrc,
            modePill: isOnline
              ? { label: "Online", bg: "bg-[#EDE9FE] text-[#6D28D9] border-[#DDD6FE]" }
              : { label: "Onsite", bg: "bg-[#DCFCE7] text-[#166534] border-[#BBF7D0]" },
            categoryPill:
              ev.category.toLowerCase().includes("school")
                ? { label: ev.category, bg: "bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]" }
                : { label: ev.category, bg: "bg-[#E0F2FE] text-[#0369A1] border-[#BAE6FD]" },
          };
        })
      : fallbackDrives;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-[#1F2421]">
          <Flame className="w-5 h-5 text-[#D97706] fill-[#F5B817]" />
          <h3 className="text-base sm:text-lg font-extrabold tracking-tight">
            Recently Viewed / Recommended Opportunities
          </h3>
        </div>
        <Link
          href="/volunteer/events"
          className="text-xs font-bold text-[#B45309] hover:text-[#946C00] hover:underline flex items-center gap-1 transition-colors"
        >
          <span>View All Events</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* 2-Column Responsive Card Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
        {displayCards.map((card) => (
          <div
            key={card.id}
            className="bg-white rounded-2xl border border-[#EFECE6] shadow-xs hover:border-[#F5B817]/60 hover:shadow-md transition-all overflow-hidden flex flex-col justify-between group"
          >
            {/* Top Thumbnail Image */}
            <div className="relative h-40 w-full overflow-hidden bg-gray-100">
              <Image
                src={card.imageSrc}
                alt={card.title}
                fill
                sizes="(max-width: 640px) 100vw, 50vw"
                className="object-cover object-center group-hover:scale-105 transition-transform duration-300"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent pointer-events-none" />

              {/* Mode & Category Tags on Image */}
              <div className="absolute top-3 left-3 flex flex-wrap items-center gap-2">
                <span
                  className={`text-[11px] font-extrabold px-2.5 py-0.5 rounded-full border shadow-2xs ${card.modePill.bg}`}
                >
                  {card.modePill.label}
                </span>
                <span
                  className={`text-[11px] font-extrabold px-2.5 py-0.5 rounded-full border shadow-2xs ${card.categoryPill.bg}`}
                >
                  {card.categoryPill.label}
                </span>
              </div>

              {/* Date Badge */}
              <div className="absolute bottom-3 left-3 bg-white/95 backdrop-blur-xs px-2.5 py-1 rounded-lg text-[11px] font-extrabold text-[#1F2421] shadow-2xs flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-[#F5B817]" />
                <span>{card.date}</span>
              </div>
            </div>

            {/* Card Content */}
            <div className="p-5 flex-1 flex flex-col justify-between space-y-3">
              <div className="space-y-1.5">
                <h4 className="text-sm sm:text-base font-extrabold text-[#1F2421] group-hover:text-[#946C00] transition-colors line-clamp-1">
                  {card.title}
                </h4>
                <p className="text-xs text-[#6B7280] line-clamp-2 leading-relaxed">
                  {card.description}
                </p>
              </div>

              {/* Bottom Location & Action */}
              <div className="pt-2 border-t border-[#EFECE6]/80 flex items-center justify-between text-xs">
                <span className="text-[#6B7280] flex items-center gap-1 font-medium truncate max-w-[160px]">
                  {card.mode === "ONLINE" ? (
                    <Video className="w-3.5 h-3.5 text-blue-500 shrink-0" />
                  ) : (
                    <MapPin className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                  )}
                  <span className="truncate">{card.location}</span>
                </span>

                <Link
                  href={card.id.endsWith("-curated") ? "/volunteer/events" : `/volunteer/events/${card.id}`}
                  className="font-extrabold text-[#B45309] group-hover:text-[#D97706] hover:underline flex items-center gap-1 shrink-0"
                >
                  <span>View Event</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

