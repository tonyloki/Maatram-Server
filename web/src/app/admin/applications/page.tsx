"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  SlidersHorizontal,
  CheckCircle2,
  XCircle,
  Clock,
  UserCheck,
  ChevronRight,
  AlertCircle,
  Loader2,
  ShieldAlert,
  ArrowRight,
  Eye,
} from "lucide-react";
import { apiClient, ApiError } from "@/lib/api-client";
import { ApplicationListResponse, ApplicationDetailResponse } from "@/types";
import { fadeInUp, staggerContainer } from "@/lib/animations";

export default function AdminApplicationsPage() {
  const [applications, setApplications] = useState<ApplicationDetailResponse[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [categoryFilter, setCategoryFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Quick Action Dialog state
  const [selectedApp, setSelectedApp] = useState<ApplicationDetailResponse | null>(null);
  const [actionType, setActionType] = useState<"APPROVE" | "REJECT" | null>(null);
  const [actionNotes, setActionNotes] = useState("");
  const [rejectReason, setRejectReason] = useState("");
  const [isSubmittingAction, setIsSubmittingAction] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const loadApplications = useCallback(async () => {
    setError(null);
    try {
      const params: Record<string, string | number> = {
        page,
        page_size: 20,
      };
      if (statusFilter !== "ALL") params.status = statusFilter;
      if (categoryFilter !== "ALL") params.category = categoryFilter;
      if (searchQuery.trim()) params.search = searchQuery.trim();

      const res = await apiClient<ApplicationListResponse>("/applications", { params });
      setApplications(res.items || []);
      setTotalCount(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err: unknown) {
      console.error("Failed to load applications", err);
      setError("Unable to retrieve onboarding applications.");
    } finally {
      setIsLoading(false);
    }
  }, [page, statusFilter, categoryFilter, searchQuery]);

  useEffect(() => {
    void loadApplications();
  }, [loadApplications]);

  const handleDecision = async () => {
    if (!selectedApp || !actionType) return;
    setIsSubmittingAction(true);
    setActionError(null);
    try {
      if (actionType === "APPROVE") {
        await apiClient(`/applications/${selectedApp.id}/approve`, {
          method: "POST",
          body: JSON.stringify({ notes: actionNotes.trim() || undefined }),
        });
      } else {
        if (!rejectReason.trim()) {
          setActionError("A mandatory rejection reason is required.");
          setIsSubmittingAction(false);
          return;
        }
        await apiClient(`/applications/${selectedApp.id}/reject`, {
          method: "POST",
          body: JSON.stringify({ reason: rejectReason.trim() }),
        });
      }
      setSelectedApp(null);
      setActionType(null);
      setActionNotes("");
      setRejectReason("");
      void loadApplications();
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setActionError(err.message || "Failed to submit decision.");
      } else {
        setActionError("An unexpected error occurred while processing decision.");
      }
    } finally {
      setIsSubmittingAction(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "APPROVED":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Approved
          </span>
        );
      case "REJECTED":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-red-50 text-red-800 border border-red-200">
            <XCircle className="w-3 h-3 text-red-600" /> Rejected
          </span>
        );
      case "PENDING":
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
            <Clock className="w-3 h-3 text-amber-600" /> Pending Review
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-charcoal-100 text-charcoal-700">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Title & Count */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-charcoal-900 tracking-tight font-serif flex items-center gap-2.5">
            Volunteer Applications Review
          </h1>
          <p className="text-sm text-charcoal-500 mt-1">
            Review applicant qualifications, verify under-18 parental safeguarding, and decide admission into the portal.
          </p>
        </div>
        <div className="self-start sm:self-auto bg-white border border-charcoal-200/80 rounded-2xl px-4 py-2 text-xs font-bold text-charcoal-700 shadow-2xs">
          Total Applications: <span className="font-extrabold text-charcoal-900">{totalCount}</span>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-white rounded-3xl border border-charcoal-200/80 p-4 shadow-2xs space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="w-5 h-5 text-charcoal-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(1);
            }}
            placeholder="Search by applicant name, email, or mobile number..."
            className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-charcoal-200 text-sm focus:outline-none focus:ring-2 focus:ring-[#F5B817] text-charcoal-900 bg-charcoal-50/50 focus:bg-white transition-all"
          />
        </div>

        {/* Filter Controls Row */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-charcoal-100">
          {/* Status Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none">
            {["ALL", "PENDING", "APPROVED", "REJECTED"].map((st) => (
              <button
                key={st}
                onClick={() => {
                  setStatusFilter(st);
                  setPage(1);
                }}
                className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all whitespace-nowrap ${
                  statusFilter === st
                    ? "bg-charcoal-900 text-[#F5B817] shadow-xs"
                    : "bg-charcoal-100 text-charcoal-600 hover:bg-charcoal-200"
                }`}
              >
                {st === "ALL" ? "All Statuses" : st}
              </button>
            ))}
          </div>

          {/* Category Dropdown */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-charcoal-500 font-bold uppercase tracking-wider">Category:</span>
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setPage(1);
              }}
              className="bg-charcoal-50 border border-charcoal-200 rounded-xl px-3 py-1.5 font-bold text-charcoal-800 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Categories</option>
              <option value="STUDENT">Student</option>
              <option value="ALUMNI">Alumni</option>
              <option value="CORPORATE">Corporate</option>
            </select>
          </div>
        </div>
      </div>

      {/* Applications Table */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-charcoal-200/80 shadow-2xs">
          <Loader2 className="w-8 h-8 text-[#F5B817] animate-spin" />
          <p className="text-sm font-semibold text-charcoal-600 mt-3">Loading volunteer applications...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-3xl p-8 text-center text-red-800 space-y-3">
          <AlertCircle className="w-10 h-10 text-red-500 mx-auto" />
          <h3 className="text-base font-bold">{error}</h3>
          <button
            onClick={() => {
              setIsLoading(true);
              void loadApplications();
            }}
            className="px-5 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-bold shadow-2xs transition-colors"
          >
            Retry
          </button>
        </div>
      ) : applications.length === 0 ? (
        <div className="bg-white rounded-3xl border border-charcoal-200/80 p-12 text-center shadow-2xs">
          <UserCheck className="w-12 h-12 text-charcoal-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-charcoal-900">No applications match current filters</h3>
          <p className="text-sm text-charcoal-500 mt-1 max-w-sm mx-auto">
            Try resetting your filters or clearing search terms to inspect all registered volunteers.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-charcoal-200/80 overflow-hidden shadow-2xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs md:text-sm text-charcoal-700">
              <thead className="bg-charcoal-50/80 border-b border-charcoal-200 text-charcoal-500 uppercase tracking-wider text-[11px] font-bold">
                <tr>
                  <th className="py-3.5 px-5">Applicant</th>
                  <th className="py-3.5 px-4">Category</th>
                  <th className="py-3.5 px-4">Institution / Org</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">Safeguarding</th>
                  <th className="py-3.5 px-4">Submitted</th>
                  <th className="py-3.5 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-charcoal-100">
                {applications.map((app) => {
                  const prof = app.volunteer_profile;
                  const fullName = prof ? `${prof.first_name} ${prof.last_name}` : "Applicant";
                  const orgOrCollege =
                    prof?.student_profile?.college_name ||
                    prof?.alumni_profile?.organisation ||
                    prof?.corporate_profile?.organisation ||
                    "—";

                  return (
                    <tr key={app.id} className="hover:bg-charcoal-50/60 transition-colors">
                      <td className="py-4 px-5">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-full bg-charcoal-100 flex items-center justify-center font-extrabold text-xs text-charcoal-800 flex-shrink-0">
                            {prof?.first_name ? prof.first_name[0] : "A"}
                          </div>
                          <div>
                            <p className="font-bold text-charcoal-900">{fullName}</p>
                            <p className="text-xs text-charcoal-500">{app.user_email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md bg-charcoal-100 text-charcoal-700">
                          {prof?.category || "STUDENT"}
                        </span>
                      </td>
                      <td className="py-4 px-4 font-semibold text-charcoal-800 truncate max-w-[200px]">
                        {orgOrCollege}
                      </td>
                      <td className="py-4 px-4">{getStatusBadge(app.status)}</td>
                      <td className="py-4 px-4">
                        {prof?.parental_consent_status === "PENDING" ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                            <ShieldAlert className="w-3 h-3 text-amber-600" /> Consent Needed
                          </span>
                        ) : prof?.parental_consent_status === "VERIFIED" ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Verified
                          </span>
                        ) : (
                          <span className="text-xs text-charcoal-400">Adult</span>
                        )}
                      </td>
                      <td className="py-4 px-4 text-xs text-charcoal-500 whitespace-nowrap">
                        {new Date(app.submitted_at).toLocaleDateString("en-IN", {
                          day: "numeric",
                          month: "short",
                          year: "numeric",
                        })}
                      </td>
                      <td className="py-4 px-5 text-right whitespace-nowrap">
                        <div className="inline-flex items-center gap-2">
                          <Link
                            href={`/admin/applications/${app.id}`}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl border border-charcoal-200 hover:border-charcoal-400 bg-white text-xs font-bold text-charcoal-800 shadow-2xs hover:bg-charcoal-50 transition-all"
                          >
                            <Eye className="w-3.5 h-3.5 text-charcoal-500" /> View Details
                          </Link>

                          {app.status === "PENDING" && (
                            <>
                              <button
                                onClick={() => {
                                  setSelectedApp(app);
                                  setActionType("APPROVE");
                                }}
                                className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-2xs transition-colors"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => {
                                  setSelectedApp(app);
                                  setActionType("REJECT");
                                }}
                                className="px-3 py-1.5 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold shadow-2xs transition-colors"
                              >
                                Reject
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="p-4 border-t border-charcoal-200/80 flex items-center justify-between text-xs font-bold text-charcoal-600">
              <span>
                Page {page} of {totalPages}
              </span>
              <div className="flex items-center gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="px-3 py-1.5 rounded-xl border border-charcoal-200 bg-white disabled:opacity-40 hover:bg-charcoal-50"
                >
                  Previous
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="px-3 py-1.5 rounded-xl border border-charcoal-200 bg-white disabled:opacity-40 hover:bg-charcoal-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Decision Confirmation Dialog */}
      <AnimatePresence>
        {selectedApp && actionType && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-950/60 backdrop-blur-xs">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-3xl max-w-lg w-full p-6 md:p-8 shadow-2xl border border-charcoal-200 space-y-4"
            >
              <h3 className="text-lg font-bold text-charcoal-900">
                {actionType === "APPROVE" ? "Approve Volunteer Application" : "Reject Volunteer Application"}
              </h3>

              <p className="text-xs md:text-sm text-charcoal-600 leading-relaxed">
                You are about to {actionType === "APPROVE" ? "approve" : "reject"} the application submitted by{" "}
                <span className="font-bold text-charcoal-950">
                  {selectedApp.volunteer_profile?.first_name} {selectedApp.volunteer_profile?.last_name}
                </span>{" "}
                ({selectedApp.user_email}).
              </p>

              {actionType === "APPROVE" ? (
                <div>
                  <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                    Approval Notes (Optional)
                  </label>
                  <textarea
                    rows={3}
                    value={actionNotes}
                    onChange={(e) => setActionNotes(e.target.value)}
                    placeholder="Enter any administrative review notes..."
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs md:text-sm text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-[#F5B817]"
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                    Mandatory Rejection Reason *
                  </label>
                  <textarea
                    rows={3}
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                    placeholder="Provide specific feedback or reason for application denial..."
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-xs md:text-sm text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-red-400"
                    required
                  />
                </div>
              )}

              {actionError && (
                <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs font-semibold flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
                  {actionError}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-charcoal-100">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedApp(null);
                    setActionType(null);
                  }}
                  className="px-4 py-2 rounded-xl text-xs font-bold text-charcoal-600 hover:bg-charcoal-100"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  disabled={isSubmittingAction}
                  onClick={handleDecision}
                  className={`px-5 py-2 rounded-xl text-xs font-bold text-white shadow-2xs transition-colors flex items-center gap-1.5 ${
                    actionType === "APPROVE" ? "bg-emerald-600 hover:bg-emerald-700" : "bg-red-600 hover:bg-red-700"
                  }`}
                >
                  {isSubmittingAction && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  Confirm {actionType === "APPROVE" ? "Approval" : "Rejection"}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

