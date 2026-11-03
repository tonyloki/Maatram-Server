"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Calendar,
  MapPin,
  Video,
  Search,
  Users,
  AlertCircle,
  ArrowRight,
  Lock,
} from "lucide-react";
import { format } from "date-fns";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import { EventItem, EventListResponse } from "@/types";

export default function EventsCataloguePage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [events, setEvents] = useState<EventItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedMode, setSelectedMode] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const fetchEvents = useCallback(async () => {
    if (!isAuthenticated) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const params: Record<string, string> = {};
      if (selectedCategory !== "ALL") params.category = selectedCategory;
      if (selectedMode !== "ALL") params.mode = selectedMode;
      if (searchQuery.trim()) params.search = searchQuery.trim();

      const data = await apiClient<EventListResponse>("/events", { params });
      setEvents(data.items || []);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load events.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, selectedCategory, selectedMode, searchQuery]);

  useEffect(() => {
    let isMounted = true;
    if (authLoading || !isAuthenticated) {
      return;
    }

    async function loadEvents() {
      try {
        const params: Record<string, string> = {};
        if (selectedCategory !== "ALL") params.category = selectedCategory;
        if (selectedMode !== "ALL") params.mode = selectedMode;
        if (searchQuery.trim()) params.search = searchQuery.trim();

        const data = await apiClient<EventListResponse>("/events", { params });
        if (isMounted) {
          setEvents(data.items || []);
          setIsLoading(false);
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : "Failed to load events.";
          setError(msg);
          setIsLoading(false);
        }
      }
    }

    void loadEvents();

    return () => {
      isMounted = false;
    };
  }, [authLoading, isAuthenticated, selectedCategory, selectedMode, searchQuery]);

  const categories = [
    { label: "All Categories", value: "ALL" },
    { label: "School Visit", value: "SCHOOL_VISIT" },
    { label: "Mock Interview", value: "MOCK_INTERVIEW" },
    { label: "BGV Support", value: "BGV_SUPPORT" },
  ];

  const modes = [
    { label: "All Modes", value: "ALL" },
    { label: "Offline", value: "OFFLINE" },
    { label: "Online", value: "ONLINE" },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="volunteer" />

      <main className="flex-1">
        {/* PAGE HEADER */}
        <section className="py-12 bg-white border-b border-[#EBE6DD]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl">
              <span className="text-xs font-bold uppercase tracking-wider text-[#B45309] bg-[#FFF8E7] px-3.5 py-1.5 rounded-full border border-[#F5B817]/30 inline-block mb-3">
                Volunteering Drives
              </span>
              <h1 className="text-3xl sm:text-4xl font-extrabold text-[#1F2421]">
                Discover Volunteer Opportunities
              </h1>
              <p className="text-sm text-[#4B5563] mt-2">
                Explore upcoming school visits, career readiness sessions, and background verification drives.
              </p>
            </div>
          </div>
        </section>

        {/* CATALOGUE CONTENT */}
        <section className="py-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {/* If user is not authenticated: Show clear informative gate */}
            {!authLoading && !isAuthenticated ? (
              <div className="max-w-3xl mx-auto bg-white rounded-3xl p-8 sm:p-12 border border-[#EBE6DD] shadow-sm text-center space-y-6">
                <div className="w-14 h-14 rounded-2xl bg-[#FFF8E7] border border-[#F5B817]/40 flex items-center justify-center text-[#B45309] mx-auto">
                  <Lock className="w-7 h-7" />
                </div>

                <div className="space-y-2">
                  <h2 className="text-2xl font-bold text-[#1F2421]">
                    Volunteer Authentication Required
                  </h2>
                  <p className="text-sm text-[#6B7280] max-w-lg mx-auto leading-relaxed">
                    Under Maatram Foundation safeguarding and child protection guidelines, real event locations, dates,
                    and registration rosters are exclusively accessible to verified, registered volunteers.
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
                  <Link href="/login?redirect=/events">
                    <Button variant="primary" size="md" className="w-full sm:w-auto px-6">
                      Login to View Opportunities
                    </Button>
                  </Link>
                  <Link href="/register">
                    <Button variant="outline" size="md" className="w-full sm:w-auto px-6">
                      Register as Volunteer
                    </Button>
                  </Link>
                </div>

                {/* Opportunity Track Previews */}
                <div className="pt-8 border-t border-[#EBE6DD] grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
                  <div className="p-4 rounded-xl bg-[#FAF8F3] border border-[#EBE6DD]">
                    <div className="font-bold text-xs text-[#946C00] uppercase mb-1">Track 1</div>
                    <div className="text-sm font-bold text-[#1F2421]">School Visits</div>
                    <div className="text-xs text-[#6B7280] mt-1">In-person guidance at rural government schools.</div>
                  </div>
                  <div className="p-4 rounded-xl bg-[#FAF8F3] border border-[#EBE6DD]">
                    <div className="font-bold text-xs text-[#1D4ED8] uppercase mb-1">Track 2</div>
                    <div className="text-sm font-bold text-[#1F2421]">Mock Interviews</div>
                    <div className="text-xs text-[#6B7280] mt-1">Online & hybrid 1-on-1 career coaching.</div>
                  </div>
                  <div className="p-4 rounded-xl bg-[#FAF8F3] border border-[#EBE6DD]">
                    <div className="font-bold text-xs text-[#15803D] uppercase mb-1">Track 3</div>
                    <div className="text-sm font-bold text-[#1F2421]">BGV Support</div>
                    <div className="text-xs text-[#6B7280] mt-1">Home verification for scholarship applicants.</div>
                  </div>
                </div>
              </div>
            ) : (
              /* Authenticated User: Full Event Discovery Experience */
              <div className="space-y-6">
                {/* Search & Filter Bar */}
                <div className="bg-white p-4 sm:p-6 rounded-2xl border border-[#EBE6DD] shadow-sm flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
                  {/* Category Filter Pills */}
                  <div className="flex flex-wrap items-center gap-2">
                    {categories.map((c) => (
                      <button
                        key={c.value}
                        onClick={() => setSelectedCategory(c.value)}
                        className={`text-xs font-semibold px-3 py-1.5 rounded-full transition-colors ${
                          selectedCategory === c.value
                            ? "bg-[#F5B817] text-[#1F2421] shadow-sm"
                            : "bg-[#FAF8F3] text-[#4B5563] hover:bg-[#F3F4F6] border border-[#EBE6DD]"
                        }`}
                      >
                        {c.label}
                      </button>
                    ))}
                  </div>

                  {/* Mode Selector & Search */}
                  <div className="flex items-center gap-3">
                    <select
                      value={selectedMode}
                      onChange={(e) => setSelectedMode(e.target.value)}
                      className="text-xs font-medium bg-[#FAF8F3] border border-[#D1D5DB] rounded-lg px-3 py-2 text-[#374151] focus:outline-none focus:ring-2 focus:ring-[#F5B817]"
                    >
                      {modes.map((m) => (
                        <option key={m.value} value={m.value}>
                          {m.label}
                        </option>
                      ))}
                    </select>

                    <div className="relative flex-1 sm:w-64">
                      <Search className="w-4 h-4 text-[#9CA3AF] absolute left-3 top-1/2 -translate-y-1/2" />
                      <input
                        type="text"
                        placeholder="Search events..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full text-xs bg-[#FAF8F3] border border-[#D1D5DB] rounded-lg pl-9 pr-3 py-2 text-[#374151] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#F5B817]"
                      />
                    </div>
                  </div>
                </div>

                {/* Loading State */}
                {isLoading && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1, 2, 3].map((n) => (
                      <div key={n} className="bg-white rounded-2xl p-6 border border-[#EBE6DD] animate-pulse space-y-4">
                        <div className="h-4 bg-gray-200 rounded w-1/3" />
                        <div className="h-6 bg-gray-200 rounded w-3/4" />
                        <div className="h-16 bg-gray-100 rounded" />
                        <div className="h-10 bg-gray-200 rounded" />
                      </div>
                    ))}
                  </div>
                )}

                {/* Error State */}
                {error && !isLoading && (
                  <div className="bg-[#FEF2F2] border border-[#F87171] rounded-2xl p-6 text-center space-y-3">
                    <AlertCircle className="w-6 h-6 text-[#DC2626] mx-auto" />
                    <p className="text-sm font-semibold text-[#991B1B]">{error}</p>
                    <Button variant="outline" size="sm" onClick={() => fetchEvents()}>
                      Try Again
                    </Button>
                  </div>
                )}

                {/* Empty State */}
                {!isLoading && !error && events.length === 0 && (
                  <div className="bg-white rounded-2xl p-12 text-center border border-[#EBE6DD] space-y-3">
                    <Calendar className="w-10 h-10 text-[#9CA3AF] mx-auto" />
                    <h3 className="text-base font-bold text-[#1F2421]">No Events Found</h3>
                    <p className="text-xs text-[#6B7280] max-w-sm mx-auto">
                      There are currently no published volunteering opportunities matching your filter criteria. Check back soon!
                    </p>
                  </div>
                )}

                {/* Live Events Grid */}
                {!isLoading && !error && events.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {events.map((event) => {
                      const startDate = new Date(event.start_time);
                      const formattedDate = format(startDate, "dd MMM yyyy");
                      const formattedTime = format(startDate, "hh:mm a");

                      return (
                        <Card key={event.id} className="p-6 bg-white border-[#EBE6DD] flex flex-col justify-between hover:shadow-md transition-shadow">
                          <div>
                            <div className="flex items-center justify-between mb-3">
                              <Badge variant={event.mode === "ONLINE" ? "brand" : "neutral"}>
                                {event.category.replace(/_/g, " ")}
                              </Badge>
                              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#FAF8F3] text-[#4B5563] border border-[#EBE6DD]">
                                {event.mode}
                              </span>
                            </div>

                            <h3 className="text-lg font-bold text-[#1F2421] mb-2 line-clamp-2">
                              {event.title}
                            </h3>

                            {event.description && (
                              <p className="text-xs text-[#4B5563] mb-4 line-clamp-3 leading-relaxed">
                                {event.description}
                              </p>
                            )}

                            <div className="space-y-2 text-xs text-[#6B7280] mb-6 pt-2 border-t border-[#F3F4F6]">
                              <div className="flex items-center gap-2">
                                <Calendar className="w-4 h-4 text-[#F5B817] shrink-0" />
                                <span>{formattedDate} at {formattedTime}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                {event.mode === "ONLINE" ? (
                                  <>
                                    <Video className="w-4 h-4 text-[#F5B817] shrink-0" />
                                    <span>Online Meeting</span>
                                  </>
                                ) : (
                                  <>
                                    <MapPin className="w-4 h-4 text-[#F5B817] shrink-0" />
                                    <span className="truncate">{event.location || "Location to be announced"}</span>
                                  </>
                                )}
                              </div>
                              <div className="flex items-center gap-2">
                                <Users className="w-4 h-4 text-[#F5B817] shrink-0" />
                                <span>
                                  {event.capacity} volunteers needed ({event.registered_count} applied)
                                </span>
                              </div>
                            </div>
                          </div>

                          <Link href={`/events/${event.id}`}>
                            <Button variant="primary" size="sm" className="w-full justify-center">
                              <span>View Details & Register</span>
                              <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                            </Button>
                          </Link>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
