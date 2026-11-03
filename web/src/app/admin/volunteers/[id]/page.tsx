"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  User,
  GraduationCap,
  Briefcase,
  Calendar,
  Phone,
  Mail,
  MapPin,
  ShieldCheck,
  AlertTriangle,
  Award,
  Clock,
  Sparkles,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { VolunteerProfileResponse } from "@/types";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function AdminVolunteerProfilePage({ params }: PageProps) {
  const { id } = use(params);

  const [profile, setProfile] = useState<VolunteerProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await apiClient.get<VolunteerProfileResponse>(`/volunteers/${id}`);
        setProfile(res.data);
      } catch (err: unknown) {
        const e = err as { message?: string };
        setError(e.message || "Failed to load volunteer profile.");
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-10 h-10 border-4 border-amber-400 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm font-medium text-charcoal-500">Loading volunteer profile...</p>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 text-center">
        <div className="w-14 h-14 bg-red-50 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertTriangle className="w-7 h-7" />
        </div>
        <h2 className="text-xl font-bold text-charcoal-900 mb-2">Volunteer Not Found</h2>
        <p className="text-charcoal-600 mb-6">{error || "Could not retrieve the requested volunteer profile."}</p>
        <Link
          href="/admin/volunteers"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-amber-500 text-charcoal-900 font-semibold rounded-lg hover:bg-amber-400"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Directory
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-16">
      {/* Back button & Header */}
      <div>
        <Link
          href="/admin/volunteers"
          className="inline-flex items-center gap-2 text-sm font-medium text-charcoal-600 hover:text-charcoal-900 transition mb-3"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Volunteer Directory
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-amber-100 text-amber-900 font-bold text-xl flex items-center justify-center border-2 border-amber-300">
              {profile.first_name?.[0]}
              {profile.last_name?.[0]}
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight">
                  {profile.first_name} {profile.last_name}
                </h1>
                <span className="px-3 py-1 bg-amber-100 text-amber-900 rounded-full text-xs font-bold uppercase tracking-wider">
                  {profile.category}
                </span>
              </div>
              <p className="text-sm text-charcoal-500 mt-0.5">
                Volunteer ID: <span className="font-mono text-xs">{profile.id}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Minor Notice if applicable */}
      {profile.is_minor && (
        <div className="bg-amber-50 border border-amber-300 rounded-xl p-4 flex items-center gap-3">
          <ShieldCheck className="w-6 h-6 text-amber-700 shrink-0" />
          <div>
            <div className="text-sm font-bold text-amber-900">Minor Safeguarding Status</div>
            <div className="text-xs text-amber-800">
              Parental Consent: <strong>{profile.parental_consent_status || "PENDING"}</strong> • Date of Birth:{" "}
              {profile.date_of_birth}
            </div>
          </div>
        </div>
      )}

      {/* Grid: Contact & Category */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Contact Info */}
        <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-stone-100 pb-3">
            <User className="w-4 h-4 text-amber-600" />
            <h3 className="text-base font-bold text-charcoal-900">Contact & Demographics</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <span className="text-charcoal-400 font-semibold uppercase">Mobile Number</span>
              <p className="font-medium text-charcoal-900 flex items-center gap-1.5 mt-0.5 text-sm">
                <Phone className="w-3.5 h-3.5 text-stone-400" />
                {profile.mobile_number || "Restricted / None"}
              </p>
            </div>
            <div>
              <span className="text-charcoal-400 font-semibold uppercase">Date of Birth</span>
              <p className="font-medium text-charcoal-900 flex items-center gap-1.5 mt-0.5 text-sm">
                <Calendar className="w-3.5 h-3.5 text-stone-400" />
                {profile.date_of_birth || "N/A"}
              </p>
            </div>
            <div>
              <span className="text-charcoal-400 font-semibold uppercase">Gender</span>
              <p className="font-medium text-charcoal-900 capitalize mt-0.5 text-sm">{profile.gender || "N/A"}</p>
            </div>
            <div>
              <span className="text-charcoal-400 font-semibold uppercase">Location</span>
              <p className="font-medium text-charcoal-900 mt-0.5 text-sm">
                {profile.city ? `${profile.city}, ${profile.state}` : "N/A"}
              </p>
            </div>
            <div className="sm:col-span-2">
              <span className="text-charcoal-400 font-semibold uppercase">Full Address</span>
              <p className="font-medium text-charcoal-800 flex items-start gap-1.5 mt-0.5 text-xs">
                <MapPin className="w-3.5 h-3.5 text-stone-400 shrink-0 mt-0.5" />
                {profile.address_line1 ? (
                  <>
                    {profile.address_line1}
                    {profile.address_line2 ? `, ${profile.address_line2}` : ""}
                    {profile.city ? `, ${profile.city}` : ""}
                    {profile.pincode ? ` - ${profile.pincode}` : ""}
                  </>
                ) : (
                  "No address recorded"
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Category Affiliation */}
        <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-stone-100 pb-3">
            {profile.category === "STUDENT" ? (
              <GraduationCap className="w-4 h-4 text-amber-600" />
            ) : (
              <Briefcase className="w-4 h-4 text-amber-600" />
            )}
            <h3 className="text-base font-bold text-charcoal-900">Institutional Affiliation</h3>
          </div>

          <div className="space-y-3 text-xs">
            {profile.category === "STUDENT" ? (
              <>
                <div>
                  <span className="text-charcoal-400 font-semibold uppercase">College / University</span>
                  <p className="font-semibold text-charcoal-900 text-sm mt-0.5">{profile.college_name || "N/A"}</p>
                </div>
                <div>
                  <span className="text-charcoal-400 font-semibold uppercase">Department</span>
                  <p className="font-medium text-charcoal-800 mt-0.5">{profile.department || "N/A"}</p>
                </div>
                <div>
                  <span className="text-charcoal-400 font-semibold uppercase">Graduation Year</span>
                  <p className="font-medium text-charcoal-800 mt-0.5">{profile.graduation_year || "N/A"}</p>
                </div>
                <div>
                  <span className="text-charcoal-400 font-semibold uppercase">Student Roll / ID</span>
                  <p className="font-mono text-charcoal-800 mt-0.5">{profile.student_id || "N/A"}</p>
                </div>
              </>
            ) : (
              <>
                <div>
                  <span className="text-charcoal-400 font-semibold uppercase">Employer / Organisation</span>
                  <p className="font-semibold text-charcoal-900 text-sm mt-0.5">{profile.employer_name || "N/A"}</p>
                </div>
                <div>
                  <span className="text-charcoal-400 font-semibold uppercase">Designation / Role</span>
                  <p className="font-medium text-charcoal-800 mt-0.5">{profile.job_title || "N/A"}</p>
                </div>
                {profile.industry && (
                  <div>
                    <span className="text-charcoal-400 font-semibold uppercase">Industry</span>
                    <p className="font-medium text-charcoal-800 mt-0.5">{profile.industry}</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Skills & Bio */}
      <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs">
        <h3 className="text-base font-bold text-charcoal-900 mb-3">Skills & Experience Profile</h3>
        <div className="flex flex-wrap gap-2 mb-4">
          {profile.skills && profile.skills.length > 0 ? (
            profile.skills.map((s: string, idx: number) => (
              <span key={idx} className="px-3 py-1 bg-amber-50 text-amber-900 text-xs font-semibold rounded-md">
                {s}
              </span>
            ))
          ) : (
            <span className="text-charcoal-400 italic text-xs">No specific skills listed</span>
          )}
        </div>
        {profile.bio && (
          <div className="text-xs text-charcoal-700 bg-stone-50 p-4 rounded-lg border border-stone-100">
            <span className="font-semibold text-charcoal-900 block mb-1">Personal Statement:</span>
            {profile.bio}
          </div>
        )}
      </div>
    </div>
  );
}

