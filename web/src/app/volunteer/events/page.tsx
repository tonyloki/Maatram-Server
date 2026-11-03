"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import {
  Search,
  SlidersHorizontal,
  Calendar,
  Clock,
  MapPin,
  Users,
  ChevronRight,
  Filter,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { EventItem, EventListResponse, RegistrationListResponse } from "@/types";
import { fadeInUp, staggerContainer } from "@/lib/animations";

const CATEGORIES = [
  { id: "ALL", label: "All" },
  { id: "SCHOOL_VISIT", label: "School Visit" },
  { id: "MOCK_INTERVIEW", label: "Mock Interview" },
  { id: "BGV", label: "BGV Support" },
  { id: "ADMISSIONS", label: "Admissions" },
  { id: "PANEL_INTERVIEW", label: "Panel Interview" },
];

export default function VolunteerEventsPage() {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [registeredEventIds, setRegisteredEventIds] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [selectedMode, setSelectedMode] = useState<"ALL" | "ONLINE" | "OFFLINE">("ALL");
  const [selectedTimeframe, setSelectedTimeframe] = useState<"UPCOMING" | "ALL">("UPCOMING");

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: Record<string, string | number> = {
        page: 1,
        page_size: 50,
      };
      if (selectedCategory !== "ALL") {
        params.category = selectedCategory;
      }
      if (selectedMode !== "ALL") {
        params.mode = selectedMode;
      }

      const [eventsRes, registrationsRes] = await Promise.all([
        apiClient<EventListResponse>("/events", { params }).catch((err) => {
          console.warn("Could not load /events directly:", err);
          return { items: [], total: 0, page: 1, page_size: 50, total_pages: 1 };
        }),
        apiClient<RegistrationListResponse>("/registrations/me", { params: { page: 1, page_size: 100 } }).catch(() => ({
          items: [],
          total: 0,
          page: 1,
          page_size: 100,
          total_pages: 1,
        })),
      ]);

      setEvents(eventsRes.items || []);
      const registeredIds = new Set(
        (registrationsRes.items || [])
          .filter((r) => !["WITHDRAWN", "DECLINED"].includes(r.status))
          .map((r) => r.event_id)
      );
      setRegisteredEventIds(registeredIds);
    } catch (err: unknown) {
      console.error("Failed to load events catalogue", err);
      setError("Unable to load events at this moment. Please check your connection.");
    } finally {
      setIsLoading(false);
    }
  }, [selectedCategory, selectedMode]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Client-side search and timeframe filtering
  const filteredEvents = events.filter((evt) => {
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchTitle = evt.title.toLowerCase().includes(q);
      const matchCat = evt.category.toLowerCase().includes(q);
      const matchLoc = (evt.location || "").toLowerCase().includes(q);
      if (!matchTitle && !matchCat && !matchLoc) return false;
    }
    if (selectedTimeframe === "UPCOMING") {
      const isPast = new Date(evt.end_time).getTime() < Date.now();
      if (isPast) return false;
    }
    return true;
  });

  const getCategoryImage = (category: string) => {
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

  const formatEventDate = (isoStr: string) => {
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

  const formatEventTime = (startIso: string, endIso: string) => {
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

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Title */}
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-charcoal-900 tracking-tight font-serif">
          Discover Events
        </h1>
        <p className="text-sm text-charcoal-500 mt-1">
          Explore upcoming volunteering initiatives, mentorship visits, and interview panels.
        </p>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white rounded-2xl border border-charcoal-200/80 p-3 md:p-4 shadow-sm space-y-3">
        {/* Search input with icons */}
        <div className="relative flex items-center">
          <Search className="w-5 h-5 text-charcoal-400 absolute left-3.5 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search events, e.g., school visit, mock interview, chennai..."
            className="w-full pl-11 pr-12 py-2.5 text-sm md:text-base rounded-xl border border-charcoal-200 focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent text-charcoal-900 placeholder:text-charcoal-400 transition-all bg-charcoal-50/50 focus:bg-white"
          />
          <button
            type="button"
            title="Filter options"
            className="absolute right-3 p-1.5 rounded-lg text-charcoal-400 hover:text-charcoal-700 hover:bg-charcoal-100 transition-colors"
          >
            <SlidersHorizontal className="w-4 h-4" />
          </button>
        </div>

        {/* Filter Pills & Dropdowns */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3 pt-1">
          {/* Category Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
            {CATEGORIES.map((cat) => {
              const active = selectedCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-3.5 py-1.5 rounded-full text-xs md:text-sm font-semibold transition-all whitespace-nowrap ${
                    active
                      ? "bg-primary-500 text-charcoal-950 shadow-sm ring-1 ring-primary-500"
                      : "bg-charcoal-100/70 text-charcoal-600 hover:bg-charcoal-200/70 hover:text-charcoal-900"
                  }`}
                >
                  {cat.label}
                </button>
              );
            })}
          </div>

          {/* Mode & Date Dropdowns */}
          <div className="flex items-center gap-2 self-end lg:self-auto text-xs md:text-sm">
            {/* Mode Selector */}
            <div className="flex items-center gap-1.5 bg-charcoal-50 border border-charcoal-200 rounded-xl px-2.5 py-1.5">
              <span className="text-charcoal-500 font-medium">Mode:</span>
              <select
                value={selectedMode}
                onChange={(e) => setSelectedMode(e.target.value as "ALL" | "ONLINE" | "OFFLINE")}
                className="bg-transparent text-charcoal-800 font-semibold focus:outline-none cursor-pointer"
              >
                <option value="ALL">All</option>
                <option value="OFFLINE">Offline</option>
                <option value="ONLINE">Online</option>
              </select>
            </div>

            {/* Date Selector */}
            <div className="flex items-center gap-1.5 bg-charcoal-50 border border-charcoal-200 rounded-xl px-2.5 py-1.5">
              <span className="text-charcoal-500 font-medium">Date:</span>
              <select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value as "UPCOMING" | "ALL")}
                className="bg-transparent text-charcoal-800 font-semibold focus:outline-none cursor-pointer"
              >
                <option value="UPCOMING">Upcoming</option>
                <option value="ALL">All Events</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Events List */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-charcoal-200/80">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm font-medium text-charcoal-500 mt-3">Loading available opportunities...</p>
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
      ) : filteredEvents.length === 0 ? (
        <div className="bg-white rounded-2xl border border-charcoal-200/80 p-12 text-center">
          <div className="w-14 h-14 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto text-primary-700 mb-4">
            <Filter className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-bold text-charcoal-900">No events found</h3>
          <p className="text-sm text-charcoal-500 max-w-md mx-auto mt-1">
            We couldn't find any volunteering events matching your current filters. Try resetting search or selecting “All”.
          </p>
          <button
            onClick={() => {
              setSearchQuery("");
              setSelectedCategory("ALL");
              setSelectedMode("ALL");
              setSelectedTimeframe("UPCOMING");
            }}
            className="mt-4 px-4 py-2 bg-charcoal-900 text-white rounded-xl text-sm font-semibold hover:bg-charcoal-800 transition-colors"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="space-y-4"
        >
          {filteredEvents.map((event) => {
            const isRegistered = registeredEventIds.has(event.id);
            const neededVolunteers = Math.max(0, event.capacity - (event.selected_count || 0));

            return (
              <motion.div
                key={event.id}
                variants={fadeInUp}
                className="bg-white rounded-2xl border border-charcoal-200/70 hover:border-primary-300 p-4 md:p-5 shadow-sm hover:shadow-md transition-all flex flex-col md:flex-row items-start md:items-center gap-4 md:gap-6 justify-between group"
              >
                {/* Event Image */}
                <div className="relative w-full md:w-36 h-32 md:h-24 rounded-xl overflow-hidden flex-shrink-0 bg-charcoal-100 border border-charcoal-200/60">
                  <Image
                    src={getCategoryImage(event.category)}
                    alt={event.title}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  {isRegistered && (
                    <div className="absolute top-2 left-2 bg-emerald-600/95 backdrop-blur-sm text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 shadow-sm">
                      <CheckCircle2 className="w-3 h-3" /> Registered
                    </div>
                  )}
                </div>

                {/* Event Metadata & Details */}
                <div className="flex-1 min-w-0 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h2 className="text-base md:text-lg font-bold text-charcoal-900 tracking-tight group-hover:text-primary-800 transition-colors">
                      {event.title}
                    </h2>
                    <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-charcoal-100 text-charcoal-600">
                      <Users className="w-3.5 h-3.5" />
                      {neededVolunteers > 0 ? `${neededVolunteers} volunteers needed` : "Spots full"}
                    </span>
                  </div>

                  {/* Date, Time & Location Line */}
                  <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs md:text-sm text-charcoal-600">
                    <span className="flex items-center gap-1.5 font-medium">
                      <Calendar className="w-3.5 h-3.5 text-primary-600" />
                      {formatEventDate(event.start_time)}
                    </span>
                    <span className="flex items-center gap-1.5 font-medium">
                      <Clock className="w-3.5 h-3.5 text-primary-600" />
                      {formatEventTime(event.start_time, event.end_time)}
                    </span>
                    <span className="flex items-center gap-1.5 font-medium">
                      <MapPin className="w-3.5 h-3.5 text-primary-600" />
                      {event.mode === "ONLINE" ? "Online / Meet" : event.location || "Tamil Nadu"}
                    </span>
                  </div>

                  {/* Badges Line */}
                  <div className="flex items-center gap-2 pt-0.5">
                    <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md bg-sage-50 text-sage-800 border border-sage-200">
                      {event.category.replace("_", " ")}
                    </span>
                    <span
                      className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md border ${
                        event.mode === "ONLINE"
                          ? "bg-sky-50 text-sky-800 border-sky-200"
                          : "bg-coral-50 text-coral-800 border-coral-200"
                      }`}
                    >
                      {event.mode}
                    </span>
                  </div>
                </div>

                {/* Right Action Button */}
                <div className="w-full md:w-auto flex-shrink-0 pt-2 md:pt-0">
                  <Link
                    href={`/volunteer/events/${event.id}`}
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
      )}
    </div>
  );
}

