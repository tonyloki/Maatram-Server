"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  ArrowLeft,
  Calendar,
  Clock,
  MapPin,
  Globe,
  Users,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Award,
  ChevronRight,
  ShieldCheck,
  Send,
  UserCheck,
  UserX,
  FileText,
  Sparkles,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import {
  EventResponse,
  RegistrationResponse,
  RegistrationListResponse,
  AttendanceRecordResponse,
  AttendanceListResponse,
  EventCompletionPreviewResponse,
  EventCompletionResponse,
} from "@/types";

type EventTab = "subscribed" | "selected" | "attendance" | "completion";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function AdminEventDetailPage({ params }: PageProps) {
  const { id } = use(params);
  const searchParams = useSearchParams();
  const tabCandidate = searchParams.get("tab");
  const initialTab: EventTab =
    tabCandidate === "selected" || tabCandidate === "attendance" || tabCandidate === "completion"
      ? tabCandidate
      : "subscribed";

  const [activeTab, setActiveTab] = useState<EventTab>(initialTab);

  const [event, setEvent] = useState<EventResponse | null>(null);
  const [registrations, setRegistrations] = useState<RegistrationResponse[]>([]);
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecordResponse[]>([]);
  const [completionPreview, setCompletionPreview] = useState<EventCompletionPreviewResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selection states
  const [selectedRegIds, setSelectedRegIds] = useState<string[]>([]);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  // Manual attendance correction modal
  const [correctingRecord, setCorrectingRecord] = useState<AttendanceRecordResponse | null>(null);
  const [correctionHours, setCorrectionHours] = useState<string>("4.0");
  const [correctionStatus, setCorrectionStatus] = useState<"ATTENDED" | "INCOMPLETE" | "ABSENT">("ATTENDED");
  const [correctionReason, setCorrectionReason] = useState<string>("");

  // Completion modal
  const [completeModalOpen, setCompleteModalOpen] = useState(false);
  const [completionSuccess, setCompletionSuccess] = useState<EventCompletionResponse | null>(null);

  const fetchEventData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [evRes, regRes, attRes] = await Promise.all([
        apiClient.get<EventResponse>(`/events/${id}`),
        apiClient.get<RegistrationListResponse>(`/events/${id}/registrations`),
        apiClient.get<AttendanceListResponse>(`/events/${id}/attendance`),
      ]);

      setEvent(evRes.data);
      setRegistrations(regRes.data.items || []);
      setAttendanceRecords(attRes.data.items || []);

      // If activeTab is completion, also load preview
      if (activeTab === "completion" || evRes.data.status === "REGISTRATION_CLOSED") {
        try {
          const previewRes = await apiClient.get<EventCompletionPreviewResponse>(
            `/events/${id}/completion-preview`
          );
          setCompletionPreview(previewRes.data);
        } catch {
          // completion preview might fail if no attendance or draft
        }
      }
    } catch (err: unknown) {
      const e = err as { message?: string };
      setError(e.message || "Failed to load event data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEventData();
  }, [id, activeTab]);

  // Tab filtering
  const subscribedList = registrations.filter(
    (r) => r.status === "SUBSCRIBED" || r.status === "WAITLISTED"
  );
  const selectedList = registrations.filter((r) => r.status === "SELECTED");
  const attendedCount = attendanceRecords.filter((a) => a.status === "ATTENDED").length;

  const totalCreditedHours = attendanceRecords.reduce((acc, curr) => {
    return acc + (Number(curr.hours_credited) || 0);
  }, 0);

  // Batch Select action
  const handleBatchSelect = async () => {
    if (selectedRegIds.length === 0) return;
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient.post(`/events/${id}/select`, {
        registration_ids: selectedRegIds,
      });
      setSelectedRegIds([]);
      await fetchEventData();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to select registrations.");
    } finally {
      setActionLoading(false);
    }
  };

  // Single Registration Select
  const handleSingleSelect = async (regId: string) => {
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient.post(`/events/${id}/registrations/${regId}/select`);
      await fetchEventData();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to select registration.");
    } finally {
      setActionLoading(false);
    }
  };

  // Single Waitlist Promote
  const handlePromoteWaitlist = async (regId: string) => {
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient.post(`/events/${id}/waitlist/${regId}/promote`);
      await fetchEventData();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to promote registration.");
    } finally {
      setActionLoading(false);
    }
  };

  // Single Decline / Not Selected
  const handleDecline = async (regId: string) => {
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient.post(`/events/${id}/registrations/${regId}/not-selected`);
      await fetchEventData();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to decline registration.");
    } finally {
      setActionLoading(false);
    }
  };

  // Quick Check-in
  const handleQuickCheckIn = async (profileId: string) => {
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient.post(`/events/${id}/attendance/check-in`, {
        volunteer_profile_ids: [profileId],
      });
      await fetchEventData();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to check in volunteer.");
    } finally {
      setActionLoading(false);
    }
  };

  // Quick Check-out
  const handleQuickCheckOut = async (profileId: string) => {
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient.post(`/events/${id}/attendance/check-out`, {
        volunteer_profile_ids: [profileId],
      });
      await fetchEventData();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to check out volunteer.");
    } finally {
      setActionLoading(false);
    }
  };

  // Attendance Correction Submit
  const handleAttendanceCorrection = async () => {
    if (!correctingRecord) return;
    if (correctionReason.trim().length < 3) {
      setActionError("Please provide an explicit audit reason for this correction.");
      return;
    }
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient.post(`/attendance/${correctingRecord.id}/correct`, {
        hours_credited: Number(correctionHours),
        status: correctionStatus,
        reason: correctionReason.trim(),
      });
      setCorrectingRecord(null);
      await fetchEventData();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to correct attendance record.");
    } finally {
      setActionLoading(false);
    }
  };

  // Finalize & Award Gamification
  const handleCompleteAndAward = async () => {
    try {
      setActionLoading(true);
      setActionError(null);
      const res = await apiClient.post<EventCompletionResponse>(
        `/events/${id}/complete-and-award`
      );
      setCompletionSuccess(res.data);
      setCompleteModalOpen(false);
      await fetchEventData();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to complete event.");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-10 h-10 border-4 border-amber-400 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-medium text-charcoal-500">Loading event dashboard...</p>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 text-center">
        <div className="w-14 h-14 bg-red-50 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertTriangle className="w-7 h-7" />
        </div>
        <h2 className="text-xl font-bold text-charcoal-900 mb-2">Event Not Found</h2>
        <p className="text-charcoal-600 mb-6">{error || "Could not retrieve the event dossier."}</p>
        <Link
          href="/admin/events"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-amber-500 text-charcoal-900 font-semibold rounded-lg hover:bg-amber-400"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Events List
        </Link>
      </div>
    );
  }

  const startDate = new Date(event.start_time);
  const endDate = new Date(event.end_time);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Top Breadcrumb */}
      <div>
        <div className="flex items-center gap-2 text-xs font-medium text-charcoal-500 mb-2">
          <Link href="/admin/events" className="hover:text-charcoal-900 transition flex items-center gap-1">
            <ArrowLeft className="w-3.5 h-3.5" />
            Events
          </Link>
          <span>/</span>
          <span className="text-charcoal-800 font-semibold truncate max-w-md">{event.title}</span>
        </div>

        {/* Screen 8 Header */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight">
                {event.title}
              </h1>
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${
                  event.status === "PUBLISHED"
                    ? "bg-emerald-100 text-emerald-800"
                    : event.status === "COMPLETED"
                    ? "bg-blue-100 text-blue-800"
                    : event.status === "REGISTRATION_CLOSED"
                    ? "bg-amber-100 text-amber-900"
                    : "bg-stone-100 text-charcoal-700"
                }`}
              >
                {event.status.replace("_", " ")}
              </span>
              <span className="px-2.5 py-0.5 bg-amber-100 text-amber-900 rounded text-xs font-semibold">
                {event.category.replace("_", " ")}
              </span>
              <span className="px-2 py-0.5 bg-stone-100 text-charcoal-700 rounded text-xs font-medium">
                {event.mode}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs text-charcoal-500 mt-2">
              <div className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-stone-400" />
                {startDate.toLocaleDateString("en-IN", {
                  day: "numeric",
                  month: "short",
                  year: "numeric",
                })}
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-stone-400" />
                {startDate.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })} -{" "}
                {endDate.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
              </div>
              {event.location && (
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-stone-400" />
                  {event.location}
                </div>
              )}
              <div className="flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-stone-400" />
                <strong>{event.capacity}</strong> required
              </div>
            </div>
          </div>

          {/* Top Right Action: Complete Event */}
          {event.status !== "COMPLETED" && (
            <div className="flex items-center gap-2 self-start lg:self-auto">
              <button
                type="button"
                onClick={async () => {
                  try {
                    const previewRes = await apiClient.get<EventCompletionPreviewResponse>(
                      `/events/${id}/completion-preview`
                    );
                    setCompletionPreview(previewRes.data);
                  } catch {
                    // ignore
                  }
                  setCompleteModalOpen(true);
                }}
                className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-charcoal-950 font-bold text-xs rounded-xl shadow-xs transition flex items-center gap-2"
              >
                <Award className="w-4 h-4" />
                Mark as Completed
              </button>
            </div>
          )}
        </div>
      </div>

      {actionError && (
        <div className="p-3 bg-red-50 text-red-700 text-xs rounded-xl border border-red-200">
          {actionError}
        </div>
      )}

      {completionSuccess && (
        <div className="p-4 bg-emerald-50 text-emerald-800 text-xs rounded-xl border border-emerald-200 flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <div>
            <div className="font-bold text-sm">Event Finalized & Gamification Points Awarded!</div>
            <div>
              {completionSuccess.volunteers_awarded} volunteers received exact points (
              {completionSuccess.total_points_awarded} total pts) credited to the immutable ledger.
            </div>
          </div>
        </div>
      )}

      {/* 4 Metric Summary Cards Matching Screen 8 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white border border-stone-200 rounded-xl p-4 shadow-xs">
          <div className="text-2xl font-black text-charcoal-900 tracking-tight">{registrations.length}</div>
          <div className="text-xs font-semibold text-charcoal-500 mt-0.5">Subscribed</div>
        </div>
        <div className="bg-white border border-stone-200 rounded-xl p-4 shadow-xs">
          <div className="text-2xl font-black text-charcoal-900 tracking-tight">{selectedList.length}</div>
          <div className="text-xs font-semibold text-charcoal-500 mt-0.5">Selected</div>
        </div>
        <div className="bg-white border border-stone-200 rounded-xl p-4 shadow-xs">
          <div className="text-2xl font-black text-charcoal-900 tracking-tight">{attendedCount}</div>
          <div className="text-xs font-semibold text-charcoal-500 mt-0.5">Attended</div>
        </div>
        <div className="bg-white border border-stone-200 rounded-xl p-4 shadow-xs">
          <div className="text-2xl font-black text-charcoal-900 tracking-tight">{totalCreditedHours} hrs</div>
          <div className="text-xs font-semibold text-charcoal-500 mt-0.5">Total Hours</div>
        </div>
      </div>

      {/* Screen 8 Tabs Navigation */}
      <div className="border-b border-stone-200 flex items-center gap-6 text-xs font-bold text-charcoal-500">
        <button
          type="button"
          onClick={() => setActiveTab("subscribed")}
          className={`pb-3 transition relative ${
            activeTab === "subscribed"
              ? "text-charcoal-900 border-b-2 border-amber-500 font-extrabold"
              : "hover:text-charcoal-800"
          }`}
        >
          Subscribed ({subscribedList.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("selected")}
          className={`pb-3 transition relative ${
            activeTab === "selected"
              ? "text-charcoal-900 border-b-2 border-amber-500 font-extrabold"
              : "hover:text-charcoal-800"
          }`}
        >
          Selected ({selectedList.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("attendance")}
          className={`pb-3 transition relative ${
            activeTab === "attendance"
              ? "text-charcoal-900 border-b-2 border-amber-500 font-extrabold"
              : "hover:text-charcoal-800"
          }`}
        >
          Attendance ({attendanceRecords.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("completion")}
          className={`pb-3 transition relative ${
            activeTab === "completion"
              ? "text-charcoal-900 border-b-2 border-amber-500 font-extrabold"
              : "hover:text-charcoal-800"
          }`}
        >
          Completion & Points
        </button>
      </div>

      {/* TAB 1: SUBSCRIBED APPLICANTS (SCREEN 8 TABLE) */}
      {activeTab === "subscribed" && (
        <div className="bg-white border border-stone-200 rounded-xl shadow-xs overflow-hidden space-y-3">
          {/* Batch Actions Bar */}
          <div className="p-3 bg-stone-50 border-b border-stone-200 flex items-center justify-between text-xs">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={
                  subscribedList.length > 0 && selectedRegIds.length === subscribedList.length
                }
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedRegIds(subscribedList.map((r) => r.id));
                  } else {
                    setSelectedRegIds([]);
                  }
                }}
                className="w-4 h-4 rounded border-stone-300 text-amber-500 focus:ring-amber-500"
              />
              <span className="text-charcoal-600 font-medium">
                {selectedRegIds.length} of {subscribedList.length} applicants selected
              </span>
            </div>

            {selectedRegIds.length > 0 && (
              <button
                type="button"
                disabled={actionLoading}
                onClick={handleBatchSelect}
                className="px-4 py-1.5 bg-amber-500 hover:bg-amber-400 text-charcoal-950 font-bold rounded-lg transition text-xs shadow-xs"
              >
                {actionLoading ? "Processing..." : `Confirm Selection (${selectedRegIds.length})`}
              </button>
            )}
          </div>

          {subscribedList.length === 0 ? (
            <div className="py-16 text-center text-charcoal-500 text-xs">
              No pending subscriptions. All applicants have been processed.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-stone-50 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase tracking-wider">
                    <th className="py-3 px-4 w-10"></th>
                    <th className="py-3 px-4">Volunteer</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4">Skills / Notes</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {subscribedList.map((reg) => {
                    const isChecked = selectedRegIds.includes(reg.id);
                    const vol = reg.volunteer;

                    return (
                      <tr key={reg.id} className="hover:bg-amber-50/20 transition">
                        <td className="py-3 px-4">
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedRegIds((prev) => [...prev, reg.id]);
                              } else {
                                setSelectedRegIds((prev) => prev.filter((id) => id !== reg.id));
                              }
                            }}
                            className="w-4 h-4 rounded border-stone-300 text-amber-500 focus:ring-amber-500"
                          />
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-900 font-bold flex items-center justify-center text-xs">
                              {vol ? `${vol.first_name?.[0] || ""}${vol.last_name?.[0] || ""}` : "V"}
                            </div>
                            <div>
                              <div className="font-bold text-charcoal-900 text-xs">
                                {vol ? `${vol.first_name} ${vol.last_name}` : "Volunteer"}
                              </div>
                              <div className="text-[11px] text-charcoal-500">
                                {vol?.email || vol?.mobile_number || "Contact concealed"}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span className="font-semibold text-charcoal-700">
                            {vol?.category || "STUDENT"}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-charcoal-600">
                          {reg.notes || "Standard event registration"}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                              reg.status === "WAITLISTED"
                                ? "bg-purple-100 text-purple-800"
                                : "bg-amber-100 text-amber-900"
                            }`}
                          >
                            {reg.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              type="button"
                              disabled={actionLoading}
                              onClick={() => handleSingleSelect(reg.id)}
                              className="px-3 py-1 bg-amber-500 hover:bg-amber-400 text-charcoal-950 font-bold rounded text-[11px] transition"
                            >
                              Select
                            </button>
                            {reg.status === "WAITLISTED" && (
                              <button
                                type="button"
                                disabled={actionLoading}
                                onClick={() => handlePromoteWaitlist(reg.id)}
                                className="px-2.5 py-1 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded text-[11px] transition"
                              >
                                Promote
                              </button>
                            )}
                            <button
                              type="button"
                              disabled={actionLoading}
                              onClick={() => handleDecline(reg.id)}
                              className="px-2.5 py-1 border border-stone-200 text-red-600 hover:bg-red-50 rounded text-[11px] font-semibold transition"
                            >
                              Decline
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: SELECTED PARTICIPANTS */}
      {activeTab === "selected" && (
        <div className="bg-white border border-stone-200 rounded-xl shadow-xs overflow-hidden">
          {selectedList.length === 0 ? (
            <div className="py-16 text-center text-charcoal-500 text-xs">
              No volunteers selected yet. Go to Subscribed tab to make selections.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-stone-50 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase tracking-wider">
                    <th className="py-3 px-4">Volunteer</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4">Selected On</th>
                    <th className="py-3 px-4">Check-In Quick Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {selectedList.map((reg) => {
                    const vol = reg.volunteer;
                    const isCheckedIn = attendanceRecords.some(
                      (a) => a.volunteer_profile_id === reg.volunteer_profile_id
                    );

                    return (
                      <tr key={reg.id} className="hover:bg-stone-50/50 transition">
                        <td className="py-3 px-4">
                          <div className="font-bold text-charcoal-900">
                            {vol ? `${vol.first_name} ${vol.last_name}` : "Volunteer"}
                          </div>
                          <div className="text-[11px] text-charcoal-500">
                            {vol?.email || vol?.mobile_number}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span className="font-semibold text-charcoal-700">{vol?.category}</span>
                        </td>
                        <td className="py-3 px-4 text-charcoal-500">
                          {reg.selected_at
                            ? new Date(reg.selected_at).toLocaleDateString("en-IN")
                            : "Approved"}
                        </td>
                        <td className="py-3 px-4">
                          {isCheckedIn ? (
                            <span className="inline-flex items-center gap-1 text-emerald-700 font-semibold text-xs">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Checked In
                            </span>
                          ) : (
                            <button
                              type="button"
                              disabled={actionLoading}
                              onClick={() => handleQuickCheckIn(reg.volunteer_profile_id)}
                              className="px-3 py-1 bg-stone-900 hover:bg-stone-800 text-white rounded text-xs font-semibold transition"
                            >
                              Check In
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: ATTENDANCE & CORRECTIONS */}
      {activeTab === "attendance" && (
        <div className="bg-white border border-stone-200 rounded-xl shadow-xs overflow-hidden space-y-3">
          {attendanceRecords.length === 0 ? (
            <div className="py-16 text-center text-charcoal-500 text-xs">
              No attendance records created yet. Check in volunteers from Selected tab.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-stone-50 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase tracking-wider">
                    <th className="py-3 px-4">Volunteer</th>
                    <th className="py-3 px-4">Check-In</th>
                    <th className="py-3 px-4">Check-Out</th>
                    <th className="py-3 px-4">Duration</th>
                    <th className="py-3 px-4">Credited Hours</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Audit Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {attendanceRecords.map((att) => (
                    <tr key={att.id} className="hover:bg-amber-50/20 transition">
                      <td className="py-3 px-4 font-bold text-charcoal-900">
                        {att.volunteer_name || "Volunteer"}
                      </td>
                      <td className="py-3 px-4 text-charcoal-600">
                        {new Date(att.check_in_time).toLocaleTimeString("en-IN", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </td>
                      <td className="py-3 px-4 text-charcoal-600">
                        {att.check_out_time ? (
                          new Date(att.check_out_time).toLocaleTimeString("en-IN", {
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        ) : (
                          <button
                            type="button"
                            disabled={actionLoading}
                            onClick={() => handleQuickCheckOut(att.volunteer_profile_id)}
                            className="px-2 py-0.5 bg-amber-500 text-charcoal-950 font-bold rounded text-[11px]"
                          >
                            Check Out Now
                          </button>
                        )}
                      </td>
                      <td className="py-3 px-4 text-charcoal-600">
                        {att.duration_minutes ? `${att.duration_minutes} min` : "In Progress"}
                      </td>
                      <td className="py-3 px-4 font-bold text-charcoal-900">
                        {att.hours_credited} hrs
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                            att.status === "ATTENDED"
                              ? "bg-emerald-100 text-emerald-800"
                              : att.status === "INCOMPLETE"
                              ? "bg-amber-100 text-amber-900"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {att.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          type="button"
                          onClick={() => {
                            setCorrectingRecord(att);
                            setCorrectionHours(String(att.hours_credited || "4.0"));
                            setCorrectionStatus(att.status);
                            setCorrectionReason("");
                          }}
                          className="px-3 py-1 border border-stone-300 hover:bg-stone-100 text-charcoal-700 font-semibold rounded text-[11px]"
                        >
                          Manual Correction
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: COMPLETION & GAMIFICATION PREVIEW */}
      {activeTab === "completion" && (
        <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs space-y-6">
          <div className="flex items-center justify-between border-b border-stone-100 pb-4">
            <div>
              <h3 className="text-base font-bold text-charcoal-900 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-500" />
                Gamification & Exactly-Once Award Dry-Run
              </h3>
              <p className="text-xs text-charcoal-500 mt-0.5">
                Calculate points formula:{" "}
                <code className="bg-stone-100 px-1 py-0.5 rounded text-amber-800">
                  Total Points = (10 × Event) + (2 × Verified Hours)
                </code>
              </p>
            </div>
            {event.status !== "COMPLETED" && (
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => setCompleteModalOpen(true)}
                className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-charcoal-950 font-bold text-xs rounded-xl shadow-xs transition"
              >
                Execute Completion & Award
              </button>
            )}
          </div>

          {completionPreview ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 bg-stone-50 rounded-lg">
                  <div className="text-xs text-charcoal-500 uppercase font-semibold">
                    Attended Volunteers
                  </div>
                  <div className="text-2xl font-black text-charcoal-900 mt-1">
                    {completionPreview.attended_count}
                  </div>
                </div>
                <div className="p-4 bg-stone-50 rounded-lg">
                  <div className="text-xs text-charcoal-500 uppercase font-semibold">
                    Total Hours To Credit
                  </div>
                  <div className="text-2xl font-black text-charcoal-900 mt-1">
                    {completionPreview.total_hours_to_credit} hrs
                  </div>
                </div>
                <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
                  <div className="text-xs text-amber-800 uppercase font-semibold">
                    Total Gamification Points
                  </div>
                  <div className="text-2xl font-black text-amber-900 mt-1">
                    {completionPreview.total_points_to_award} pts
                  </div>
                </div>
              </div>

              {completionPreview.warnings && completionPreview.warnings.length > 0 && (
                <div className="p-4 bg-amber-50 rounded-lg border border-amber-300 text-xs text-amber-900">
                  <div className="font-bold mb-1 flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-amber-700" />
                    Pre-Completion Audit Warnings:
                  </div>
                  <ul className="list-disc pl-5 space-y-1">
                    {completionPreview.warnings.map((w, idx) => (
                      <li key={idx}>{w}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="py-8 text-center text-xs text-charcoal-500">
              {event.status === "COMPLETED"
                ? "Event has already been completed and awards have been locked in the ledger."
                : "No preview generated yet. Ensure attendees have checked in and checked out."}
            </div>
          )}
        </div>
      )}

      {/* MODAL: MANUAL ATTENDANCE CORRECTION */}
      {correctingRecord && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-stone-200">
            <h3 className="text-lg font-bold text-charcoal-900 mb-1">Audit Attendance Correction</h3>
            <p className="text-xs text-charcoal-600 mb-4">
              Volunteer: <strong>{correctingRecord.volunteer_name}</strong>
            </p>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-charcoal-700 mb-1">
                  Corrected Hours (Decimal):
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  max="24"
                  value={correctionHours}
                  onChange={(e) => setCorrectionHours(e.target.value)}
                  className="w-full p-2.5 bg-stone-50 border border-stone-300 rounded-lg"
                />
              </div>

              <div>
                <label className="block font-semibold text-charcoal-700 mb-1">Status:</label>
                <select
                  value={correctionStatus}
                  onChange={(e) =>
                    setCorrectionStatus(e.target.value as "ATTENDED" | "INCOMPLETE" | "ABSENT")
                  }
                  className="w-full p-2.5 bg-stone-50 border border-stone-300 rounded-lg"
                >
                  <option value="ATTENDED">ATTENDED</option>
                  <option value="INCOMPLETE">INCOMPLETE</option>
                  <option value="ABSENT">ABSENT</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-charcoal-700 mb-1">
                  Correction Reason (Mandatory Audit Log):
                </label>
                <textarea
                  required
                  rows={3}
                  value={correctionReason}
                  onChange={(e) => setCorrectionReason(e.target.value)}
                  placeholder="e.g. Volunteer forgot to check out on site; verified with school mentor"
                  className="w-full p-2.5 bg-stone-50 border border-stone-300 rounded-lg"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 mt-6">
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => setCorrectingRecord(null)}
                className="px-4 py-2 border border-stone-300 text-charcoal-700 rounded-lg text-xs font-semibold hover:bg-stone-50"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={actionLoading}
                onClick={handleAttendanceCorrection}
                className="px-5 py-2 bg-charcoal-900 hover:bg-charcoal-800 text-white font-bold rounded-lg text-xs transition"
              >
                {actionLoading ? "Saving..." : "Save Correction"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: COMPLETE EVENT CONFIRMATION */}
      {completeModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-stone-200">
            <h3 className="text-lg font-bold text-charcoal-900 mb-2">Finalize & Complete Event</h3>
            <p className="text-xs text-charcoal-600 mb-4">
              This action will mark the event as <strong>COMPLETED</strong> and permanently credit{" "}
              <strong>{completionPreview?.total_points_to_award || 0} gamification points</strong> to the
              immutable points ledger.
            </p>

            <div className="flex items-center justify-end gap-3">
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => setCompleteModalOpen(false)}
                className="px-4 py-2 border border-stone-300 text-charcoal-700 rounded-lg text-xs font-semibold hover:bg-stone-50"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={actionLoading}
                onClick={handleCompleteAndAward}
                className="px-5 py-2 bg-amber-500 hover:bg-amber-400 text-charcoal-950 font-bold rounded-lg text-xs transition"
              >
                {actionLoading ? "Finalizing..." : "Confirm & Award Points"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
