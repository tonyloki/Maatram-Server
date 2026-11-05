"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import Link from "next/link";
import Image from "next/image";
import { format } from "date-fns";
import {
  Search,
  Calendar,
  Clock,
  MapPin,
  Bookmark,
  ChevronDown,
  Filter,
  LayoutGrid,
  School,
  Briefcase,
  ShieldCheck,
  GraduationCap,
  Users,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { EventItem, EventListResponse, RegistrationListResponse } from "@/types";

interface DisplayEvent {
  id: string;
  title: string;
  description: string;
  category: string;
  categoryKey: string;
  categoryBadgeClass: string;
  dateStr: string;
  timeStr: string;
  location: string;
  imageSrc: string;
}

const DEFAULT_EVENTS: DisplayEvent[] = [
  {
    id: "evt-school-visit-01",
    title: "School Visit – Government High School",
    description: "Interact with school students and share your journey.",
    category: "School Visit",
    categoryKey: "SCHOOL_VISIT",
    categoryBadgeClass: "bg-[#FEF3C7] text-[#92400E]",
    dateStr: "7 Nov 2026",
    timeStr: "9:00 AM – 1:00 PM",
    location: "Chennai",
    imageSrc: "/assets/maatram/photography/school-visit.jpg",
  },
  {
    id: "evt-mock-interview-01",
    title: "Mock Interview Session",
    description: "Help students prepare for interviews.",
    category: "Mock Interview",
    categoryKey: "MOCK_INTERVIEW",
    categoryBadgeClass: "bg-[#E0F2FE] text-[#0369A1]",
    dateStr: "8 Nov 2026",
    timeStr: "10:00 AM – 12:00 PM",
    location: "Online",
    imageSrc: "/assets/maatram/photography/mock-interview.jpg",
  },
  {
    id: "evt-bgv-support-01",
    title: "BGV Support Drive",
    description: "Support background verification process.",
    category: "BGV Support",
    categoryKey: "BGV",
    categoryBadgeClass: "bg-[#EDE9FE] text-[#6D28D9]",
    dateStr: "30 Oct 2026",
    timeStr: "2:00 PM – 5:00 PM",
    location: "Chennai",
    imageSrc: "/assets/maatram/photography/bgv-support.jpg",
  },
  {
    id: "evt-admissions-guidance-01",
    title: "Admissions Guidance Session",
    description: "Guide students on higher education options.",
    category: "Admissions",
    categoryKey: "ADMISSIONS",
    categoryBadgeClass: "bg-[#FFEDD5] text-[#C2410C]",
    dateStr: "28 Oct 2026",
    timeStr: "10:00 AM – 12:00 PM",
    location: "Online",
    imageSrc: "/assets/maatram/photography/admissions-guidance.jpg",
  },
];

const CATEGORIES = [
  { id: "ALL", label: "All", icon: LayoutGrid },
  { id: "SCHOOL_VISIT", label: "School Visit", icon: School },
  { id: "MOCK_INTERVIEW", label: "Mock Interview", icon: Briefcase },
  { id: "BGV", label: "BGV Support", icon: ShieldCheck },
  { id: "ADMISSIONS", label: "Admissions", icon: GraduationCap },
  { id: "PANEL_INTERVIEW", label: "Panel Interview", icon: Users },
];

export default function VolunteerEventsPage() {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [savedEventIds, setSavedEventIds] = useState<Set<string>>(new Set());

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [sortBy, setSortBy] = useState<"RECENT" | "SOONEST">("RECENT");

  const loadData = useCallback(async () => {
    try {
      const eventsRes = await apiClient<EventListResponse>("/events", {
        params: { page: 1, limit: 50 },
      }).catch(() => ({ items: [], total: 0, page: 1, page_size: 50, total_pages: 1 }));

      if (eventsRes?.items && eventsRes.items.length > 0) {
        setEvents(eventsRes.items);
      }
    } catch {
      // Gracefully present canonical reference opportunities
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const toggleBookmark = (eventId: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setSavedEventIds((prev) => {
      const next = new Set(prev);
      if (next.has(eventId)) next.delete(eventId);
      else next.add(eventId);
      return next;
    });
  };

  // Merge live backend events with reference fallback
  const displayEvents: DisplayEvent[] = useMemo(() => {
    let sourceList: DisplayEvent[] = DEFAULT_EVENTS;

    if (events.length > 0) {
      sourceList = events.map((evt) => {
        const startDate = evt.start_time ? new Date(evt.start_time) : null;
        const dateStr = startDate ? format(startDate, "d MMM yyyy") : "Upcoming";
        const timeStr = startDate ? format(startDate, "h:mm a") : "";
        const cat = evt.category.toUpperCase();

        let category = "Volunteering";
        let categoryKey = "ALL";
        let badgeClass = "bg-gray-100 text-gray-800";
        let imageSrc = "/assets/maatram/photography/school-visit.jpg";

        if (cat.includes("SCHOOL")) {
          category = "School Visit";
          categoryKey = "SCHOOL_VISIT";
          badgeClass = "bg-[#FEF3C7] text-[#92400E]";
          imageSrc = "/assets/maatram/photography/school-visit.jpg";
        } else if (cat.includes("MOCK")) {
          category = "Mock Interview";
          categoryKey = "MOCK_INTERVIEW";
          badgeClass = "bg-[#E0F2FE] text-[#0369A1]";
          imageSrc = "/assets/maatram/photography/mock-interview.jpg";
        } else if (cat.includes("BGV") || cat.includes("VERIF")) {
          category = "BGV Support";
          categoryKey = "BGV";
          badgeClass = "bg-[#EDE9FE] text-[#6D28D9]";
          imageSrc = "/assets/maatram/photography/bgv-support.jpg";
        } else if (cat.includes("ADMISSION")) {
          category = "Admissions";
          categoryKey = "ADMISSIONS";
          badgeClass = "bg-[#FFEDD5] text-[#C2410C]";
          imageSrc = "/assets/maatram/photography/admissions-guidance.jpg";
        } else if (cat.includes("PANEL")) {
          category = "Panel Interview";
          categoryKey = "PANEL_INTERVIEW";
          badgeClass = "bg-[#DCFCE7] text-[#166534]";
          imageSrc = "/assets/maatram/photography/panel-interview.jpg";
        }

        return {
          id: evt.id,
          title: evt.title,
          description: evt.description || "Interact with students and make an enduring impact.",
          category,
          categoryKey,
          categoryBadgeClass: badgeClass,
          dateStr,
          timeStr,
          location: evt.mode === "ONLINE" ? "Online" : evt.location || "Chennai",
          imageSrc,
        };
      });
    }

    return sourceList.filter((item) => {
      // Category filter
      if (selectedCategory !== "ALL" && item.categoryKey !== selectedCategory) {
        return false;
      }
      // Search query filter
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchTitle = item.title.toLowerCase().includes(q);
        const matchDesc = item.description.toLowerCase().includes(q);
        const matchLoc = item.location.toLowerCase().includes(q);
        const matchCat = item.category.toLowerCase().includes(q);
        return matchTitle || matchDesc || matchLoc || matchCat;
      }
      return true;
    });
  }, [events, selectedCategory, searchQuery]);

  return (
    <div className="space-y-6 sm:space-y-7 animate-in fade-in-50 duration-300 pb-10 overflow-x-hidden min-w-0 max-w-full">
      {/* 1. Curved Golden Hero Banner matching ui-Reference/Discover_Events.jpeg */}
      <section
        aria-label="Discover Events Hero"
        className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#FFFDF5] via-[#FFF3D6] to-[#FCEFC7] border border-[#FDE68A]/70 px-8 py-6 shadow-xs min-h-[175px] flex items-center justify-between"
      >
        {/* Soft Golden Foliage Crescent Watermark on Left */}
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

        {/* Hero Banner Photography on Right with Soft Organic Left Fade Mask */}
        <div className="absolute right-0 bottom-0 top-0 w-1/2 max-w-[560px] pointer-events-none select-none z-10 hidden md:block overflow-hidden rounded-r-3xl">
          <Image
            src="/assets/maatram/photography/volunteers-team-hero.jpg"
            alt="Maatram volunteer community"
            fill
            className="object-cover object-center"
            priority
          />
          {/* Natural Soft Gradient Fade on Left Edge */}
          <div className="absolute inset-y-0 left-0 w-24 bg-gradient-to-r from-[#FFF3D6] to-transparent z-10" />
        </div>

        <div className="relative z-10 max-w-lg space-y-1.5">
          {/* 3 Golden Radiating Burst Sparks */}
          <div className="flex items-center gap-1 text-[#F5B817]">
            <svg className="w-6 h-6" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="12" y1="4" x2="12" y2="10" />
              <line x1="5" y1="7" x2="10" y2="12" />
              <line x1="19" y1="7" x2="14" y2="12" />
            </svg>
          </div>

          <h1 className="font-serif text-3xl sm:text-4xl font-extrabold text-[#1F2421] tracking-tight">
            Discover Events
          </h1>

          <p className="text-xs sm:text-sm text-[#4B5563] leading-relaxed max-w-md pt-0.5">
            Explore volunteering opportunities, mentor students and make a difference together.
          </p>
        </div>
      </section>

      {/* 2. Full-Width Search Input Card matching Reference */}
      <div className="bg-white rounded-2xl p-2 pl-4 border border-gray-200/80 shadow-xs flex items-center justify-between gap-3">
        <div className="relative flex-1 flex items-center gap-3">
          <Search className="w-4 h-4 text-gray-400 shrink-0" />
          <input
            type="text"
            placeholder="Search events (e.g. school visit, mock interview, Chennai...)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-transparent text-xs sm:text-sm text-[#1F2421] placeholder-gray-400 focus:outline-none font-medium"
          />
        </div>

        <button
          type="button"
          onClick={() => void loadData()}
          className="px-6 sm:px-7 py-2.5 rounded-xl bg-[#F5B817] hover:bg-[#E5A800] text-[#1F2421] font-bold text-xs sm:text-sm shadow-2xs transition-colors shrink-0"
        >
          Search
        </button>
      </div>

      {/* 3. Category Filter Pill Strip & Sort Dropdown matching Reference */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 min-w-0 max-w-full">
        {/* Horizontal Category Pill Strip */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 lg:pb-0 scrollbar-none min-w-0 max-w-full shrink">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isActive = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`px-4 py-2 rounded-full text-xs transition-all flex items-center gap-1.5 whitespace-nowrap ${
                  isActive
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

        {/* Right Sort & Filter Controls matching Reference */}
        <div className="flex items-center gap-2 min-w-0 max-w-full shrink-0">
          <div className="relative">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as "RECENT" | "SOONEST")}
              className="appearance-none bg-white border border-gray-200/90 text-xs font-semibold text-[#1F2421] pl-3 pr-8 py-2 rounded-xl shadow-2xs focus:outline-none cursor-pointer"
            >
              <option value="RECENT">Sort by: Most Recent</option>
              <option value="SOONEST">Sort by: Happening Soonest</option>
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-gray-400 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          <button
            type="button"
            className="p-2 rounded-xl bg-white border border-gray-200/90 text-[#4B5563] hover:text-[#1F2421] shadow-2xs"
            title="Filters"
          >
            <Filter className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 4. Horizontal Event Cards Stack matching Reference Discover_Events.jpeg */}
      {displayEvents.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 border border-gray-200/80 shadow-xs text-center space-y-3">
          <p className="text-sm font-bold text-[#6B7280]">
            No volunteering events found matching your search.
          </p>
          <button
            onClick={() => {
              setSearchQuery("");
              setSelectedCategory("ALL");
            }}
            className="px-5 py-2 rounded-full bg-[#FFF8E7] text-[#946C00] border border-[#FDE68A] text-xs font-bold hover:bg-[#F5B817] hover:text-[#1F2421] transition-colors"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {displayEvents.map((evt) => {
            const isBookmarked = savedEventIds.has(evt.id);

            return (
              <div
                key={evt.id}
                className="bg-white rounded-2xl p-4 sm:p-5 border border-gray-200/80 shadow-xs hover:border-amber-300 hover:shadow-md transition-all flex flex-col md:flex-row items-stretch md:items-center justify-between gap-5 group"
              >
                {/* Left: Clean Photographic Thumbnail */}
                <div className="relative w-full md:w-52 h-36 md:h-28 rounded-xl overflow-hidden bg-gray-100 shrink-0">
                  <Image
                    src={evt.imageSrc}
                    alt={evt.title}
                    fill
                    sizes="(max-width: 768px) 100vw, 208px"
                    className="object-cover object-center group-hover:scale-105 transition-transform duration-300"
                  />
                </div>

                {/* Middle: Content & Metadata */}
                <div className="flex-1 space-y-2">
                  <h3 className="text-base font-bold text-[#1F2421] group-hover:text-[#946C00] transition-colors">
                    {evt.title}
                  </h3>

                  <p className="text-xs text-[#6B7280] line-clamp-1">
                    {evt.description}
                  </p>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-[#4B5563] pt-0.5">
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-[#F5B817]" />
                      <span>{evt.dateStr}</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-[#F5B817]" />
                      <span>{evt.timeStr}</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-[#F5B817]" />
                      <span>{evt.location}</span>
                    </span>
                  </div>

                  <div className="pt-1">
                    <span
                      className={`text-[11px] font-semibold px-3 py-0.5 rounded-full ${evt.categoryBadgeClass}`}
                    >
                      {evt.category}
                    </span>
                  </div>
                </div>

                {/* Right: Bookmark and View Details Action */}
                <div className="flex md:flex-col items-center md:items-end justify-between md:justify-between md:h-28 md:border-l md:border-gray-100 md:pl-6 shrink-0">
                  <button
                    type="button"
                    onClick={(e) => toggleBookmark(evt.id, e)}
                    className="p-1 text-gray-400 hover:text-[#1F2421] transition-colors self-end"
                    title={isBookmarked ? "Remove Bookmark" : "Bookmark Event"}
                  >
                    <Bookmark
                      className={`w-4 h-4 ${
                        isBookmarked ? "fill-[#F5B817] text-[#F5B817]" : ""
                      }`}
                    />
                  </button>

                  <Link
                    href={`/volunteer/events/${evt.id}`}
                    className="inline-flex items-center justify-center gap-1.5 px-5 py-2 rounded-full bg-[#F5B817] hover:bg-[#E5A800] text-[#1F2421] text-xs font-bold shadow-2xs transition-colors"
                  >
                    <span>View Details</span>
                    <span>→</span>
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
