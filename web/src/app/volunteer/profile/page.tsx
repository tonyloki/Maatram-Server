"use client";

import React, { useState, useEffect, useCallback, Suspense } from "react";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  User,
  Shield,
  Award,
  CheckCircle2,
  Clock,
  Coins,
  Camera,
  Save,
  Check,
  AlertCircle,
  Loader2,
  Lock,
  Mail,
  Phone,
  GraduationCap,
  Briefcase,
  Building,
} from "lucide-react";
import { apiClient, ApiError } from "@/lib/api-client";
import {
  VolunteerProfileResponse,
  ConsentResponse,
  ConsentUpdate,
  GamificationSummaryResponse,
  VolunteerAchievementsListResponse,
  AchievementBadge,
} from "@/types";

type ProfileTab = "information" | "consents" | "achievements";

function ProfileContent() {
  const searchParams = useSearchParams();
  const initialTab = (searchParams.get("tab") as ProfileTab) || "consents";

  const [activeTab, setActiveTab] = useState<ProfileTab>(
    ["information", "consents", "achievements"].includes(initialTab) ? initialTab : "consents"
  );

  const [profile, setProfile] = useState<VolunteerProfileResponse | null>(null);
  const [consent, setConsent] = useState<ConsentResponse | null>(null);
  const [gamification, setGamification] = useState<GamificationSummaryResponse | null>(null);
  const [achievements, setAchievements] = useState<AchievementBadge[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form states for "My Information"
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [mobileNumber, setMobileNumber] = useState("");
  const [bio, setBio] = useState("");
  const [collegeName, setCollegeName] = useState("");
  const [degree, setDegree] = useState("");
  const [department, setDepartment] = useState("");
  const [organisation, setOrganisation] = useState("");
  const [jobRole, setJobRole] = useState("");

  const [isSavingInfo, setIsSavingInfo] = useState(false);
  const [infoMessage, setInfoMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Consent update state
  const [isUpdatingConsent, setIsUpdatingConsent] = useState(false);
  const [consentSuccessText, setConsentSuccessText] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [profRes, conRes, gamRes, achRes] = await Promise.all([
        apiClient<VolunteerProfileResponse>("/volunteers/me"),
        apiClient<ConsentResponse>("/consent/me").catch(() => null),
        apiClient<GamificationSummaryResponse>("/gamification/summary").catch(() => null),
        apiClient<VolunteerAchievementsListResponse>("/achievements").catch(() => ({
          items: [],
          total_earned: 0,
          total_available: 0,
        })),
      ]);

      setProfile(profRes);
      setConsent(conRes);
      setGamification(gamRes);
      setAchievements(achRes.items || []);

      // Populate form
      setFirstName(profRes.first_name || "");
      setLastName(profRes.last_name || "");
      setMobileNumber(profRes.mobile_number || "");
      setBio(profRes.bio || "");
      if (profRes.student_profile) {
        setCollegeName(profRes.student_profile.college_name || "");
        setDegree(profRes.student_profile.degree || "");
        setDepartment(profRes.student_profile.department || "");
      } else if (profRes.alumni_profile) {
        setCollegeName(profRes.alumni_profile.college_name || "");
        setDepartment(profRes.alumni_profile.department || "");
        setOrganisation(profRes.alumni_profile.organisation || "");
        setJobRole(profRes.alumni_profile.job_role || "");
      } else if (profRes.corporate_profile) {
        setOrganisation(profRes.corporate_profile.organisation || "");
        setJobRole(profRes.corporate_profile.designation || "");
      }
    } catch (err: unknown) {
      console.error("Failed to load profile data", err);
      setError("Unable to load profile data. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle Consent Toggle
  const handleToggleConsent = async (key: keyof ConsentUpdate) => {
    if (!consent) return;
    const previousValue = !!consent[key];
    const newValue = !previousValue;

    // Optimistic update
    setConsent({
      ...consent,
      [key]: newValue,
    });
    setConsentSuccessText("Consent preference updated.");
    setTimeout(() => setConsentSuccessText(null), 3000);

    try {
      setIsUpdatingConsent(true);
      const updated = await apiClient<ConsentResponse>("/consent/me", {
        method: "PUT",
        body: JSON.stringify({
          [key]: newValue,
        }),
      });
      setConsent(updated);
    } catch (err: unknown) {
      // Revert optimistic update on failure
      setConsent({
        ...consent,
        [key]: previousValue,
      });
      setConsentSuccessText(null);
      alert("Failed to save consent preference. Please try again.");
    } finally {
      setIsUpdatingConsent(false);
    }
  };

  // Handle Information Form Submit
  const handleSaveInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingInfo(true);
    setInfoMessage(null);
    try {
      const payload: Record<string, unknown> = {
        first_name: firstName,
        last_name: lastName,
        mobile_number: mobileNumber,
        bio,
      };

      if (profile?.category === "STUDENT") {
        payload.student_details = {
          college_name: collegeName,
          degree,
          department,
        };
      } else if (profile?.category === "ALUMNI") {
        payload.alumni_details = {
          organisation,
          job_role: jobRole,
          department,
        };
      } else if (profile?.category === "CORPORATE") {
        payload.corporate_details = {
          organisation,
          designation: jobRole,
        };
      }

      const updated = await apiClient<VolunteerProfileResponse>("/volunteers/me", {
        method: "PATCH",
        body: JSON.stringify(payload),
      });

      setProfile(updated);
      setInfoMessage({ type: "success", text: "Profile details updated successfully!" });
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        setInfoMessage({ type: "error", text: err.message || "Failed to update profile." });
      } else {
        setInfoMessage({ type: "error", text: "An unexpected error occurred while saving." });
      }
    } finally {
      setIsSavingInfo(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-charcoal-200/80">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
        <p className="text-sm font-medium text-charcoal-500 mt-3">Loading your volunteer profile...</p>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="bg-white rounded-3xl border border-charcoal-200/80 p-12 text-center max-w-md mx-auto space-y-4">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
        <h2 className="text-xl font-bold text-charcoal-900">{error || "Profile unavailable"}</h2>
        <button
          onClick={loadData}
          className="px-5 py-2.5 bg-primary-500 text-charcoal-950 font-bold rounded-xl shadow-xs hover:bg-primary-400 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  const fullName = `${profile.first_name} ${profile.last_name}`.trim();
  const collegeOrOrg =
    profile.student_profile?.college_name ||
    profile.alumni_profile?.college_name ||
    profile.corporate_profile?.organisation ||
    "Maatram Foundation";
  const deptOrRole =
    profile.student_profile?.department ||
    profile.alumni_profile?.job_role ||
    profile.corporate_profile?.designation ||
    "Volunteer Member";

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Page Title */}
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-charcoal-900 tracking-tight font-serif">
          My Profile
        </h1>
        <p className="text-sm text-charcoal-500 mt-1">
          Manage your personal details, DPDP affirmative consents, and view your verified gamification badges.
        </p>
      </div>

      {/* Main Two-Column Layout (Matching Screen 6) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Profile Card (Screen 6 Visual Match) */}
        <div className="lg:col-span-5 bg-white rounded-3xl border border-charcoal-200/80 p-6 md:p-8 shadow-xs space-y-6">
          {/* Avatar & Header */}
          <div className="flex flex-col items-center text-center">
            <div className="relative mb-3">
              <div className="w-24 h-24 rounded-full overflow-hidden bg-primary-100 ring-4 ring-primary-300/60 shadow-sm flex items-center justify-center text-primary-900 font-extrabold text-2xl relative">
                {profile.avatar_media_id ? (
                  <Image
                    src={`/api/v1/media/${profile.avatar_media_id}`}
                    alt={fullName}
                    fill
                    className="object-cover"
                  />
                ) : (
                  <span>
                    {profile.first_name[0]}
                    {profile.last_name[0]}
                  </span>
                )}
              </div>
              <button
                type="button"
                title="Change Avatar"
                className="absolute bottom-0 right-0 p-1.5 bg-charcoal-900 text-white rounded-full hover:bg-charcoal-800 shadow-sm transition-colors"
              >
                <Camera className="w-3.5 h-3.5" />
              </button>
            </div>

            <h2 className="text-xl font-bold text-charcoal-900">{fullName}</h2>

            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-charcoal-100 text-charcoal-700">
                {profile.category}
              </span>
              <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                Approved
              </span>
            </div>
          </div>

          {/* Details Table (Screen 6 Match) */}
          <div className="divide-y divide-charcoal-100 text-xs md:text-sm pt-2">
            <div className="py-2.5 flex items-center justify-between">
              <span className="text-charcoal-500 font-medium">Email</span>
              <span className="font-semibold text-charcoal-900 max-w-[200px] truncate">
                {profile.user_id ? "volunteer@maatram.org" : "user@maatram.org"}
              </span>
            </div>

            <div className="py-2.5 flex items-center justify-between">
              <span className="text-charcoal-500 font-medium">Phone</span>
              <span className="font-semibold text-charcoal-900">{profile.mobile_number || "—"}</span>
            </div>

            <div className="py-2.5 flex items-start justify-between gap-4">
              <span className="text-charcoal-500 font-medium flex-shrink-0">
                {profile.category === "STUDENT" ? "College" : "Organisation"}
              </span>
              <span className="font-semibold text-charcoal-900 text-right">{collegeOrOrg}</span>
            </div>

            <div className="py-2.5 flex items-start justify-between gap-4">
              <span className="text-charcoal-500 font-medium flex-shrink-0">
                {profile.category === "STUDENT" ? "Department" : "Designation"}
              </span>
              <span className="font-semibold text-charcoal-900 text-right">{deptOrRole}</span>
            </div>

            <div className="py-2.5 flex items-center justify-between">
              <span className="text-charcoal-500 font-medium">Total Hours</span>
              <span className="font-bold text-primary-800">
                {Number(gamification?.total_hours || 0)} hrs (This Year)
              </span>
            </div>

            <div className="py-2.5 flex items-center justify-between">
              <span className="text-charcoal-500 font-medium">Total Points</span>
              <span className="font-bold text-primary-800">
                {Number(gamification?.total_points || 0)} pts (This Year)
              </span>
            </div>
          </div>
        </div>

        {/* Right Section: Tabs & Content (Screen 6 Visual Match) */}
        <div className="lg:col-span-7 bg-white rounded-3xl border border-charcoal-200/80 p-6 md:p-8 shadow-xs space-y-6">
          {/* Tabs Navigation (Screen 6: My Information | Consents | Achievements) */}
          <div className="flex items-center gap-6 border-b border-charcoal-200 text-sm font-semibold">
            <button
              type="button"
              onClick={() => setActiveTab("information")}
              className={`pb-3 relative transition-colors ${
                activeTab === "information" ? "text-charcoal-950 font-bold" : "text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              My Information
              {activeTab === "information" && (
                <motion.div layoutId="profileTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
              )}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("consents")}
              className={`pb-3 relative transition-colors ${
                activeTab === "consents" ? "text-charcoal-950 font-bold" : "text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              Consents
              {activeTab === "consents" && (
                <motion.div layoutId="profileTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
              )}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("achievements")}
              className={`pb-3 relative transition-colors ${
                activeTab === "achievements" ? "text-charcoal-950 font-bold" : "text-charcoal-500 hover:text-charcoal-800"
              }`}
            >
              Achievements
              {activeTab === "achievements" && (
                <motion.div layoutId="profileTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500" />
              )}
            </button>
          </div>

          {/* TAB 1: Consents (Screen 6 Exact Match) */}
          {activeTab === "consents" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-charcoal-900">My Consents</h3>
                  <p className="text-xs text-charcoal-500">
                    Compliant with India's Digital Personal Data Protection Act (DPDPA 2023). Toggle permissions anytime.
                  </p>
                </div>
                {consentSuccessText && (
                  <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                    {consentSuccessText}
                  </span>
                )}
              </div>

              {/* Six DPDP Switches (Screen 6 Direct Match) */}
              <div className="space-y-4 pt-2">
                {/* 1. Leaderboard */}
                <div className="flex items-center justify-between p-3.5 rounded-2xl bg-charcoal-50/60 hover:bg-charcoal-50 border border-charcoal-100 transition-colors">
                  <div className="pr-4">
                    <p className="text-sm font-semibold text-charcoal-900">Show my name on Leaderboard</p>
                    <p className="text-xs text-charcoal-500">
                      When disabled, your score appears as “Anonymous Volunteer”.
                    </p>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    aria-checked={consent?.leaderboard_visible ?? true}
                    onClick={() => handleToggleConsent("leaderboard_visible")}
                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      consent?.leaderboard_visible ? "bg-primary-500" : "bg-charcoal-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                        consent?.leaderboard_visible ? "translate-x-5" : "translate-x-0"
                      }`}
                    />
                  </button>
                </div>

                {/* 2. Media / Photo Usage */}
                <div className="flex items-center justify-between p-3.5 rounded-2xl bg-charcoal-50/60 hover:bg-charcoal-50 border border-charcoal-100 transition-colors">
                  <div className="pr-4">
                    <p className="text-sm font-semibold text-charcoal-900">
                      Allow my photo to be used in communications
                    </p>
                    <p className="text-xs text-charcoal-500">
                      Event photo highlights, newsletters, and social media reels.
                    </p>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    aria-checked={consent?.media_usage ?? true}
                    onClick={() => handleToggleConsent("media_usage")}
                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      consent?.media_usage ? "bg-primary-500" : "bg-charcoal-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                        consent?.media_usage ? "translate-x-5" : "translate-x-0"
                      }`}
                    />
                  </button>
                </div>

                {/* 3. Emails from Maatram */}
                <div className="flex items-center justify-between p-3.5 rounded-2xl bg-charcoal-50/60 hover:bg-charcoal-50 border border-charcoal-100 transition-colors">
                  <div className="pr-4">
                    <p className="text-sm font-semibold text-charcoal-900">Receive emails from Maatram</p>
                    <p className="text-xs text-charcoal-500">
                      Impact summaries, upcoming event alerts, and thank you notes.
                    </p>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    aria-checked={consent?.thank_you_emails ?? true}
                    onClick={() => handleToggleConsent("thank_you_emails")}
                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      consent?.thank_you_emails ? "bg-primary-500" : "bg-charcoal-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                        consent?.thank_you_emails ? "translate-x-5" : "translate-x-0"
                      }`}
                    />
                  </button>
                </div>

                {/* 4. LinkedIn mentions */}
                <div className="flex items-center justify-between p-3.5 rounded-2xl bg-charcoal-50/60 hover:bg-charcoal-50 border border-charcoal-100 transition-colors">
                  <div className="pr-4">
                    <p className="text-sm font-semibold text-charcoal-900">
                      Allow LinkedIn mentions (e.g., appreciation posts)
                    </p>
                    <p className="text-xs text-charcoal-500">
                      Highlighting milestones, top quarterly contributions, and certificate tags.
                    </p>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    aria-checked={consent?.linkedin_content ?? true}
                    onClick={() => handleToggleConsent("linkedin_content")}
                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      consent?.linkedin_content ? "bg-primary-500" : "bg-charcoal-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                        consent?.linkedin_content ? "translate-x-5" : "translate-x-0"
                      }`}
                    />
                  </button>
                </div>

                {/* 5. Contact with coordinators */}
                <div className="flex items-center justify-between p-3.5 rounded-2xl bg-charcoal-50/60 hover:bg-charcoal-50 border border-charcoal-100 transition-colors">
                  <div className="pr-4">
                    <p className="text-sm font-semibold text-charcoal-900">
                      Share my contact with event coordinators
                    </p>
                    <p className="text-xs text-charcoal-500">
                      Permits coordinators to reach you via WhatsApp/call for urgent event briefing.
                    </p>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    aria-checked={consent?.contact_available ?? true}
                    onClick={() => handleToggleConsent("contact_available")}
                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      consent?.contact_available ? "bg-primary-500" : "bg-charcoal-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                        consent?.contact_available ? "translate-x-5" : "translate-x-0"
                      }`}
                    />
                  </button>
                </div>

                {/* 6. Name Visible on certificates */}
                <div className="flex items-center justify-between p-3.5 rounded-2xl bg-charcoal-50/60 hover:bg-charcoal-50 border border-charcoal-100 transition-colors">
                  <div className="pr-4">
                    <p className="text-sm font-semibold text-charcoal-900">
                      Show full name on certificates & public records
                    </p>
                    <p className="text-xs text-charcoal-500">
                      Used when generating downloadable volunteering certificates.
                    </p>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    aria-checked={consent?.name_visible ?? true}
                    onClick={() => handleToggleConsent("name_visible")}
                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                      consent?.name_visible ? "bg-primary-500" : "bg-charcoal-300"
                    }`}
                  >
                    <span
                      className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                        consent?.name_visible ? "translate-x-5" : "translate-x-0"
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: My Information */}
          {activeTab === "information" && (
            <form onSubmit={handleSaveInfo} className="space-y-4">
              {infoMessage && (
                <div
                  className={`p-3.5 rounded-xl text-xs md:text-sm font-semibold flex items-center gap-2 ${
                    infoMessage.type === "success"
                      ? "bg-emerald-50 border border-emerald-200 text-emerald-800"
                      : "bg-red-50 border border-red-200 text-red-800"
                  }`}
                >
                  {infoMessage.type === "success" ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-red-600" />
                  )}
                  {infoMessage.text}
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-sm font-medium text-charcoal-900 focus:ring-2 focus:ring-primary-400 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-sm font-medium text-charcoal-900 focus:ring-2 focus:ring-primary-400 focus:outline-none"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                  Mobile Number
                </label>
                <input
                  type="tel"
                  value={mobileNumber}
                  onChange={(e) => setMobileNumber(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-sm font-medium text-charcoal-900 focus:ring-2 focus:ring-primary-400 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                  Short Bio & Volunteering Interests
                </label>
                <textarea
                  rows={3}
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="Share a short summary about your background and motivation to mentor students..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-sm font-medium text-charcoal-900 focus:ring-2 focus:ring-primary-400 focus:outline-none"
                />
              </div>

              {profile.category === "STUDENT" && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-charcoal-100">
                  <div className="sm:col-span-2">
                    <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                      College Name
                    </label>
                    <input
                      type="text"
                      value={collegeName}
                      onChange={(e) => setCollegeName(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-sm font-medium text-charcoal-900 focus:ring-2 focus:ring-primary-400 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                      Degree
                    </label>
                    <input
                      type="text"
                      value={degree}
                      onChange={(e) => setDegree(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-sm font-medium text-charcoal-900 focus:ring-2 focus:ring-primary-400 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                      Department
                    </label>
                    <input
                      type="text"
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-sm font-medium text-charcoal-900 focus:ring-2 focus:ring-primary-400 focus:outline-none"
                    />
                  </div>
                </div>
              )}

              {(profile.category === "ALUMNI" || profile.category === "CORPORATE") && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-charcoal-100">
                  <div>
                    <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                      Current Organisation
                    </label>
                    <input
                      type="text"
                      value={organisation}
                      onChange={(e) => setOrganisation(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-sm font-medium text-charcoal-900 focus:ring-2 focus:ring-primary-400 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-charcoal-700 uppercase tracking-wider mb-1">
                      Job Role / Designation
                    </label>
                    <input
                      type="text"
                      value={jobRole}
                      onChange={(e) => setJobRole(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-charcoal-200 text-sm font-medium text-charcoal-900 focus:ring-2 focus:ring-primary-400 focus:outline-none"
                    />
                  </div>
                </div>
              )}

              <div className="pt-3">
                <button
                  type="submit"
                  disabled={isSavingInfo}
                  className="px-6 py-2.5 rounded-xl bg-charcoal-900 hover:bg-charcoal-800 text-white font-bold text-sm shadow-xs transition-colors flex items-center gap-2"
                >
                  {isSavingInfo ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" /> Save Changes
                    </>
                  )}
                </button>
              </div>
            </form>
          )}

          {/* TAB 3: Achievements */}
          {activeTab === "achievements" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-charcoal-900">Achievements & Badges</h3>
                  <p className="text-xs text-charcoal-500">
                    Milestone badges awarded automatically based on verified volunteering hours and activities.
                  </p>
                </div>
                <span className="text-xs font-bold text-primary-900 bg-primary-100 px-3 py-1 rounded-full">
                  {achievements.filter((a) => a.is_earned).length} / {achievements.length} Earned
                </span>
              </div>

              {achievements.length === 0 ? (
                <div className="p-8 text-center text-charcoal-400 text-sm">
                  No badges currently configured. Complete events to unlock special honors!
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
                  {achievements.map((badge) => (
                    <div
                      key={badge.id}
                      className={`p-4 rounded-2xl border transition-all flex items-start gap-3.5 ${
                        badge.is_earned
                          ? "bg-amber-50/50 border-amber-200 shadow-xs"
                          : "bg-charcoal-50/40 border-charcoal-200/70 opacity-60"
                      }`}
                    >
                      <div
                        className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 text-lg ${
                          badge.is_earned
                            ? "bg-amber-400 text-charcoal-950 shadow-xs"
                            : "bg-charcoal-200 text-charcoal-400"
                        }`}
                      >
                        {badge.is_earned ? <Award className="w-6 h-6" /> : <Lock className="w-5 h-5" />}
                      </div>

                      <div className="space-y-0.5">
                        <div className="flex items-center gap-1.5">
                          <h4 className="font-bold text-sm text-charcoal-900">{badge.title}</h4>
                          {badge.is_earned && (
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                          )}
                        </div>
                        <p className="text-xs text-charcoal-600 leading-snug">{badge.description}</p>
                        {badge.is_earned && badge.awarded_at && (
                          <p className="text-[10px] text-amber-800 font-semibold pt-1">
                            Earned on {new Date(badge.awarded_at).toLocaleDateString("en-IN")}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function VolunteerProfilePage() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-charcoal-200/80">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm font-medium text-charcoal-500 mt-3">Loading profile...</p>
        </div>
      }
    >
      <ProfileContent />
    </Suspense>
  );
}

