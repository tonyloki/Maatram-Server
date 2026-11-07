"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Calendar,
  Plus,
  Search,
  MapPin,
  Globe,
  Clock,
  Users,
  ChevronRight,
  Filter,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Copy,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { EventResponse, EventListResponse, EventStatus, EventCategory } from "@/types";

export default function AdminEventsPage() {
  const [events, setEvents] = useState<EventResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [categoryFilter, setCategoryFilter] = useState<string>("ALL");
  const [search, setSearch] = useState("");
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams();
      if (statusFilter !== "ALL") params.append("status", statusFilter);
      if (categoryFilter !== "ALL") params.append("category", categoryFilter);
      if (search.trim()) params.append("search", search.trim());
      params.append("page", "1");
      params.append("limit", "50");

      const res = await apiClient.get<EventListResponse>(`/events?${params.toString()}`);
      setEvents(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setError(e.message || "Failed to load events.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [statusFilter, categoryFilter, search]);

  const handlePublish = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    try {
      setActionLoadingId(id);
      await apiClient.post(`/events/${id}/publish`);
      await fetchEvents();
    } catch (err: unknown) {
      const errorObj = err as { message?: string };
      alert(errorObj.message || "Failed to publish event.");
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleCloseRegistration = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    try {
      setActionLoadingId(id);
      await apiClient.post(`/events/${id}/close-registration`);
      await fetchEvents();
    } catch (err: unknown) {
      const errorObj = err as { message?: string };
      alert(errorObj.message || "Failed to close registration.");
    } finally {
      setActionLoadingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight flex items-center gap-2.5">
            <Calendar className="w-7 h-7 text-[#F5B817]" />
            Manage Events & Operations
          </h1>
          <p className="text-sm text-charcoal-500 mt-1">
            Create events, review registrations, manage participant selection, and complete gamification awards.
          </p>
        </div>
        <Link
          href="/admin/events/create"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#F5B817] hover:bg-[#E5A800] text-[#1F2421] font-bold text-xs rounded-xl shadow-xs transition"
        >
          <Plus className="w-4 h-4" />
          Create New Event
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-stone-200 shadow-xs space-y-3">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Status Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0 scrollbar-none">
            {(["ALL", "DRAFT", "PUBLISHED", "REGISTRATION_CLOSED", "COMPLETED", "CANCELLED"] as const).map((st) => (
              <button
                key={st}
                type="button"
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition whitespace-nowrap ${
                  statusFilter === st
                    ? "bg-[#F5B817] text-[#1F2421] shadow-xs"
                    : "bg-stone-100 text-charcoal-600 hover:bg-stone-200/70"
                }`}
              >
                {st === "ALL"
                  ? "All Statuses"
                  : st === "REGISTRATION_CLOSED"
                  ? "Reg Closed"
                  : st.charAt(0) + st.slice(1).toLowerCase()}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative w-full md:w-72">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search event title or location..."
              className="w-full text-xs pl-9 pr-3 py-2 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
            />
            <Search className="w-4 h-4 text-stone-400 absolute left-2.5 top-2.5 pointer-events-none" />
          </div>
        </div>

        {/* Category Filter */}
        <div className="flex items-center gap-2 pt-2 border-t border-stone-100 text-xs">
          <Filter className="w-3.5 h-3.5 text-stone-400 shrink-0" />
          <span className="font-semibold text-charcoal-500">Category:</span>
          <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none">
            {(["ALL", "SCHOOL_VISIT", "MOCK_INTERVIEW", "BGV_SUPPORT", "CAREER_GUIDANCE", "OTHER"] as const).map(
              (cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setCategoryFilter(cat)}
                  className={`px-2.5 py-1 rounded text-[11px] font-medium transition ${
                    categoryFilter === cat
                      ? "bg-charcoal-900 text-white"
                      : "bg-stone-100 text-charcoal-600 hover:bg-stone-200"
                  }`}
                >
                  {cat === "ALL"
                    ? "All Categories"
                    : cat.replace("_", " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase())}
                </button>
              )
            )}
          </div>
        </div>
      </div>

      {/* Events Listing */}
      {loading ? (
        <div className="py-20 text-center bg-white rounded-xl border border-stone-200">
          <div className="w-8 h-8 border-3 border-[#F5B817] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs text-charcoal-500 font-medium">Loading events catalogue...</p>
        </div>
      ) : error ? (
        <div className="py-16 text-center text-red-600 bg-white rounded-xl border border-red-200">
          <p className="text-sm font-semibold">{error}</p>
        </div>
      ) : events.length === 0 ? (
        <div className="py-20 text-center bg-white rounded-xl border border-stone-200">
          <Calendar className="w-10 h-10 text-stone-300 mx-auto mb-3" />
          <p className="text-sm font-bold text-charcoal-700">No events found</p>
          <p className="text-xs text-charcoal-500 mt-1">
            Try resetting your filters or create a new event above.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {events.map((ev) => {
            const startDate = new Date(ev.start_time);
            const endDate = new Date(ev.end_time);

            return (
              <div
                key={ev.id}
                className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs hover:border-amber-300 transition flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                {/* Event Basic Info */}
                <div className="space-y-2 max-w-2xl">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider ${
                        ev.status === "PUBLISHED"
                          ? "bg-emerald-100 text-emerald-800"
                          : ev.status === "DRAFT"
                          ? "bg-stone-100 text-charcoal-700"
                          : ev.status === "REGISTRATION_CLOSED"
                          ? "bg-amber-100 text-amber-900"
                          : ev.status === "COMPLETED"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {ev.status.replace("_", " ")}
                    </span>
                    <span className="px-2 py-0.5 bg-amber-50 text-amber-800 rounded text-[11px] font-semibold">
                      {ev.category.replace("_", " ")}
                    </span>
                    <span className="px-2 py-0.5 bg-stone-100 text-charcoal-600 rounded text-[11px] font-medium flex items-center gap-1">
                      {ev.mode === "ONLINE" ? <Globe className="w-3 h-3" /> : <MapPin className="w-3 h-3" />}
                      {ev.mode}
                    </span>
                  </div>

                  <Link href={`/admin/events/${ev.id}`} className="block group">
                    <h3 className="text-lg font-bold text-charcoal-900 group-hover:text-amber-600 transition tracking-tight">
                      {ev.title}
                    </h3>
                  </Link>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-charcoal-500">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-stone-400" />
                      {startDate.toLocaleDateString("en-IN", {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      })}{" "}
                      •{" "}
                      {startDate.toLocaleTimeString("en-IN", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </div>
                    {ev.location && (
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-stone-400" />
                        {ev.location}
                      </div>
                    )}
                    <div className="flex items-center gap-1">
                      <Users className="w-3.5 h-3.5 text-stone-400" />
                      Capacity: <strong>{ev.capacity}</strong> volunteers
                    </div>
                  </div>
                </div>

                {/* Event Actions & Navigation */}
                <div className="flex flex-wrap items-center gap-2 self-start md:self-auto shrink-0">
                  {/* Status-specific action */}
                  {ev.status === "DRAFT" && (
                    <button
                      type="button"
                      disabled={actionLoadingId === ev.id}
                      onClick={(e) => handlePublish(ev.id, e)}
                      className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Publish
                    </button>
                  )}
                  {ev.status === "PUBLISHED" && (
                    <button
                      type="button"
                      disabled={actionLoadingId === ev.id}
                      onClick={(e) => handleCloseRegistration(ev.id, e)}
                      className="px-3 py-1.5 bg-stone-800 hover:bg-stone-700 text-white rounded-lg text-xs font-semibold transition"
                    >
                      Close Reg
                    </button>
                  )}

                  {/* Operational links */}
                  <Link
                    href={`/admin/events/${ev.id}/participants`}
                    className="px-3 py-1.5 bg-amber-100 hover:bg-amber-200 text-amber-900 rounded-lg text-xs font-bold transition flex items-center gap-1"
                  >
                    <Users className="w-3.5 h-3.5" />
                    Participants
                  </Link>

                  <Link
                    href={`/admin/events/${ev.id}/attendance`}
                    className="px-3 py-1.5 bg-stone-100 hover:bg-stone-200 text-charcoal-700 rounded-lg text-xs font-semibold transition"
                  >
                    Attendance
                  </Link>

                  <Link
                    href={`/admin/events/${ev.id}`}
                    className="p-1.5 text-stone-400 hover:text-charcoal-900 rounded-lg hover:bg-stone-100 transition"
                    title="View Event Details"
                  >
                    <ChevronRight className="w-5 h-5" />
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

