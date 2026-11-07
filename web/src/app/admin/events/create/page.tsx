"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Calendar, Save, AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { EventCategory, EventMode } from "@/types";

export default function CreateEventPage() {
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<EventCategory>("SCHOOL_VISIT");
  const [mode, setMode] = useState<EventMode>("OFFLINE");
  const [location, setLocation] = useState("");
  const [meetingUrl, setMeetingUrl] = useState("");
  const [capacity, setCapacity] = useState<number>(20);

  // Dates and times
  const [startDate, setStartDate] = useState("");
  const [startTime, setStartTime] = useState("09:00");
  const [endDate, setEndDate] = useState("");
  const [endTime, setEndTime] = useState("13:00");
  const [regDeadlineDate, setRegDeadlineDate] = useState("");
  const [regDeadlineTime, setRegDeadlineTime] = useState("18:00");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      setError("Please provide both an event title and a description.");
      return;
    }
    if (!startDate || !regDeadlineDate) {
      setError("Please provide start date and registration deadline.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const startIso = new Date(`${startDate}T${startTime}:00`).toISOString();
      const endIso = new Date(`${endDate || startDate}T${endTime}:00`).toISOString();
      const regIso = new Date(`${regDeadlineDate}T${regDeadlineTime}:00`).toISOString();

      const payload = {
        title: title.trim(),
        description: description.trim(),
        category,
        mode,
        location: mode === "OFFLINE" ? location.trim() : null,
        online_meeting_url: mode === "ONLINE" ? meetingUrl.trim() : null,
        capacity_required: Number(capacity),
        start_time: startIso,
        end_time: endIso,
        registration_deadline: regIso,
        timezone: "Asia/Kolkata",
      };

      const res = await apiClient.post<{ id: string }>("/events", payload);
      router.push(`/admin/events/${res.data.id}`);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setError(e.message || "Failed to create event.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-16">
      {/* Header */}
      <div>
        <Link
          href="/admin/events"
          className="inline-flex items-center gap-2 text-sm font-medium text-charcoal-600 hover:text-charcoal-900 transition mb-3"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Events List
        </Link>
        <h1 className="text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight flex items-center gap-2.5">
          <Calendar className="w-7 h-7 text-[#F5B817]" />
          Create New Volunteering Event
        </h1>
        <p className="text-sm text-charcoal-500 mt-1">
          Draft an event for volunteer registration and participation selection.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white border border-stone-200 rounded-xl p-6 sm:p-8 shadow-xs space-y-6">
        {/* Title */}
        <div>
          <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1.5">
            Event Title *
          </label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Government High School Visit - Science Fair Mentoring"
            className="w-full text-sm p-3 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
          />
        </div>

        {/* Category & Mode */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1.5">
              Category *
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as EventCategory)}
              className="w-full text-sm p-3 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
            >
              <option value="SCHOOL_VISIT">School Visit</option>
              <option value="MOCK_INTERVIEW">Mock Interview Session</option>
              <option value="BGV_SUPPORT">BGV Verification Support</option>
              <option value="CAREER_GUIDANCE">Career Guidance Workshop</option>
              <option value="OTHER">Other Community Event</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1.5">
              Delivery Mode *
            </label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as EventMode)}
              className="w-full text-sm p-3 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
            >
              <option value="OFFLINE">Offline (In-Person)</option>
              <option value="ONLINE">Online (Virtual)</option>
            </select>
          </div>
        </div>

        {/* Location or Meeting URL */}
        {mode === "OFFLINE" ? (
          <div>
            <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1.5">
              Physical Location / Venue
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Chennai Higher Secondary School, T. Nagar, Chennai"
              className="w-full text-sm p-3 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
            />
          </div>
        ) : (
          <div>
            <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1.5">
              Online Meeting Link
            </label>
            <input
              type="url"
              value={meetingUrl}
              onChange={(e) => setMeetingUrl(e.target.value)}
              placeholder="e.g. https://meet.google.com/abc-defg-hij"
              className="w-full text-sm p-3 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
            />
          </div>
        )}

        {/* Capacity */}
        <div className="max-w-xs">
          <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1.5">
            Volunteer Capacity Required *
          </label>
          <input
            type="number"
            min={1}
            max={500}
            required
            value={capacity}
            onChange={(e) => setCapacity(Number(e.target.value))}
            className="w-full text-sm p-3 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
          />
        </div>

        {/* Schedule */}
        <div className="pt-4 border-t border-stone-100">
          <h3 className="text-sm font-bold text-charcoal-900 mb-3">Event Schedule & Deadlines</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-charcoal-600 mb-1">Start Date *</label>
              <input
                type="date"
                required
                value={startDate}
                onChange={(e) => {
                  setStartDate(e.target.value);
                  if (!endDate) setEndDate(e.target.value);
                  if (!regDeadlineDate) setRegDeadlineDate(e.target.value);
                }}
                className="w-full text-xs p-2.5 bg-stone-50 border border-stone-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-charcoal-600 mb-1">Start Time *</label>
              <input
                type="time"
                required
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full text-xs p-2.5 bg-stone-50 border border-stone-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-charcoal-600 mb-1">End Date *</label>
              <input
                type="date"
                required
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full text-xs p-2.5 bg-stone-50 border border-stone-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-charcoal-600 mb-1">End Time *</label>
              <input
                type="time"
                required
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full text-xs p-2.5 bg-stone-50 border border-stone-300 rounded-lg"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
            <div>
              <label className="block text-xs font-medium text-charcoal-600 mb-1">
                Registration Deadline Date *
              </label>
              <input
                type="date"
                required
                value={regDeadlineDate}
                onChange={(e) => setRegDeadlineDate(e.target.value)}
                className="w-full text-xs p-2.5 bg-stone-50 border border-stone-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-charcoal-600 mb-1">
                Registration Deadline Time *
              </label>
              <input
                type="time"
                required
                value={regDeadlineTime}
                onChange={(e) => setRegDeadlineTime(e.target.value)}
                className="w-full text-xs p-2.5 bg-stone-50 border border-stone-300 rounded-lg"
              />
            </div>
          </div>
        </div>

        {/* Description */}
        <div>
          <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1.5">
            Event Description & Briefing *
          </label>
          <textarea
            required
            rows={5}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the volunteering objectives, dress code, mentor roles, and orientation instructions..."
            className="w-full text-sm p-3 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
          />
        </div>

        {/* Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-stone-100">
          <Link
            href="/admin/events"
            className="px-5 py-2.5 border border-stone-300 text-charcoal-700 font-semibold rounded-lg text-xs hover:bg-stone-50 transition"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 bg-[#F5B817] hover:bg-[#E5A800] text-[#1F2421] font-bold rounded-lg text-xs shadow-xs transition flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {loading ? "Creating Draft..." : "Create Event Draft"}
          </button>
        </div>
      </form>
    </div>
  );
}

