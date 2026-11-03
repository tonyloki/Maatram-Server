"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Clock,
  Search,
  CheckCircle2,
  Calendar,
  AlertTriangle,
  ArrowRight,
  Filter,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { EventResponse, EventListResponse } from "@/types";

export default function AdminAttendanceOverviewPage() {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        const res = await apiClient.get<EventListResponse>("/events?limit=50");
        setEvents(res.data.items || []);
      } catch (err: unknown) {
        const e = err as { message?: string };
        setError(e.message || "Failed to load events for attendance.");
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  const filteredEvents = events.filter((ev) =>
    ev.title.toLowerCase().includes(search.toLowerCase()) ||
    (ev.location && ev.location.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight flex items-center gap-2.5">
          <Clock className="w-7 h-7 text-amber-500" />
          Attendance & Verified Hours Central
        </h1>
        <p className="text-sm text-charcoal-500 mt-1">
          Select an event to inspect live check-in timestamps, correct missing checkouts, or audit volunteer hours.
        </p>
      </div>

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-stone-200 shadow-xs flex items-center justify-between gap-4">
        <div className="relative w-full max-w-md">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by event title or venue..."
            className="w-full text-xs pl-9 pr-3 py-2 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-amber-500"
          />
          <Search className="w-4 h-4 text-stone-400 absolute left-2.5 top-2.5 pointer-events-none" />
        </div>
        <div className="text-xs text-charcoal-500">
          Showing <strong>{filteredEvents.length}</strong> events
        </div>
      </div>

      {/* Events Roster */}
      {loading ? (
        <div className="py-20 text-center bg-white rounded-xl border border-stone-200">
          <div className="w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-charcoal-500">Loading events roster...</p>
        </div>
      ) : error ? (
        <div className="py-16 text-center text-red-600 bg-white rounded-xl border border-red-200 text-sm">
          {error}
        </div>
      ) : filteredEvents.length === 0 ? (
        <div className="py-20 text-center bg-white rounded-xl border border-stone-200 text-xs text-charcoal-500">
          No matching events found.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredEvents.map((ev) => {
            const startDate = new Date(ev.start_time);

            return (
              <div
                key={ev.id}
                className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs hover:border-amber-300 transition flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        ev.status === "COMPLETED"
                          ? "bg-blue-100 text-blue-800"
                          : ev.status === "PUBLISHED"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-amber-100 text-amber-900"
                      }`}
                    >
                      {ev.status.replace("_", " ")}
                    </span>
                    <span className="text-[11px] text-charcoal-400 font-medium">
                      {startDate.toLocaleDateString("en-IN", {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      })}
                    </span>
                  </div>

                  <h3 className="font-bold text-charcoal-900 text-base line-clamp-1">{ev.title}</h3>
                  <p className="text-xs text-charcoal-500 mt-1 line-clamp-1">
                    {ev.location || ev.mode}
                  </p>
                </div>

                <div className="pt-4 mt-4 border-t border-stone-100 flex items-center justify-between">
                  <span className="text-xs text-charcoal-500">
                    Capacity: <strong>{ev.capacity}</strong>
                  </span>
                  <Link
                    href={`/admin/events/${ev.id}?tab=attendance`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 hover:bg-amber-400 text-charcoal-950 font-bold rounded-lg text-xs transition"
                  >
                    Open Roster
                    <ArrowRight className="w-3.5 h-3.5" />
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

