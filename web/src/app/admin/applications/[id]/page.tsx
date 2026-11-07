"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  ShieldCheck,
  User,
  GraduationCap,
  Briefcase,
  Calendar,
  Phone,
  Mail,
  MapPin,
  FileText,
  History,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { ApplicationDetailResponse } from "@/types";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function ApplicationDetailPage({ params }: PageProps) {
  const { id } = use(params);

  const [application, setApplication] = useState<ApplicationDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Action modals state
  const [approveModalOpen, setApproveModalOpen] = useState(false);
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [consentModalOpen, setConsentModalOpen] = useState(false);

  const [approveNotes, setApproveNotes] = useState("");
  const [rejectReason, setRejectReason] = useState("");
  const [consentStatus, setConsentStatus] = useState<"VERIFIED" | "REJECTED">("VERIFIED");
  const [consentNotes, setConsentNotes] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const fetchApplication = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.get<ApplicationDetailResponse>(`/applications/${id}`);
      setApplication(res.data);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setError(e.message || "Failed to load application details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplication();
  }, [id]);

  const handleApprove = async () => {
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient.post(`/applications/${id}/approve`, {
        notes: approveNotes.trim() ? approveNotes : undefined,
      });
      setApproveModalOpen(false);
      await fetchApplication();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to approve application.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (rejectReason.trim().length < 3) {
      setActionError("Please provide an explicit rejection reason (at least 3 characters).");
      return;
    }
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient.post(`/applications/${id}/reject`, {
        reason: rejectReason.trim(),
      });
      setRejectModalOpen(false);
      await fetchApplication();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to reject application.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleVerifyConsent = async () => {
    try {
      setActionLoading(true);
      setActionError(null);
      await apiClient.post(`/applications/${id}/verify-parental-consent`, {
        status: consentStatus,
        notes: consentNotes.trim() ? consentNotes : undefined,
      });
      setConsentModalOpen(false);
      await fetchApplication();
    } catch (err: unknown) {
      const e = err as { message?: string };
      setActionError(e.message || "Failed to update parental consent verification.");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-10 h-10 border-4 border-[#F5B817] border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-medium text-charcoal-500">Loading application dossier...</p>
      </div>
    );
  }

  if (error || !application) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 text-center">
        <div className="w-14 h-14 bg-red-50 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertTriangle className="w-7 h-7" />
        </div>
        <h2 className="text-xl font-bold text-charcoal-900 mb-2">Application Not Found</h2>
        <p className="text-charcoal-600 mb-6">{error || "Could not retrieve the requested application."}</p>
        <Link
          href="/admin/applications"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#F5B817] text-[#1F2421] font-semibold rounded-lg hover:bg-[#E5A800]"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Applications
        </Link>
      </div>
    );
  }

  const profile = application.volunteer_profile;
  const isPending = application.status === "PENDING";
  const isMinor = profile?.is_minor;
  const consentStatusBadge = profile?.parental_consent_status;

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-16">
      {/* Back button & Header */}
      <div>
        <Link
          href="/admin/applications"
          className="inline-flex items-center gap-2 text-sm font-medium text-charcoal-600 hover:text-charcoal-900 transition mb-3"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Applications List
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight">
                {profile?.first_name} {profile?.last_name}
              </h1>
              <span
                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase ${
                  application.status === "APPROVED"
                    ? "bg-emerald-100 text-emerald-800"
                    : application.status === "REJECTED"
                    ? "bg-red-100 text-red-800"
                    : "bg-amber-100 text-amber-900"
                }`}
              >
                {application.status}
              </span>
            </div>
            <p className="text-sm text-charcoal-500 mt-1">
              Application ID: <span className="font-mono text-xs">{application.id}</span> • Submitted on{" "}
              {new Date(application.submitted_at).toLocaleDateString("en-IN", {
                day: "numeric",
                month: "short",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          </div>

          {/* Action buttons if Pending */}
          {isPending && (
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => {
                  setActionError(null);
                  setRejectReason("");
                  setRejectModalOpen(true);
                }}
                className="px-4 py-2 border border-red-200 text-red-600 hover:bg-red-50 rounded-lg text-sm font-semibold transition flex items-center gap-2"
              >
                <XCircle className="w-4 h-4" />
                Reject
              </button>
              <button
                type="button"
                onClick={() => {
                  setActionError(null);
                  setApproveNotes("");
                  setApproveModalOpen(true);
                }}
                className="px-5 py-2 bg-[#F5B817] hover:bg-[#E5A800] text-[#1F2421] rounded-lg text-sm font-bold shadow-sm transition flex items-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4" />
                Approve Volunteer
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Minor Safeguarding Notice */}
      {isMinor && (
        <div className="bg-amber-50/80 border border-amber-300 rounded-xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-800 shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-amber-900">
                Minor Safeguarding Policy — Age &lt; 18
              </h4>
              <p className="text-xs text-amber-800 mt-0.5">
                This applicant was born on {profile?.date_of_birth} and is classified as a minor. In accordance with
                Maatram child safeguarding rules, administrative verification of written parental/guardian consent is
                mandatory before onboarding.
              </p>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-xs font-semibold text-amber-900">Current Consent Status:</span>
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold ${
                    consentStatusBadge === "VERIFIED"
                      ? "bg-emerald-100 text-emerald-800"
                      : consentStatusBadge === "REJECTED"
                      ? "bg-red-100 text-red-800"
                      : "bg-amber-200 text-amber-900"
                  }`}
                >
                  {consentStatusBadge || "PENDING"}
                </span>
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={() => {
              setActionError(null);
              setConsentStatus(consentStatusBadge === "VERIFIED" ? "VERIFIED" : "VERIFIED");
              setConsentNotes("");
              setConsentModalOpen(true);
            }}
            className="px-4 py-2 bg-charcoal-900 text-white rounded-lg text-xs font-semibold hover:bg-charcoal-800 transition shrink-0"
          >
            Update Consent Status
          </button>
        </div>
      )}

      {/* Main Grid: Details & Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Profile & Categories */}
        <div className="lg:col-span-2 space-y-6">
          {/* Personal & Contact Information */}
          <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs">
            <div className="flex items-center gap-2 border-b border-stone-100 pb-3 mb-4">
              <User className="w-4 h-4 text-amber-600" />
              <h3 className="text-base font-bold text-charcoal-900">Personal & Contact Dossier</h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Email Address</span>
                <p className="font-semibold text-charcoal-900 flex items-center gap-1.5 mt-0.5">
                  <Mail className="w-3.5 h-3.5 text-stone-400" />
                  {application.user_email || "N/A"}
                </p>
              </div>
              <div>
                <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Mobile Number</span>
                <p className="font-semibold text-charcoal-900 flex items-center gap-1.5 mt-0.5">
                  <Phone className="w-3.5 h-3.5 text-stone-400" />
                  {profile?.mobile_number || "N/A"}
                </p>
              </div>
              <div>
                <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Date of Birth</span>
                <p className="font-semibold text-charcoal-900 flex items-center gap-1.5 mt-0.5">
                  <Calendar className="w-3.5 h-3.5 text-stone-400" />
                  {profile?.date_of_birth || "N/A"}
                </p>
              </div>
              <div>
                <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Gender</span>
                <p className="font-semibold text-charcoal-900 mt-0.5 capitalize">{profile?.gender || "Not specified"}</p>
              </div>
              <div className="sm:col-span-2">
                <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Residential Address</span>
                <p className="font-medium text-charcoal-800 flex items-start gap-1.5 mt-0.5">
                  <MapPin className="w-3.5 h-3.5 text-stone-400 mt-0.5 shrink-0" />
                  {profile?.address_line1 ? (
                    <>
                      {profile.address_line1}
                      {profile.address_line2 ? `, ${profile.address_line2}` : ""}
                      {profile.city ? `, ${profile.city}` : ""}
                      {profile.state ? `, ${profile.state}` : ""}
                      {profile.pincode ? ` - ${profile.pincode}` : ""}
                    </>
                  ) : (
                    "No address recorded"
                  )}
                </p>
              </div>
              {profile?.emergency_contact_name && (
                <div className="sm:col-span-2 pt-2 border-t border-stone-100">
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">
                    Emergency Contact
                  </span>
                  <p className="text-sm font-semibold text-charcoal-900 mt-0.5">
                    {profile.emergency_contact_name} ({profile.emergency_contact_relationship || "Relation"}) —{" "}
                    {profile.emergency_contact_phone}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Category Affiliation */}
          <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs">
            <div className="flex items-center gap-2 border-b border-stone-100 pb-3 mb-4">
              {profile?.category === "STUDENT" ? (
                <GraduationCap className="w-4 h-4 text-amber-600" />
              ) : (
                <Briefcase className="w-4 h-4 text-amber-600" />
              )}
              <h3 className="text-base font-bold text-charcoal-900">
                Volunteer Category: <span className="text-amber-700">{profile?.category}</span>
              </h3>
            </div>

            {profile?.category === "STUDENT" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">College / University</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5">{profile?.college_name || "N/A"}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Department / Degree</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5">{profile?.department || "N/A"}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Expected Graduation</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5">{profile?.graduation_year || "N/A"}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Student ID / Roll No.</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5 font-mono">{profile?.student_id || "N/A"}</p>
                </div>
              </div>
            )}

            {profile?.category === "ALUMNI" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Alma Mater</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5">{profile?.college_name || "N/A"}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Graduation Batch</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5">{profile?.graduation_year || "N/A"}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Current Employer</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5">{profile?.employer_name || "N/A"}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Designation / Role</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5">{profile?.job_title || "N/A"}</p>
                </div>
              </div>
            )}

            {profile?.category === "CORPORATE" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Corporate Employer</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5">{profile?.employer_name || "N/A"}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Designation / Role</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5">{profile?.job_title || "N/A"}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Industry Domain</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5">{profile?.industry || "N/A"}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Corporate ID</span>
                  <p className="font-semibold text-charcoal-900 mt-0.5 font-mono">{profile?.corporate_id || "N/A"}</p>
                </div>
              </div>
            )}
          </div>

          {/* Skills & Background Note */}
          <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs">
            <div className="flex items-center gap-2 border-b border-stone-100 pb-3 mb-4">
              <FileText className="w-4 h-4 text-amber-600" />
              <h3 className="text-base font-bold text-charcoal-900">Interests & Volunteer Background</h3>
            </div>
            <div className="space-y-4">
              <div>
                <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Skills / Interests</span>
                <div className="flex flex-wrap gap-1.5 mt-1.5">
                  {profile?.skills && profile.skills.length > 0 ? (
                    profile.skills.map((skill, idx) => (
                      <span key={idx} className="px-2.5 py-1 bg-amber-50 text-amber-800 text-xs font-medium rounded-md">
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-charcoal-400 italic">No skills entered</span>
                  )}
                </div>
              </div>
              {profile?.bio && (
                <div>
                  <span className="text-xs font-medium text-charcoal-500 uppercase tracking-wider">Motivation / Bio</span>
                  <p className="text-sm text-charcoal-700 bg-stone-50 p-3 rounded-lg mt-1 border border-stone-100">
                    {profile.bio}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right 1 Col: Audit & Review History */}
        <div className="space-y-6">
          {/* Status Card */}
          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs">
            <h4 className="text-xs font-bold text-charcoal-400 uppercase tracking-wider mb-3">Review Decision Status</h4>
            <div className="flex items-center gap-3">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                  application.status === "APPROVED"
                    ? "bg-emerald-100 text-emerald-700"
                    : application.status === "REJECTED"
                    ? "bg-red-100 text-red-700"
                    : "bg-amber-100 text-amber-700"
                }`}
              >
                {application.status === "APPROVED" ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : application.status === "REJECTED" ? (
                  <XCircle className="w-5 h-5" />
                ) : (
                  <Clock className="w-5 h-5" />
                )}
              </div>
              <div>
                <div className="font-bold text-charcoal-900">{application.status}</div>
                <div className="text-xs text-charcoal-500">
                  {application.status === "PENDING"
                    ? "Awaiting admin committee review"
                    : `Processed on ${new Date(application.updated_at).toLocaleDateString("en-IN")}`}
                </div>
              </div>
            </div>

            {application.notes && (
              <div className="mt-4 pt-3 border-t border-stone-100 text-xs text-charcoal-600">
                <span className="font-semibold text-charcoal-700">Review Notes:</span>
                <p className="mt-0.5 bg-stone-50 p-2 rounded">{application.notes}</p>
              </div>
            )}
          </div>

          {/* Review Trail */}
          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs">
            <div className="flex items-center gap-2 border-b border-stone-100 pb-3 mb-4">
              <History className="w-4 h-4 text-amber-600" />
              <h4 className="text-sm font-bold text-charcoal-900">Audit & Review Trail</h4>
            </div>

            {application.reviews && application.reviews.length > 0 ? (
              <div className="space-y-4">
                {application.reviews.map((rev) => (
                  <div key={rev.id} className="relative pl-4 border-l-2 border-amber-300 pb-1 text-xs">
                    <div className="font-semibold text-charcoal-900 capitalize">
                      {rev.action.toLowerCase().replace("_", " ")}
                    </div>
                    <div className="text-charcoal-500 text-[11px]">
                      {new Date(rev.created_at).toLocaleString("en-IN")}
                    </div>
                    {rev.notes && <p className="text-charcoal-700 mt-1 bg-stone-50 p-1.5 rounded">{rev.notes}</p>}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-charcoal-400 italic">No previous reviews logged for this dossier.</p>
            )}
          </div>
        </div>
      </div>

      {/* APPROVE MODAL */}
      {approveModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-stone-200">
            <h3 className="text-lg font-bold text-charcoal-900 mb-2">Approve Volunteer Application</h3>
            <p className="text-xs text-charcoal-600 mb-4">
              Approving will activate <strong>{profile?.first_name} {profile?.last_name}</strong> as an active volunteer.
              They will receive their activation email and can begin subscribing to upcoming events.
            </p>
            {actionError && (
              <div className="p-3 mb-4 rounded-lg bg-red-50 text-red-700 text-xs border border-red-200">
                {actionError}
              </div>
            )}
            <div className="mb-4">
              <label className="block text-xs font-semibold text-charcoal-700 mb-1">
                Approval Notes (Optional):
              </label>
              <textarea
                value={approveNotes}
                onChange={(e) => setApproveNotes(e.target.value)}
                placeholder="e.g., Interview completed; assigned to Chennai School Visit mentor team"
                rows={3}
                className="w-full text-xs p-2.5 rounded-lg border border-stone-300 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
              />
            </div>
            <div className="flex items-center justify-end gap-3">
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => setApproveModalOpen(false)}
                className="px-4 py-2 border border-stone-300 text-charcoal-700 text-xs font-semibold rounded-lg hover:bg-stone-50"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={actionLoading}
                onClick={handleApprove}
                className="px-5 py-2 bg-[#F5B817] hover:bg-[#E5A800] text-[#1F2421] font-bold text-xs rounded-lg transition"
              >
                {actionLoading ? "Approving..." : "Confirm Approval"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* REJECT MODAL */}
      {rejectModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-stone-200">
            <h3 className="text-lg font-bold text-charcoal-900 mb-2">Reject Volunteer Application</h3>
            <p className="text-xs text-charcoal-600 mb-4">
              Per Maatram governance rules, an explicit reason must be logged for record-keeping and volunteer notification.
            </p>
            {actionError && (
              <div className="p-3 mb-4 rounded-lg bg-red-50 text-red-700 text-xs border border-red-200">
                {actionError}
              </div>
            )}
            <div className="mb-4">
              <label className="block text-xs font-semibold text-charcoal-700 mb-1">
                Rejection Reason (Mandatory):
              </label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="e.g., Incomplete institutional affiliation / outside operating location"
                rows={3}
                className="w-full text-xs p-2.5 rounded-lg border border-stone-300 focus:outline-hidden focus:ring-2 focus:ring-red-500"
              />
            </div>
            <div className="flex items-center justify-end gap-3">
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => setRejectModalOpen(false)}
                className="px-4 py-2 border border-stone-300 text-charcoal-700 text-xs font-semibold rounded-lg hover:bg-stone-50"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={actionLoading}
                onClick={handleReject}
                className="px-5 py-2 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-lg transition"
              >
                {actionLoading ? "Rejecting..." : "Confirm Rejection"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* PARENTAL CONSENT MODAL */}
      {consentModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-stone-200">
            <h3 className="text-lg font-bold text-charcoal-900 mb-2">Verify Minor Parental Consent</h3>
            <p className="text-xs text-charcoal-600 mb-4">
              Documentary review under Section 4.5 of Maatram Safeguarding Directives.
            </p>
            {actionError && (
              <div className="p-3 mb-4 rounded-lg bg-red-50 text-red-700 text-xs border border-red-200">
                {actionError}
              </div>
            )}
            <div className="mb-4">
              <label className="block text-xs font-semibold text-charcoal-700 mb-1">Verification Status:</label>
              <select
                value={consentStatus}
                onChange={(e) => setConsentStatus(e.target.value as "VERIFIED" | "REJECTED")}
                className="w-full text-xs p-2.5 rounded-lg border border-stone-300 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
              >
                <option value="VERIFIED">VERIFIED — Signed Consent Form Received & Checked</option>
                <option value="REJECTED">REJECTED — Consent Refused or Invalid Document</option>
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-xs font-semibold text-charcoal-700 mb-1">
                Verification Notes:
              </label>
              <textarea
                value={consentNotes}
                onChange={(e) => setConsentNotes(e.target.value)}
                placeholder="e.g., Parent signed letter verified via phone confirmation"
                rows={3}
                className="w-full text-xs p-2.5 rounded-lg border border-stone-300 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
              />
            </div>
            <div className="flex items-center justify-end gap-3">
              <button
                type="button"
                disabled={actionLoading}
                onClick={() => setConsentModalOpen(false)}
                className="px-4 py-2 border border-stone-300 text-charcoal-700 text-xs font-semibold rounded-lg hover:bg-stone-50"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={actionLoading}
                onClick={handleVerifyConsent}
                className="px-5 py-2 bg-charcoal-900 hover:bg-charcoal-800 text-white font-bold text-xs rounded-lg transition"
              >
                {actionLoading ? "Saving..." : "Save Verification"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
