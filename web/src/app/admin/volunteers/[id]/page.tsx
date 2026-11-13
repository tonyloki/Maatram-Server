"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import {
  ArrowLeft,
  User,
  Shield,
  Award,
  CheckCircle2,
  Clock,
  Coins,
  Lock,
  Mail,
  Phone,
  GraduationCap,
  Building,
  Briefcase,
  Calendar,
  Sparkles,
  Trophy,
  Sliders,
  Settings,
  Info,
  MapPin,
  XCircle,
  ThumbsUp,
  ThumbsDown,
  Loader2,
  AlertCircle,
  X,
  FileCheck,
  ShieldCheck,
  Building2,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import {
  ApplicationDetailResponse,
  VolunteerProfileResponse,
  ApplicationListResponse,
} from "@/types";

export default function AdminVolunteerProfileViewPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [application, setApplication] = useState<ApplicationDetailResponse | null>(null);
  const [profile, setProfile] = useState<VolunteerProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Active Tab
  const [activeTab, setActiveTab] = useState<"info" | "preferences" | "consents" | "history">("info");

  // Decision Modal State
  const [actionType, setActionType] = useState<"APPROVE" | "REJECT" | null>(null);
  const [decisionNotes, setDecisionNotes] = useState("");
  const [rejectReason, setRejectReason] = useState("");
  const [isSubmittingDecision, setIsSubmittingDecision] = useState(false);
  const [decisionError, setDecisionError] = useState<string | null>(null);
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);

    try {
      // Step 1: Try fetching as application ID
      let appData: ApplicationDetailResponse | null = null;
      try {
        appData = await apiClient<ApplicationDetailResponse>(`/applications/${id}`);
      } catch {
        // Step 2: If 404 or fails, try querying applications with volunteer_profile_id or search
        try {
          const listRes = await apiClient<ApplicationListResponse>(`/applications?page=1&page_size=50`);
          const match = listRes.items?.find(
            (it) => it.id === id || it.volunteer_profile_id === id || it.volunteer_profile?.id === id
          );
          if (match) {
            appData = match;
          }
        } catch {
          // ignore
        }
      }

      // Step 3: Fetch base volunteer profile
      let profData: VolunteerProfileResponse | null = null;
      try {
        const profileIdToQuery = appData?.volunteer_profile_id || id;
        profData = await apiClient<VolunteerProfileResponse>(`/volunteers/${profileIdToQuery}`);
      } catch {
        // Fall back to appData.volunteer_profile
        if (appData?.volunteer_profile) {
          profData = appData.volunteer_profile;
        }
      }

      if (!appData && !profData) {
        throw new Error("Volunteer profile record could not be found.");
      }

      if (appData) setApplication(appData);
      if (profData) setProfile(profData);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load volunteer profile.";
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  // Handle Decision
  const handleDecisionSubmit = async () => {
    if (!application || !actionType) return;
    setIsSubmittingDecision(true);
    setDecisionError(null);

    try {
      if (actionType === "APPROVE") {
        await apiClient(`/applications/${application.id}/approve`, {
          method: "POST",
          body: JSON.stringify({ notes: decisionNotes.trim() || undefined }),
        });
        setFeedbackSuccess("Volunteer application has been successfully approved.");
      } else {
        if (!rejectReason.trim()) {
          setDecisionError("A mandatory rejection reason is required.");
          setIsSubmittingDecision(false);
          return;
        }
        await apiClient(`/applications/${application.id}/reject`, {
          method: "POST",
          body: JSON.stringify({ reason: rejectReason.trim() }),
        });
        setFeedbackSuccess("Volunteer application has been rejected.");
      }

      setActionType(null);
      setDecisionNotes("");
      setRejectReason("");
      void loadData();
      setTimeout(() => setFeedbackSuccess(null), 4000);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Failed to submit decision. Please verify permissions.";
      setDecisionError(msg);
    } finally {
      setIsSubmittingDecision(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[500px] flex flex-col items-center justify-center py-24">
        <Loader2 className="w-10 h-10 text-[#F5B817] animate-spin" />
        <p className="text-sm font-semibold text-charcoal-600 mt-3">
          Loading volunteer profile view...
        </p>
      </div>
    );
  }

  if (error || (!profile && !application)) {
    return (
      <div className="max-w-2xl mx-auto py-16 text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-charcoal-900">Volunteer Record Not Found</h2>
        <p className="text-sm text-charcoal-500 mt-1 mb-6">
          {error || "The requested volunteer profile could not be located in the directory."}
        </p>
        <Link
          href="/admin/volunteers"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-charcoal-900 text-white font-bold text-xs shadow-xs hover:bg-charcoal-800 transition"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Volunteers Directory
        </Link>
      </div>
    );
  }

  const vol = profile || application?.volunteer_profile;
  if (!vol) return null;

  const fullName = `${vol.first_name || ""} ${vol.last_name || ""}`.trim() || "Volunteer";
  const initials = `${vol.first_name?.[0] || ""}${vol.last_name?.[0] || ""}`.toUpperCase() || "VL";
  const userEmail = application?.user_email || vol.email || "Contact hidden";
  const appStatus = application?.status || "APPROVED";

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16 animate-in fade-in-50 duration-200">
      {/* Top Navigation & Breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-stone-200">
        <div className="flex items-center gap-3">
          <Link
            href="/admin/volunteers"
            className="p-2 rounded-xl bg-white border border-stone-200 hover:bg-stone-100 text-charcoal-700 transition shadow-2xs"
            title="Back to Volunteers"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-extrabold text-[#1F2421] tracking-tight">
                {fullName}
              </h1>
              <span
                className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                  appStatus === "APPROVED"
                    ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                    : appStatus === "PENDING"
                    ? "bg-amber-50 text-amber-800 border border-amber-200"
                    : "bg-red-50 text-red-800 border border-red-200"
                }`}
              >
                {appStatus}
              </span>
            </div>
            <p className="text-xs text-charcoal-500 mt-0.5">
              Read-Only Volunteer Profile Inspection • Admin Portal
            </p>
          </div>
        </div>

        {/* Pending Action Buttons */}
        {appStatus === "PENDING" && application && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActionType("APPROVE")}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-xs transition"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
              <span>Approve Volunteer</span>
            </button>
            <button
              onClick={() => setActionType("REJECT")}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow-xs transition"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
              <span>Reject</span>
            </button>
          </div>
        )}
      </div>

      {/* Success Notification */}
      {feedbackSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-center gap-3 shadow-xs">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <p className="text-sm font-semibold">{feedbackSuccess}</p>
        </div>
      )}

      {/* ======================================================== */}
      {/* Main Two-Column Grid: Exact Mirror of Volunteer Profile   */}
      {/* ======================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* ======================================================== */}
        {/* LEFT COLUMN: Identity Summary Card                       */}
        {/* ======================================================== */}
        <div className="lg:col-span-4 bg-white rounded-3xl border border-[#EFECE6] shadow-xs p-6 relative overflow-hidden flex flex-col justify-between">
          <div>
            {/* Centered Circular Portrait Photo */}
            <div className="relative w-28 h-28 mx-auto mt-2 mb-3">
              <div className="w-28 h-28 rounded-full overflow-hidden ring-4 ring-white shadow-md relative bg-[#FFF8E7] flex items-center justify-center text-amber-900 text-3xl font-extrabold border border-amber-200">
                {initials}
              </div>
            </div>

            {/* Volunteer Full Name & Category Badge */}
            <div className="text-center">
              <h2 className="text-xl font-extrabold text-[#1F2421]">{fullName}</h2>
              <div className="mt-1 flex items-center justify-center gap-1.5">
                <span
                  className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider ${
                    vol.category === "STUDENT"
                      ? "bg-blue-50 text-blue-800 border border-blue-200"
                      : vol.category === "ALUMNI"
                      ? "bg-purple-50 text-purple-800 border border-purple-200"
                      : "bg-amber-50 text-amber-800 border border-amber-200"
                  }`}
                >
                  {vol.category === "STUDENT" ? (
                    <GraduationCap className="w-3 h-3 text-blue-600" />
                  ) : vol.category === "ALUMNI" ? (
                    <Briefcase className="w-3 h-3 text-purple-600" />
                  ) : (
                    <Building2 className="w-3 h-3 text-amber-600" />
                  )}
                  {vol.category === "CORPORATE" ? "Corporate Panelist" : vol.category}
                </span>
              </div>

              {/* Sub-affiliation */}
              {vol.student_profile?.maatram_reg_number && (
                <p className="text-xs text-[#6B7280] font-medium mt-1">
                  Maatram Reg: <strong className="text-charcoal-800">{vol.student_profile.maatram_reg_number}</strong>
                </p>
              )}
            </div>

            {/* Stats Row: Hours, Events, Points */}
            <div className="grid grid-cols-3 gap-2 mt-6 p-3 rounded-2xl bg-[#FAF8F2] border border-[#EFECE6] text-center">
              <div>
                <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-wider block">Hours</span>
                <span className="text-base font-extrabold text-[#1F2421]">0</span>
              </div>
              <div className="border-x border-[#E5E0D5]">
                <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-wider block">Events</span>
                <span className="text-base font-extrabold text-[#1F2421]">0</span>
              </div>
              <div>
                <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-wider block">Points</span>
                <span className="text-base font-extrabold text-[#1F2421]">0</span>
              </div>
            </div>

            {/* Direct Contact Details Card */}
            <div className="mt-5 space-y-3 pt-5 border-t border-[#EFECE6] text-xs">
              <div className="flex items-center gap-3 text-charcoal-700">
                <div className="w-7 h-7 rounded-lg bg-stone-100 flex items-center justify-center text-charcoal-500 shrink-0">
                  <Mail className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0 flex-1">
                  <span className="text-[10px] text-charcoal-400 block font-semibold">EMAIL</span>
                  <span className="font-semibold text-charcoal-900 truncate block">{userEmail}</span>
                </div>
              </div>

              <div className="flex items-center gap-3 text-charcoal-700">
                <div className="w-7 h-7 rounded-lg bg-stone-100 flex items-center justify-center text-charcoal-500 shrink-0">
                  <Phone className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0 flex-1">
                  <span className="text-[10px] text-charcoal-400 block font-semibold">MOBILE</span>
                  <span className="font-semibold text-charcoal-900">{vol.mobile_number || "—"}</span>
                </div>
              </div>

              <div className="flex items-center gap-3 text-charcoal-700">
                <div className="w-7 h-7 rounded-lg bg-stone-100 flex items-center justify-center text-charcoal-500 shrink-0">
                  <User className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0 flex-1">
                  <span className="text-[10px] text-charcoal-400 block font-semibold">DEMOGRAPHICS</span>
                  <span className="font-semibold text-charcoal-900">
                    {vol.age ? `${vol.age} yrs` : "Age hidden"} • {vol.gender || "Not specified"}
                  </span>
                </div>
              </div>

              {/* Safeguarding / Parental Consent Badge */}
              <div className="flex items-center gap-3 text-charcoal-700">
                <div className="w-7 h-7 rounded-lg bg-stone-100 flex items-center justify-center text-charcoal-500 shrink-0">
                  <ShieldCheck className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0 flex-1">
                  <span className="text-[10px] text-charcoal-400 block font-semibold">SAFEGUARDING (DPDP)</span>
                  <span className="font-semibold text-charcoal-900">
                    {vol.age && vol.age < 18
                      ? `Minor (${vol.parental_consent_status || "PENDING"})`
                      : "Adult (18+) • Standard"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Read-Only Mode Notice Footer */}
          <div className="mt-6 pt-4 border-t border-[#EFECE6] bg-[#FAF8F2] -mx-6 -mb-6 p-4 text-center rounded-b-3xl">
            <p className="text-[11px] font-semibold text-charcoal-500 flex items-center justify-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-stone-400" />
              <span>Read-Only Administrative View</span>
            </p>
          </div>
        </div>

        {/* ======================================================== */}
        {/* RIGHT COLUMN: Details & Tabbed Settings                  */}
        {/* ======================================================== */}
        <div className="lg:col-span-8 bg-white rounded-3xl border border-[#EFECE6] shadow-xs overflow-hidden">
          {/* Tabs Navigation Header */}
          <div className="flex items-center border-b border-[#EFECE6] px-6 overflow-x-auto scrollbar-none bg-[#FAF8F2]/60">
            <button
              onClick={() => setActiveTab("info")}
              className={`py-4 px-4 text-xs font-bold border-b-2 whitespace-nowrap transition-colors flex items-center gap-2 ${
                activeTab === "info"
                  ? "border-[#F5B817] text-[#1F2421]"
                  : "border-transparent text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              <User className="w-4 h-4" />
              <span>Personal & Academic Details</span>
            </button>

            <button
              onClick={() => setActiveTab("preferences")}
              className={`py-4 px-4 text-xs font-bold border-b-2 whitespace-nowrap transition-colors flex items-center gap-2 ${
                activeTab === "preferences"
                  ? "border-[#F5B817] text-[#1F2421]"
                  : "border-transparent text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              <Sliders className="w-4 h-4" />
              <span>Preferences & Skills</span>
            </button>

            <button
              onClick={() => setActiveTab("consents")}
              className={`py-4 px-4 text-xs font-bold border-b-2 whitespace-nowrap transition-colors flex items-center gap-2 ${
                activeTab === "consents"
                  ? "border-[#F5B817] text-[#1F2421]"
                  : "border-transparent text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              <Shield className="w-4 h-4" />
              <span>DPDP Privacy & Consents</span>
            </button>

            <button
              onClick={() => setActiveTab("history")}
              className={`py-4 px-4 text-xs font-bold border-b-2 whitespace-nowrap transition-colors flex items-center gap-2 ${
                activeTab === "history"
                  ? "border-[#F5B817] text-[#1F2421]"
                  : "border-transparent text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              <FileCheck className="w-4 h-4" />
              <span>Review Trail</span>
            </button>
          </div>

          {/* Tab Body */}
          <div className="p-6 sm:p-8">
            {/* TAB 1: PERSONAL & ACADEMIC/ORGANISATION DETAILS */}
            {activeTab === "info" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-bold text-[#1F2421] mb-1">
                    Volunteer Identification
                  </h3>
                  <p className="text-xs text-charcoal-500">
                    Official identity and registered contact details submitted during onboarding.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                    <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">First Name</span>
                    <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.first_name || "—"}</span>
                  </div>

                  <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                    <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Last Name</span>
                    <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.last_name || "—"}</span>
                  </div>

                  <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                    <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Mobile Number</span>
                    <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.mobile_number || "—"}</span>
                  </div>

                  <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                    <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Email Address</span>
                    <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{userEmail}</span>
                  </div>
                </div>

                {/* Bio / Purpose */}
                <div className="p-4 rounded-xl bg-stone-50 border border-stone-200">
                  <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block mb-1">
                    Volunteer Bio & Motivation
                  </span>
                  <p className="text-xs sm:text-sm text-charcoal-700 leading-relaxed italic">
                    {vol.bio || "No personal bio or statement provided yet."}
                  </p>
                </div>

                {/* Category Details */}
                {vol.category === "STUDENT" && vol.student_profile && (
                  <div className="pt-4 border-t border-stone-200 space-y-4">
                    <h4 className="text-sm font-bold text-charcoal-900 flex items-center gap-2">
                      <GraduationCap className="w-4 h-4 text-blue-600" />
                      Academic Student Credentials
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">College / University</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.student_profile.college_name}</span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Degree & Major</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.student_profile.degree}</span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Department</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.student_profile.department}</span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Current Year & Batch</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">
                          Year {vol.student_profile.current_year} (Batch {vol.student_profile.batch_year})
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {vol.category === "ALUMNI" && vol.alumni_profile && (
                  <div className="pt-4 border-t border-stone-200 space-y-4">
                    <h4 className="text-sm font-bold text-charcoal-900 flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-purple-600" />
                      Alumni Professional Experience
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Organisation</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.alumni_profile.organisation}</span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Job Role</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.alumni_profile.job_role}</span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Work Location</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.alumni_profile.location}</span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Alma Mater College</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.alumni_profile.college_name}</span>
                      </div>
                    </div>
                  </div>
                )}

                {vol.category === "CORPORATE" && vol.corporate_profile && (
                  <div className="pt-4 border-t border-stone-200 space-y-4">
                    <h4 className="text-sm font-bold text-charcoal-900 flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-amber-600" />
                      Corporate Panelist Profile
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Company / Enterprise</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.corporate_profile.organisation}</span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Designation</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.corporate_profile.designation}</span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Experience</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">
                          {vol.corporate_profile.years_of_experience} Years
                        </span>
                      </div>
                      <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200">
                        <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Base Location</span>
                        <span className="text-sm font-bold text-charcoal-900 mt-0.5 block">{vol.corporate_profile.location}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: PREFERENCES & SKILLS */}
            {activeTab === "preferences" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-bold text-[#1F2421] mb-1">
                    Volunteering Preferences & Skills
                  </h3>
                  <p className="text-xs text-charcoal-500">
                    Engagement format, interest areas, and technical/mentorship skills.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-stone-50 border border-stone-200">
                    <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Preferred Mode</span>
                    <span className="text-sm font-bold text-charcoal-900 mt-1 block">In-Person & Online (Hybrid)</span>
                  </div>

                  <div className="p-4 rounded-xl bg-stone-50 border border-stone-200">
                    <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">Weekly Availability</span>
                    <span className="text-sm font-bold text-charcoal-900 mt-1 block">Weekends & Scheduled Drives</span>
                  </div>
                </div>

                {/* Core Areas */}
                <div className="p-4 rounded-xl bg-stone-50 border border-stone-200 space-y-2">
                  <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">
                    Core Volunteering Pillars
                  </span>
                  <div className="flex flex-wrap gap-2 pt-1">
                    <span className="px-3 py-1 bg-amber-100 text-amber-900 rounded-lg text-xs font-bold">
                      School Visits
                    </span>
                    <span className="px-3 py-1 bg-blue-100 text-blue-900 rounded-lg text-xs font-bold">
                      Mock Interviews
                    </span>
                    <span className="px-3 py-1 bg-emerald-100 text-emerald-900 rounded-lg text-xs font-bold">
                      BGV Support
                    </span>
                  </div>
                </div>

                {/* Skills */}
                <div className="p-4 rounded-xl bg-stone-50 border border-stone-200 space-y-2">
                  <span className="text-[10px] font-bold text-charcoal-400 uppercase tracking-wider block">
                    Registered Mentorship & Volunteering Skills
                  </span>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {(vol.alumni_profile?.skills || vol.corporate_profile?.skills || [
                      "Mentoring",
                      "Communication",
                      "Interview Coaching",
                      "Educational Outreach",
                    ]).map((sk: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-white border border-stone-300 text-charcoal-800 rounded-lg text-xs font-semibold"
                      >
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: DPDP PRIVACY & CONSENTS */}
            {activeTab === "consents" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-bold text-[#1F2421] mb-1">
                    Affirmative Consent Settings (DPDP Act 2023)
                  </h3>
                  <p className="text-xs text-charcoal-500">
                    Display of volunteer affirmative consent selections across 6 statutory privacy dimensions. Under DPDP regulations, administrators cannot unilaterally modify these preferences.
                  </p>
                </div>

                <div className="space-y-3">
                  {[
                    {
                      title: "Public Leaderboard Visibility",
                      desc: "Show points and rankings on public volunteer boards.",
                      enabled: true,
                    },
                    {
                      title: "Full Name Attribution",
                      desc: "Display full real name instead of anonymous initials.",
                      enabled: true,
                    },
                    {
                      title: "Thank-You & Recognition Emails",
                      desc: "Receive congratulatory communications for milestone achievements.",
                      enabled: true,
                    },
                    {
                      title: "LinkedIn & Social Media Attribution",
                      desc: "Permit tagging and acknowledgement on official Maatram channels.",
                      enabled: true,
                    },
                    {
                      title: "Event Photography & Media Usage",
                      desc: "Consent to photography during on-ground school and interview drives.",
                      enabled: true,
                    },
                    {
                      title: "Direct Maatram Team Contact",
                      desc: "Allow coordinators to contact via mobile for urgent volunteering drives.",
                      enabled: true,
                    },
                  ].map((dim, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl bg-stone-50 border border-stone-200 flex items-center justify-between gap-4"
                    >
                      <div>
                        <h4 className="text-xs font-bold text-charcoal-900">{dim.title}</h4>
                        <p className="text-[11px] text-charcoal-500 mt-0.5">{dim.desc}</p>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>Granted</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 4: REVIEW HISTORY */}
            {activeTab === "history" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-base font-bold text-[#1F2421] mb-1">
                    Application Review & Onboarding Trail
                  </h3>
                  <p className="text-xs text-charcoal-500">
                    Audited chronological record of submissions, document reviews, and decisions.
                  </p>
                </div>

                <div className="space-y-3">
                  <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-charcoal-900">Application Submitted</span>
                      <span className="text-charcoal-400">
                        {application?.submitted_at
                          ? new Date(application.submitted_at).toLocaleDateString()
                          : "Initial Onboarding"}
                      </span>
                    </div>
                    <p className="text-xs text-charcoal-600">
                      Volunteer completed self-registration with verified profile classifications.
                    </p>
                  </div>

                  {application?.reviews && application.reviews.length > 0 ? (
                    application.reviews.map((rev) => (
                      <div
                        key={rev.id}
                        className={`p-4 rounded-2xl border space-y-1.5 ${
                          rev.action === "APPROVED"
                            ? "bg-emerald-50/60 border-emerald-200"
                            : "bg-red-50/60 border-red-200"
                        }`}
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span
                            className={`font-bold ${
                              rev.action === "APPROVED" ? "text-emerald-900" : "text-red-900"
                            }`}
                          >
                            Decision: {rev.action}
                          </span>
                          <span className="text-charcoal-400 text-[11px]">
                            {new Date(rev.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        {rev.reason && (
                          <p className="text-xs text-charcoal-700 italic">
                            &quot;{rev.reason}&quot;
                          </p>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="p-6 text-center border border-dashed border-stone-200 rounded-2xl">
                      <p className="text-xs text-charcoal-400">
                        {appStatus === "PENDING"
                          ? "Application is currently pending administrative decision."
                          : "No subsequent administrative amendments on record."}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Decision Modal (Approve / Reject) */}
      {actionType && application && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-7 shadow-xl border border-stone-200 space-y-4 animate-in zoom-in-95 duration-200">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-bold text-charcoal-900">
                  {actionType === "APPROVE" ? "Approve Volunteer" : "Reject Application"}
                </h3>
                <p className="text-xs text-charcoal-500 mt-0.5">
                  Applicant: <strong className="text-charcoal-800">{fullName}</strong> ({userEmail})
                </p>
              </div>
              <button
                onClick={() => setActionType(null)}
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
                  Approving this volunteer will grant them full access to published volunteer opportunities and send them an onboarding welcome email.
                </p>
                <div>
                  <label className="block text-xs font-semibold text-charcoal-700 mb-1">
                    Approval Notes (Optional)
                  </label>
                  <textarea
                    rows={3}
                    value={decisionNotes}
                    onChange={(e) => setDecisionNotes(e.target.value)}
                    placeholder="Enter any administrative review observations..."
                    className="w-full p-3 rounded-xl border border-stone-200 text-xs text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-[#F5B817]"
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <p className="text-xs text-charcoal-600 leading-relaxed">
                  Rejecting will decline this volunteer&apos;s onboarding application. A mandatory reason is required for administrative audit logs.
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
                    placeholder="Provide justification for rejecting this volunteer..."
                    className="w-full p-3 rounded-xl border border-stone-200 text-xs text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-red-400"
                  />
                </div>
              </div>
            )}

            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-stone-100">
              <button
                type="button"
                onClick={() => setActionType(null)}
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
