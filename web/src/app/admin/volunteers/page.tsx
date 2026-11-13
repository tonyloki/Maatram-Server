"use client";

import React, { useState, useEffect, useCallback, Suspense } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Users,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  XCircle,
  GraduationCap,
  Briefcase,
  Building2,
  ChevronLeft,
  ChevronRight,
  Eye,
  Loader2,
  AlertCircle,
  ThumbsUp,
  ThumbsDown,
  X,
  Sparkles,
  UserCheck,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import {
  ApplicationListResponse,
  ApplicationDetailResponse,
  AdminDashboardResponse,
} from "@/types";

type TabType = "ALL" | "PENDING" | "APPROVED" | "REJECTED";

function VolunteersContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = (searchParams.get("tab")?.toUpperCase() as TabType) || "ALL";

  // Tab State
  const [activeTab, setActiveTab] = useState<TabType>(
    ["ALL", "PENDING", "APPROVED", "REJECTED"].includes(initialTab) ? initialTab : "ALL"
  );

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("ALL");
  const [sortBy, setSortBy] = useState<"NEWEST" | "OLDEST" | "NAME">("NEWEST");
  const [page, setPage] = useState(1);
  const pageSize = 15;

  // Data States
  const [applications, setApplications] = useState<ApplicationDetailResponse[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Summary Metrics State (7 canonical stats)
  const [stats, setStats] = useState({
    totalVolunteers: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
    students: 0,
    alumni: 0,
    corporate: 0,
  });

  // Quick Action Modal State (Approve / Reject)
  const [selectedApp, setSelectedApp] = useState<ApplicationDetailResponse | null>(null);
  const [actionType, setActionType] = useState<"APPROVE" | "REJECT" | null>(null);
  const [decisionNotes, setDecisionNotes] = useState("");
  const [rejectReason, setRejectReason] = useState("");
  const [isSubmittingDecision, setIsSubmittingDecision] = useState(false);
  const [decisionError, setDecisionError] = useState<string | null>(null);
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);

  // Fetch summary stats from PostgreSQL via /admin/dashboard
  const fetchStats = useCallback(async () => {
    try {
      const data = await apiClient<AdminDashboardResponse>("/admin/dashboard", {
        skipCache: true,
      });
      if (data) {
        setStats({
          totalVolunteers: data.applications?.total ?? data.volunteers?.total_volunteers ?? 0,
          pending: data.applications?.pending ?? 0,
          approved: data.applications?.approved ?? 0,
          rejected: data.applications?.rejected ?? 0,
          students: data.volunteers?.by_category?.STUDENT ?? 0,
          alumni: data.volunteers?.by_category?.ALUMNI ?? 0,
          corporate: data.volunteers?.by_category?.CORPORATE ?? 0,
        });
      }
    } catch (err: unknown) {
      console.warn("Failed to fetch dashboard summary metrics:", err);
    }
  }, []);

  // Fetch list of volunteers based on active tab and filters
  const fetchVolunteers = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: Record<string, string | number> = {
        page,
        page_size: pageSize,
      };

      if (activeTab !== "ALL") {
        params.status = activeTab;
      }
      if (categoryFilter !== "ALL") {
        params.category = categoryFilter;
      }
      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }

      const res = await apiClient<ApplicationListResponse>("/applications", {
        params,
        skipCache: true,
      });

      let items = res.items || [];

      // Client-side sort if requested
      if (sortBy === "NAME") {
        items = [...items].sort((a, b) =>
          (a.volunteer_profile?.first_name || "").localeCompare(
            b.volunteer_profile?.first_name || ""
          )
        );
      } else if (sortBy === "OLDEST") {
        items = [...items].sort(
          (a, b) =>
            new Date(a.submitted_at).getTime() - new Date(b.submitted_at).getTime()
        );
      }

      setApplications(items);
      setTotalCount(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load volunteers directory.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [activeTab, categoryFilter, searchQuery, sortBy, page]);

  useEffect(() => {
    void fetchStats();
  }, [fetchStats]);

  useEffect(() => {
    void fetchVolunteers();
  }, [fetchVolunteers]);

  // Handle Tab Switch
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    setPage(1);
    router.replace(`/admin/volunteers?tab=${tab.toLowerCase()}`, { scroll: false });
  };

  // Handle Search Submission
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setSearchQuery(searchInput);
  };

  // Submit Approval or Rejection
  const handleDecisionSubmit = async () => {
    if (!selectedApp || !actionType) return;
    setIsSubmittingDecision(true);
    setDecisionError(null);

    try {
      if (actionType === "APPROVE") {
        await apiClient(`/applications/${selectedApp.id}/approve`, {
          method: "POST",
          body: JSON.stringify({ notes: decisionNotes.trim() || undefined }),
        });
        setFeedbackSuccess(
          `Volunteer ${selectedApp.volunteer_profile.first_name} has been successfully approved.`
        );
      } else {
        if (!rejectReason.trim()) {
          setDecisionError("A reason is mandatory when rejecting an application.");
          setIsSubmittingDecision(false);
          return;
        }
        await apiClient(`/applications/${selectedApp.id}/reject`, {
          method: "POST",
          body: JSON.stringify({ reason: rejectReason.trim() }),
        });
        setFeedbackSuccess(
          `Application for ${selectedApp.volunteer_profile.first_name} has been rejected.`
        );
      }

      setSelectedApp(null);
      setActionType(null);
      setDecisionNotes("");
      setRejectReason("");

      // Refresh list and stats
      void fetchStats();
      void fetchVolunteers();
      setTimeout(() => setFeedbackSuccess(null), 4000);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Failed to process application decision. Please verify permissions.";
      setDecisionError(msg);
    } finally {
      setIsSubmittingDecision(false);
    }
  };

  // Helper to extract display location
  const getLocation = (app: ApplicationDetailResponse): string => {
    const prof = app.volunteer_profile;
    if (prof.category === "STUDENT" && prof.student_profile?.college_name) {
      return prof.student_profile.college_name;
    }
    if (prof.category === "ALUMNI") {
      if (prof.alumni_profile?.organisation) {
        return prof.alumni_profile.location
          ? `${prof.alumni_profile.organisation}, ${prof.alumni_profile.location}`
          : prof.alumni_profile.organisation;
      }
      return prof.alumni_profile?.location || "Tamil Nadu";
    }
    if (prof.category === "CORPORATE") {
      if (prof.corporate_profile?.organisation) {
        return prof.corporate_profile.location
          ? `${prof.corporate_profile.organisation}, ${prof.corporate_profile.location}`
          : prof.corporate_profile.organisation;
      }
      return prof.corporate_profile?.location || "Chennai";
    }
    return "Tamil Nadu";
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16 animate-in fade-in-50 duration-200">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-charcoal-900 tracking-tight flex items-center gap-2.5">
            <Users className="w-7 h-7 text-[#F5B817]" />
            Volunteers Management
          </h1>
          <p className="text-xs sm:text-sm text-charcoal-500 mt-1">
            Review onboarding applications, verify safeguarding, and inspect volunteer roster records.
          </p>
        </div>
      </div>

      {/* Success Notification */}
      {feedbackSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-center gap-3 shadow-xs">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <p className="text-sm font-semibold">{feedbackSuccess}</p>
        </div>
      )}

      {/* 4. SUMMARY STATS (7 Cards Format) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 sm:gap-4">
        {/* 1. Total Volunteers */}
        <div className="bg-white rounded-2xl border border-stone-200/80 p-4 shadow-2xs flex flex-col justify-between">
          <span className="text-[11px] font-bold text-charcoal-500 uppercase tracking-wider">
            Total Volunteers
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-charcoal-900">{stats.totalVolunteers}</span>
            <Users className="w-4 h-4 text-stone-400" />
          </div>
        </div>

        {/* 2. Pending */}
        <div
          onClick={() => handleTabChange("PENDING")}
          className={`cursor-pointer rounded-2xl border p-4 shadow-2xs flex flex-col justify-between transition ${
            activeTab === "PENDING"
              ? "bg-amber-50/70 border-amber-300 ring-2 ring-amber-400/40"
              : "bg-white border-stone-200/80 hover:border-amber-200"
          }`}
        >
          <span className="text-[11px] font-bold text-amber-700 uppercase tracking-wider">
            Pending
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-amber-900">{stats.pending}</span>
            <Clock className="w-4 h-4 text-amber-500" />
          </div>
        </div>

        {/* 3. Approved */}
        <div
          onClick={() => handleTabChange("APPROVED")}
          className={`cursor-pointer rounded-2xl border p-4 shadow-2xs flex flex-col justify-between transition ${
            activeTab === "APPROVED"
              ? "bg-emerald-50/70 border-emerald-300 ring-2 ring-emerald-400/40"
              : "bg-white border-stone-200/80 hover:border-emerald-200"
          }`}
        >
          <span className="text-[11px] font-bold text-emerald-700 uppercase tracking-wider">
            Approved
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-emerald-900">{stats.approved}</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
        </div>

        {/* 4. Rejected */}
        <div
          onClick={() => handleTabChange("REJECTED")}
          className={`cursor-pointer rounded-2xl border p-4 shadow-2xs flex flex-col justify-between transition ${
            activeTab === "REJECTED"
              ? "bg-red-50/70 border-red-300 ring-2 ring-red-400/40"
              : "bg-white border-stone-200/80 hover:border-red-200"
          }`}
        >
          <span className="text-[11px] font-bold text-red-700 uppercase tracking-wider">
            Rejected
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-red-900">{stats.rejected}</span>
            <XCircle className="w-4 h-4 text-red-500" />
          </div>
        </div>

        {/* 5. Student */}
        <div
          onClick={() => setCategoryFilter(categoryFilter === "STUDENT" ? "ALL" : "STUDENT")}
          className={`cursor-pointer rounded-2xl border p-4 shadow-2xs flex flex-col justify-between transition ${
            categoryFilter === "STUDENT"
              ? "bg-blue-50/70 border-blue-300 ring-2 ring-blue-400/40"
              : "bg-white border-stone-200/80 hover:border-blue-200"
          }`}
        >
          <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider">
            Student
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-blue-900">{stats.students}</span>
            <GraduationCap className="w-4 h-4 text-blue-500" />
          </div>
        </div>

        {/* 6. Alumni */}
        <div
          onClick={() => setCategoryFilter(categoryFilter === "ALUMNI" ? "ALL" : "ALUMNI")}
          className={`cursor-pointer rounded-2xl border p-4 shadow-2xs flex flex-col justify-between transition ${
            categoryFilter === "ALUMNI"
              ? "bg-purple-50/70 border-purple-300 ring-2 ring-purple-400/40"
              : "bg-white border-stone-200/80 hover:border-purple-200"
          }`}
        >
          <span className="text-[11px] font-bold text-purple-700 uppercase tracking-wider">
            Alumni
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-purple-900">{stats.alumni}</span>
            <Briefcase className="w-4 h-4 text-purple-500" />
          </div>
        </div>

        {/* 7. Corporate Panelist */}
        <div
          onClick={() => setCategoryFilter(categoryFilter === "CORPORATE" ? "ALL" : "CORPORATE")}
          className={`cursor-pointer rounded-2xl border p-4 shadow-2xs flex flex-col justify-between transition ${
            categoryFilter === "CORPORATE"
              ? "bg-amber-50/70 border-amber-300 ring-2 ring-amber-400/40"
              : "bg-white border-stone-200/80 hover:border-amber-200"
          }`}
        >
          <span className="text-[11px] font-bold text-amber-800 uppercase tracking-wider">
            Corporate
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="text-2xl font-black text-amber-950">{stats.corporate}</span>
            <Building2 className="w-4 h-4 text-amber-600" />
          </div>
        </div>
      </div>

      {/* 1. TABS & CONTROLS BAR */}
      <div className="bg-white rounded-3xl border border-stone-200 shadow-2xs p-4 sm:p-5 space-y-4">
        {/* Row 1: Search Form */}
        <form onSubmit={handleSearchSubmit} className="relative">
          <Search className="w-4 h-4 text-stone-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search by name, email, mobile number, or college/organisation..."
            className="w-full pl-10 pr-24 py-2.5 rounded-xl border border-stone-200 text-xs sm:text-sm text-charcoal-900 placeholder-stone-400 bg-stone-50/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:border-transparent transition"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 px-3.5 py-1.5 rounded-lg bg-[#F5B817] hover:bg-[#E5A807] text-[#1F2421] text-xs font-bold transition"
          >
            Search
          </button>
        </form>

        {/* Row 2: Status Tabs + Filters & Sorting Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2 border-t border-stone-100">
          {/* 1. Status Tabs: All, Pending, Approved, Rejected */}
          <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none pb-1 sm:pb-0">
            {(["ALL", "PENDING", "APPROVED", "REJECTED"] as const).map((tab) => {
              const isActive = activeTab === tab;
              const count =
                tab === "ALL"
                  ? stats.totalVolunteers
                  : tab === "PENDING"
                  ? stats.pending
                  : tab === "APPROVED"
                  ? stats.approved
                  : stats.rejected;

              return (
                <button
                  key={tab}
                  type="button"
                  onClick={() => handleTabChange(tab)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap flex items-center gap-1.5 ${
                    isActive
                      ? "bg-charcoal-900 text-[#F5B817] shadow-xs"
                      : "bg-stone-100 text-charcoal-600 hover:bg-stone-200"
                  }`}
                >
                  <span>
                    {tab === "ALL"
                      ? "All Volunteers"
                      : tab.charAt(0) + tab.slice(1).toLowerCase()}
                  </span>
                  <span
                    className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                      isActive ? "bg-charcoal-800 text-amber-300" : "bg-stone-200 text-stone-600"
                    }`}
                  >
                    {count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Controls: Category Filter + Sorting */}
          <div className="flex items-center gap-2 self-end sm:self-auto">
            {/* Category Dropdown */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-charcoal-500 font-semibold hidden md:inline">Category:</span>
              <select
                value={categoryFilter}
                onChange={(e) => {
                  setCategoryFilter(e.target.value);
                  setPage(1);
                }}
                className="bg-stone-50 border border-stone-200 rounded-xl px-2.5 py-1.5 font-bold text-charcoal-800 text-xs focus:outline-none focus:ring-1 focus:ring-[#F5B817] cursor-pointer"
              >
                <option value="ALL">All Categories</option>
                <option value="STUDENT">Student</option>
                <option value="ALUMNI">Alumni</option>
                <option value="CORPORATE">Corporate</option>
              </select>
            </div>

            {/* Sorting Dropdown */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-charcoal-500 font-semibold hidden md:inline">Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as "NEWEST" | "OLDEST" | "NAME")}
                className="bg-stone-50 border border-stone-200 rounded-xl px-2.5 py-1.5 font-bold text-charcoal-800 text-xs focus:outline-none focus:ring-1 focus:ring-[#F5B817] cursor-pointer"
              >
                <option value="NEWEST">Newest First</option>
                <option value="OLDEST">Oldest First</option>
                <option value="NAME">Name (A-Z)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* 5. TABLE: Profile, Name, Mobile Number, Email, Category, Location, Action (View) */}
      <div className="bg-white rounded-3xl border border-stone-200 shadow-2xs overflow-hidden">
        {isLoading ? (
          <div className="py-24 flex flex-col items-center justify-center">
            <Loader2 className="w-8 h-8 text-[#F5B817] animate-spin" />
            <p className="text-xs sm:text-sm font-semibold text-charcoal-600 mt-3">
              Loading volunteers roster...
            </p>
          </div>
        ) : error ? (
          <div className="p-8 text-center">
            <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p className="text-sm font-bold text-charcoal-800">{error}</p>
            <button
              onClick={() => void fetchVolunteers()}
              className="mt-3 px-4 py-1.5 rounded-xl bg-stone-100 hover:bg-stone-200 text-xs font-bold text-charcoal-800 transition"
            >
              Retry
            </button>
          </div>
        ) : applications.length === 0 ? (
          <div className="py-24 text-center px-4">
            <Users className="w-10 h-10 text-stone-300 mx-auto mb-3" />
            <h3 className="text-sm font-bold text-charcoal-800">No volunteers found</h3>
            <p className="text-xs text-charcoal-500 mt-1 max-w-sm mx-auto">
              {searchQuery
                ? `No volunteers matching query "${searchQuery}". Try clearing search or filters.`
                : `No volunteers currently under the "${activeTab.toLowerCase()}" status.`}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-stone-50/80 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase tracking-wider">
                  <th scope="col" className="py-4 px-4 w-14 text-center">Profile</th>
                  <th scope="col" className="py-4 px-4">Name</th>
                  <th scope="col" className="py-4 px-4">Mobile Number</th>
                  <th scope="col" className="py-4 px-4">Email</th>
                  <th scope="col" className="py-4 px-4">Category</th>
                  <th scope="col" className="py-4 px-4">Location / Institute</th>
                  <th scope="col" className="py-4 px-4 text-center">Status</th>
                  <th scope="col" className="py-4 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100 text-xs">
                {applications.map((app) => {
                  const prof = app.volunteer_profile;
                  const fullName = `${prof.first_name} ${prof.last_name}`.trim();
                  const initials = `${prof.first_name?.[0] || ""}${prof.last_name?.[0] || ""}`.toUpperCase() || "VL";
                  const locationStr = getLocation(app);

                  return (
                    <tr
                      key={app.id}
                      className="hover:bg-amber-50/30 transition-colors group"
                    >
                      {/* 1. Profile Avatar */}
                      <td className="py-3.5 px-4 text-center">
                        <div className="w-9 h-9 rounded-full bg-[#FFF3D6] text-amber-900 font-bold flex items-center justify-center mx-auto text-xs border border-amber-200/80 shadow-2xs">
                          {initials}
                        </div>
                      </td>

                      {/* 2. Name */}
                      <td className="py-3.5 px-4 font-bold text-charcoal-900 text-sm">
                        <Link
                          href={`/admin/volunteers/${prof.id || app.id}`}
                          className="hover:text-[#D97706] transition-colors"
                        >
                          {fullName}
                        </Link>
                      </td>

                      {/* 3. Mobile Number */}
                      <td className="py-3.5 px-4 font-medium text-charcoal-700">
                        {prof.mobile_number || "—"}
                      </td>

                      {/* 4. Email */}
                      <td className="py-3.5 px-4 text-charcoal-600 font-medium">
                        {app.user_email || "—"}
                      </td>

                      {/* 5. Category */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider ${
                            prof.category === "STUDENT"
                              ? "bg-blue-50 text-blue-800 border border-blue-200"
                              : prof.category === "ALUMNI"
                              ? "bg-purple-50 text-purple-800 border border-purple-200"
                              : "bg-amber-50 text-amber-900 border border-amber-200"
                          }`}
                        >
                          {prof.category === "STUDENT" ? (
                            <GraduationCap className="w-3 h-3 text-blue-600" />
                          ) : prof.category === "ALUMNI" ? (
                            <Briefcase className="w-3 h-3 text-purple-600" />
                          ) : (
                            <Building2 className="w-3 h-3 text-amber-600" />
                          )}
                          {prof.category === "CORPORATE" ? "Corporate Panelist" : prof.category}
                        </span>
                      </td>

                      {/* 6. Location */}
                      <td className="py-3.5 px-4 text-charcoal-700 max-w-xs truncate" title={locationStr}>
                        {locationStr}
                      </td>

                      {/* Status Badge */}
                      <td className="py-3.5 px-4 text-center">
                        <span
                          className={`inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                            app.status === "APPROVED"
                              ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                              : app.status === "PENDING"
                              ? "bg-amber-50 text-amber-800 border border-amber-200"
                              : "bg-red-50 text-red-800 border border-red-200"
                          }`}
                        >
                          {app.status === "APPROVED" && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                          {app.status === "PENDING" && <Clock className="w-3 h-3 text-amber-600" />}
                          {app.status === "REJECTED" && <XCircle className="w-3 h-3 text-red-600" />}
                          {app.status}
                        </span>
                      </td>

                      {/* 7. Action: View + Quick Actions for Pending */}
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* Quick Decision for Pending items */}
                          {app.status === "PENDING" && (
                            <>
                              <button
                                type="button"
                                onClick={() => {
                                  setSelectedApp(app);
                                  setActionType("APPROVE");
                                }}
                                className="p-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 transition"
                                title="Approve volunteer"
                              >
                                <ThumbsUp className="w-3.5 h-3.5" />
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  setSelectedApp(app);
                                  setActionType("REJECT");
                                }}
                                className="p-1.5 rounded-lg bg-red-50 hover:bg-red-100 text-red-700 transition"
                                title="Reject application"
                              >
                                <ThumbsDown className="w-3.5 h-3.5" />
                              </button>
                            </>
                          )}

                          {/* Primary View Action Button */}
                          <Link
                            href={`/admin/volunteers/${prof.id || app.id}`}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-stone-100 hover:bg-[#F5B817] hover:text-[#1F2421] text-charcoal-800 font-bold text-xs transition shadow-2xs"
                          >
                            <Eye className="w-3.5 h-3.5" />
                            <span>View</span>
                          </Link>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-stone-200 bg-stone-50/60 flex items-center justify-between text-xs font-semibold text-charcoal-600">
            <div>
              Showing {((page - 1) * pageSize) + 1} to{" "}
              {Math.min(page * pageSize, totalCount)} of {totalCount} volunteers
            </div>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                className="p-1.5 rounded-lg bg-white border border-stone-200 hover:bg-stone-100 disabled:opacity-40 disabled:cursor-not-allowed transition"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="px-2 font-bold text-charcoal-800">
                Page {page} of {totalPages}
              </span>
              <button
                type="button"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                className="p-1.5 rounded-lg bg-white border border-stone-200 hover:bg-stone-100 disabled:opacity-40 disabled:cursor-not-allowed transition"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Decision Modal (Approve / Reject) */}
      {selectedApp && actionType && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-7 shadow-xl border border-stone-200 space-y-4 animate-in zoom-in-95 duration-200">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-bold text-charcoal-900">
                  {actionType === "APPROVE" ? "Approve Volunteer" : "Reject Application"}
                </h3>
                <p className="text-xs text-charcoal-500 mt-0.5">
                  Applicant:{" "}
                  <strong className="text-charcoal-800">
                    {selectedApp.volunteer_profile.first_name}{" "}
                    {selectedApp.volunteer_profile.last_name}
                  </strong>{" "}
                  ({selectedApp.user_email})
                </p>
              </div>
              <button
                onClick={() => {
                  setSelectedApp(null);
                  setActionType(null);
                }}
                className="p-1 rounded-lg text-charcoal-400 hover:text-charcoal-700 hover:bg-stone-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {decisionError && (
              <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{decisionError}</span>
              </div>
            )}

            {actionType === "APPROVE" ? (
              <div className="space-y-3">
                <p className="text-xs text-charcoal-600 leading-relaxed">
                  Approving this volunteer will activate their portal access, grant them eligibility to register for published events, and dispatch a welcome notification.
                </p>
                <div>
                  <label className="block text-xs font-semibold text-charcoal-700 mb-1">
                    Approval Notes (Optional)
                  </label>
                  <textarea
                    rows={3}
                    value={decisionNotes}
                    onChange={(e) => setDecisionNotes(e.target.value)}
                    placeholder="Enter any administrative review observations or notes..."
                    className="w-full p-3 rounded-xl border border-stone-200 text-xs text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-[#F5B817]"
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-xs text-charcoal-600 leading-relaxed">
                  Rejecting will decline this volunteer&apos;s onboarding application. A mandatory reason must be provided for audit traceability and applicant notification.
                </p>
                <div>
                  <label className="block text-xs font-semibold text-charcoal-700 mb-1">
                    Rejection Reason <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    rows={3}
                    required
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                    placeholder="Provide detailed justification for rejection..."
                    className="w-full p-3 rounded-xl border border-stone-200 text-xs text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-red-400"
                  />
                </div>
              </div>
            )}

            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-stone-100">
              <button
                type="button"
                onClick={() => {
                  setSelectedApp(null);
                  setActionType(null);
                }}
                disabled={isSubmittingDecision}
                className="px-4 py-2 rounded-xl text-xs font-bold text-charcoal-600 hover:bg-stone-100 transition"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => void handleDecisionSubmit()}
                disabled={isSubmittingDecision}
                className={`px-5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
                  actionType === "APPROVE"
                    ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                    : "bg-red-600 hover:bg-red-700 text-white"
                }`}
              >
                {isSubmittingDecision && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                <span>
                  {actionType === "APPROVE" ? "Confirm Approval" : "Confirm Rejection"}
                </span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AdminVolunteersPage() {
  return (
    <Suspense
      fallback={
        <div className="py-24 flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-[#F5B817] animate-spin" />
        </div>
      }
    >
      <VolunteersContent />
    </Suspense>
  );
}
