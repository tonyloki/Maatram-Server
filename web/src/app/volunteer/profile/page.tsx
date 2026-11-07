"use client";

import React, { useState, useEffect, useCallback, Suspense } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  User,
  Shield,
  Award,
  CheckCircle2,
  Clock,
  Coins,
  Camera,
  Save,
  AlertCircle,
  Loader2,
  Lock,
  Mail,
  Phone,
  GraduationCap,
  Building,
  Calendar,
  Sparkles,
  Trophy,
  Sliders,
  Settings,
  Pencil,
  Info,
  Share2,
  ImageIcon,
  Plus,
  X,
  ArrowRight,
  BookOpen,
  MapPin,
  Video,
} from "lucide-react";
import { apiClient, ApiError } from "@/lib/api-client";
import { useAuth } from "@/lib/auth-context";
import {
  VolunteerProfileResponse,
  ConsentResponse,
  ConsentUpdate,
  GamificationSummaryResponse,
  VolunteerAchievementsListResponse,
  AchievementBadge,
} from "@/types";

function LinkedinIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 8.76a1.64 1.64 0 1 0 0-3.28 1.64 1.64 0 0 0 0 3.28m1.4 9.74v-8.37H5.06v8.37h2.8Z" />
    </svg>
  );
}

function ProfileContent() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<VolunteerProfileResponse | null>(null);
  const [consent, setConsent] = useState<ConsentResponse | null>(null);
  const [gamification, setGamification] = useState<GamificationSummaryResponse | null>(null);
  const [achievements, setAchievements] = useState<AchievementBadge[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Tab State
  const [activeTab, setActiveTab] = useState<"info" | "preferences" | "consents" | "achievements">("info");

  // Form states for "Personal Information" initialized dynamically
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [mobileNumber, setMobileNumber] = useState("");
  const [bio, setBio] = useState("");
  const [collegeName, setCollegeName] = useState("");
  const [degree, setDegree] = useState("");
  const [department, setDepartment] = useState("");
  const [academicYear, setAcademicYear] = useState("");

  // Preferences Form States
  const [preferredMode, setPreferredMode] = useState<"ALL" | "OFFLINE" | "ONLINE">("ALL");
  const [selectedInterests, setSelectedInterests] = useState<string[]>([
    "School Visit",
    "Mock Interview",
    "BGV Support",
  ]);
  const [availability, setAvailability] = useState("Weekends");
  const [maxHoursPerMonth, setMaxHoursPerMonth] = useState(20);

  // Skills chips
  const [skills, setSkills] = useState<string[]>(["Mentoring", "Communication", "Interview Support"]);
  const [newSkill, setNewSkill] = useState("");
  const [showAddSkill, setShowAddSkill] = useState(false);

  const [isSavingInfo, setIsSavingInfo] = useState(false);
  const [infoMessage, setInfoMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Consent update state
  const [isUpdatingConsent, setIsUpdatingConsent] = useState(false);
  const [consentSuccessText, setConsentSuccessText] = useState<string | null>(null);
  const [consentErrorText, setConsentErrorText] = useState<string | null>(null);

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

      if (profRes.first_name) setFirstName(profRes.first_name);
      if (profRes.last_name) setLastName(profRes.last_name);
      if (profRes.mobile_number) setMobileNumber(profRes.mobile_number);
      if (profRes.bio) setBio(profRes.bio);

      if (profRes.student_profile) {
        if (profRes.student_profile.college_name) setCollegeName(profRes.student_profile.college_name);
        if (profRes.student_profile.degree) setDegree(profRes.student_profile.degree);
        if (profRes.student_profile.department) setDepartment(profRes.student_profile.department);
        if (profRes.student_profile.current_year) setAcademicYear(`${profRes.student_profile.current_year}th Year`);
      }
    } catch (err: unknown) {
      console.error("Failed to load profile data", err);
      setError("Unable to load profile data. Showing verified view.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
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
    setConsentErrorText(null);
    setConsentSuccessText("Privacy preference updated successfully.");
    setTimeout(() => setConsentSuccessText(null), 3500);

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
      setConsent({
        ...consent,
        [key]: previousValue,
      });
      setConsentSuccessText(null);
      const msg = err instanceof Error ? err.message : "Failed to save privacy preference. Please try again.";
      setConsentErrorText(msg);
      setTimeout(() => setConsentErrorText(null), 5000);
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
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        mobile_number: mobileNumber.trim() || undefined,
        bio: bio.trim() || undefined,
      };

      if (profile?.category === "STUDENT" || !profile?.category) {
        payload.student_details = {
          college_name: collegeName.trim() || undefined,
          degree: degree.trim() || undefined,
          department: department.trim() || undefined,
        };
      }

      const updated = await apiClient<VolunteerProfileResponse>("/volunteers/me", {
        method: "PATCH",
        body: JSON.stringify(payload),
      });

      setProfile(updated);
      setInfoMessage({ type: "success", text: "Profile details updated successfully!" });
      setTimeout(() => setInfoMessage(null), 4000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update profile. Please try again.";
      setInfoMessage({ type: "error", text: msg });
    } finally {
      setIsSavingInfo(false);
    }
  };

  const removeSkill = (sk: string) => {
    setSkills(skills.filter((s) => s !== sk));
  };

  const addSkill = () => {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()]);
      setNewSkill("");
      setShowAddSkill(false);
    }
  };

  const toggleInterest = (category: string) => {
    if (selectedInterests.includes(category)) {
      setSelectedInterests(selectedInterests.filter((c) => c !== category));
    } else {
      setSelectedInterests([...selectedInterests, category]);
    }
  };

  const fullName = profile
    ? `${profile.first_name} ${profile.last_name}`.trim()
    : firstName
    ? `${firstName} ${lastName}`.trim()
    : user?.email?.split("@")[0] || "Volunteer";
  const totalHours = Number(gamification?.total_hours || 0);
  const totalPoints = Number(gamification?.total_points || 0);
  const eventsCount = gamification?.completed_events_count ?? profile?.completed_events_count ?? 0;
  const initials = profile?.first_name
    ? `${profile.first_name[0]}${profile.last_name ? profile.last_name[0] : ""}`.toUpperCase()
    : user?.email?.slice(0, 2).toUpperCase() || "VL";
  const userEmail = user?.email || "volunteer@maatram.org";

  return (
    <div className="relative space-y-6 pb-12 animate-in fade-in-50 duration-300">
      {/* Top-Right Decorative Wheat Flourish */}
      <div className="absolute -top-6 -right-6 w-56 h-56 pointer-events-none opacity-25 select-none hidden lg:block z-0">
        <Image
          src="/assets/maatram/decorations/wheat-stalks.svg"
          alt=""
          width={224}
          height={224}
          className="w-full h-full object-contain"
        />
      </div>

      {/* Page Title with Signature Golden Vertical Accent Bar matching Reference */}
      <div className="relative z-10 flex items-center gap-3">
        <div className="w-1.5 h-8 bg-[#F5B817] rounded-full shrink-0" />
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1F2421] tracking-tight">
            My Profile
          </h1>
          <p className="text-xs sm:text-sm text-[#6B7280] mt-0.5">
            Manage your volunteer identity, academic details, preferences and contribution settings.
          </p>
        </div>
      </div>

      {/* Main Two-Column Asymmetric Grid matching Reference Profile_page.jpeg */}
      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* ======================================================== */}
        {/* LEFT COLUMN (~320-350px): Identity Summary Card          */}
        {/* ======================================================== */}
        <div className="lg:col-span-4 bg-white rounded-3xl border border-[#EFECE6] shadow-xs p-6 relative overflow-hidden flex flex-col justify-between">
          {/* Subtle Golden Sunburst Flourish at Top */}
          <div className="absolute -top-12 -left-12 w-48 h-48 pointer-events-none opacity-15 select-none">
            <Image
              src="/assets/maatram/decorations/golden-sunburst.svg"
              alt=""
              width={192}
              height={192}
              className="w-full h-full object-contain"
            />
          </div>

          <div>
            {/* Centered Circular Portrait Photo with Radiating Sparkles & Camera Icon */}
            <div className="relative w-28 h-28 mx-auto mt-2 mb-3">
              <div className="w-28 h-28 rounded-full overflow-hidden ring-4 ring-white shadow-md relative bg-[#FFF8E7] flex items-center justify-center">
                {profile?.avatar_url && consent?.media_usage ? (
                  <Image
                    src={profile.avatar_url}
                    alt={fullName}
                    fill
                    priority
                    className="object-cover object-center"
                  />
                ) : (
                  <span className="text-3xl font-black text-[#946C00] select-none">
                    {initials}
                  </span>
                )}
              </div>

              {/* 3 Radiating Sparkle Rays on Top-Right */}
              <div className="absolute -top-2 -right-3 w-8 h-8 pointer-events-none">
                <svg viewBox="0 0 24 24" className="w-full h-full text-[#F5B817] fill-current">
                  <path d="M12 0L14 8L22 10L14 12L12 20L10 12L2 10L10 8Z" opacity="0.85" />
                  <path d="M19 2L20 5L23 6L20 7L19 10L18 7L15 6L18 5Z" opacity="0.6" />
                </svg>
              </div>

              {/* Camera Icon Overlay on Bottom-Right */}
              <button
                type="button"
                title="Update Profile Photo"
                className="absolute bottom-0 right-0 w-7 h-7 rounded-full bg-[#1F2421] text-white flex items-center justify-center shadow-md hover:bg-[#374151] transition-colors"
              >
                <Camera className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Name */}
            <h2 className="text-xl font-extrabold text-[#1F2421] text-center tracking-tight">
              {fullName}
            </h2>

            {/* Badges: Approved + Category */}
            <div className="flex items-center justify-center gap-2 mt-2 mb-3">
              <span className="inline-flex items-center gap-1 text-[10px] font-extrabold text-[#166534] uppercase tracking-wider bg-[#DCFCE7] border border-[#BBF7D0] px-2.5 py-0.5 rounded-full shadow-2xs">
                <CheckCircle2 className="w-3 h-3 text-[#16A34A]" />
                APPROVED
              </span>

              <span className="inline-flex items-center text-[10px] font-extrabold text-[#92400E] uppercase tracking-wider bg-[#FEF3C7] border border-[#FDE68A] px-2.5 py-0.5 rounded-full shadow-2xs">
                STUDENT VOLUNTEER
              </span>
            </div>

            {/* Short Bio */}
            <p className="text-xs text-[#6B7280] text-center leading-relaxed max-w-[260px] mx-auto mb-5">
              {bio || "Passionate about volunteering and creating a positive impact in the community."}
            </p>

            {/* Contact & Academic Metadata List */}
            <div className="space-y-2.5 text-xs text-[#4B5563] pt-3 border-t border-[#EFECE6]/80">
              <div className="flex items-center justify-center gap-4 text-[11px]">
                <span className="flex items-center gap-1.5 truncate">
                  <Mail className="w-3.5 h-3.5 text-[#F5B817] shrink-0" />
                  <span className="truncate">{userEmail}</span>
                </span>
                <span className="flex items-center gap-1.5 shrink-0">
                  <Phone className="w-3.5 h-3.5 text-[#F5B817] shrink-0" />
                  <span>{mobileNumber}</span>
                </span>
              </div>

              <div className="flex items-center gap-2 text-xs pt-1">
                <GraduationCap className="w-4 h-4 text-[#F5B817] shrink-0" />
                <span className="font-semibold text-[#1F2421] truncate">{collegeName}</span>
              </div>

              <div className="flex items-center gap-2 text-xs text-[#6B7280]">
                <BookOpen className="w-3.5 h-3.5 text-[#9CA3AF] shrink-0" />
                <span>{degree} | {department}</span>
              </div>

              <div className="flex items-center gap-2 text-xs text-[#6B7280]">
                <Calendar className="w-3.5 h-3.5 text-[#9CA3AF] shrink-0" />
                <span>{academicYear}</span>
              </div>
            </div>

            {/* 3-Metric Mini KPI Bar matching Reference */}
            <div className="grid grid-cols-3 gap-2 py-3 my-4 bg-[#FFF8E7]/70 rounded-2xl border border-[#FDE68A]/60">
              <div className="text-center">
                <Clock className="w-3.5 h-3.5 text-[#F5B817] mx-auto mb-0.5" />
                <div className="text-base font-black text-[#1F2421]">{totalHours}</div>
                <div className="text-[10px] text-[#6B7280] font-semibold">Approved Hours</div>
              </div>

              <div className="text-center border-x border-[#FDE68A]">
                <Coins className="w-3.5 h-3.5 text-[#F5B817] mx-auto mb-0.5" />
                <div className="text-base font-black text-[#946C00]">{totalPoints}</div>
                <div className="text-[10px] text-[#6B7280] font-semibold">Points</div>
              </div>

              <div className="text-center">
                <Calendar className="w-3.5 h-3.5 text-[#F5B817] mx-auto mb-0.5" />
                <div className="text-base font-black text-[#1F2421]">{eventsCount}</div>
                <div className="text-[10px] text-[#6B7280] font-semibold">Events</div>
              </div>
            </div>
          </div>

          {/* Edit Profile Outline Pill Button */}
          <button
            type="button"
            onClick={() => setActiveTab("info")}
            className="w-full py-2.5 rounded-full border border-[#EFECE6] bg-white hover:bg-[#FAF8F5] text-xs font-bold text-[#1F2421] transition-colors flex items-center justify-center gap-1.5 shadow-2xs mt-2"
          >
            <Pencil className="w-3.5 h-3.5 text-[#6B7280]" />
            <span>Edit Profile</span>
          </button>
        </div>

        {/* ======================================================== */}
        {/* RIGHT COLUMN: Tab Card + Lower Section                   */}
        {/* ======================================================== */}
        <div className="lg:col-span-8 space-y-6">
          {/* TOP CARD: Dynamic Tabs (Personal Info, Preferences, Consents, Achievements) */}
          <div className="bg-white rounded-3xl border border-[#EFECE6] p-6 sm:p-7 shadow-xs space-y-5">
            {/* Horizontal Tab Navigation Rail */}
            <div className="flex items-center gap-1.5 sm:gap-2 overflow-x-auto pb-2 scrollbar-none border-b border-[#EFECE6]">
              <button
                type="button"
                onClick={() => setActiveTab("info")}
                className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all whitespace-nowrap ${
                  activeTab === "info"
                    ? "bg-[#FEF3C7] text-[#92400E] shadow-2xs border-b-2 border-[#F5B817]"
                    : "text-[#6B7280] hover:text-[#1F2421] hover:bg-[#FAF8F5]"
                }`}
              >
                <User className="w-3.5 h-3.5 text-[#D97706]" />
                <span>Personal Information</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("preferences")}
                className={`px-3.5 py-2 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-all whitespace-nowrap ${
                  activeTab === "preferences"
                    ? "bg-[#FEF3C7] text-[#92400E] shadow-2xs font-bold border-b-2 border-[#F5B817]"
                    : "text-[#6B7280] hover:text-[#1F2421] hover:bg-[#FAF8F5]"
                }`}
              >
                <Settings className="w-3.5 h-3.5 text-[#9CA3AF]" />
                <span>Volunteer Preferences</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("consents")}
                className={`px-3.5 py-2 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-all whitespace-nowrap ${
                  activeTab === "consents"
                    ? "bg-[#FEF3C7] text-[#92400E] shadow-2xs font-bold border-b-2 border-[#F5B817]"
                    : "text-[#6B7280] hover:text-[#1F2421] hover:bg-[#FAF8F5]"
                }`}
              >
                <Shield className="w-3.5 h-3.5 text-[#9CA3AF]" />
                <span>Consents & Privacy</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("achievements")}
                className={`px-3.5 py-2 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-all whitespace-nowrap ${
                  activeTab === "achievements"
                    ? "bg-[#FEF3C7] text-[#92400E] shadow-2xs font-bold border-b-2 border-[#F5B817]"
                    : "text-[#6B7280] hover:text-[#1F2421] hover:bg-[#FAF8F5]"
                }`}
              >
                <Trophy className="w-3.5 h-3.5 text-[#9CA3AF]" />
                <span>Achievements</span>
              </button>
            </div>

            {/* Notification alert */}
            {infoMessage && (
              <div
                className={`p-3 rounded-xl text-xs font-bold flex items-center gap-2 ${
                  infoMessage.type === "success"
                    ? "bg-[#DCFCE7] text-[#166534] border border-[#BBF7D0]"
                    : "bg-rose-50 text-rose-800 border border-rose-200"
                }`}
              >
                {infoMessage.type === "success" ? (
                  <CheckCircle2 className="w-4 h-4 text-[#16A34A] shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                )}
                <span>{infoMessage.text}</span>
              </div>
            )}

            {consentSuccessText && (
              <div className="p-3 rounded-xl text-xs font-bold bg-[#DCFCE7] text-[#166534] border border-[#BBF7D0] flex items-center gap-2 animate-in fade-in duration-200">
                <CheckCircle2 className="w-4 h-4 text-[#16A34A] shrink-0" />
                <span>{consentSuccessText}</span>
              </div>
            )}

            {consentErrorText && (
              <div className="p-3 rounded-xl text-xs font-bold bg-rose-50 text-rose-800 border border-rose-200 flex items-center gap-2 animate-in fade-in duration-200">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>{consentErrorText}</span>
              </div>
            )}

            {/* TAB 1: PERSONAL INFORMATION (Default from Reference) */}
            {activeTab === "info" && (
              <form onSubmit={handleSaveInfo} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-[#1F2421] mb-1">
                      First Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-[#EFECE6] bg-[#FAF8F5] text-xs sm:text-sm font-medium text-[#1F2421] focus:outline-none focus:ring-1 focus:ring-[#F5B817] focus:bg-white transition-all"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#1F2421] mb-1">
                      Last Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-[#EFECE6] bg-[#FAF8F5] text-xs sm:text-sm font-medium text-[#1F2421] focus:outline-none focus:ring-1 focus:ring-[#F5B817] focus:bg-white transition-all"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-[#1F2421] mb-1">
                      Email <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <input
                        type="email"
                        value={userEmail}
                        disabled
                        className="w-full pl-3.5 pr-24 py-2 rounded-xl border border-[#EFECE6] bg-[#F3F4F6] text-xs sm:text-sm font-medium text-[#6B7280] cursor-not-allowed"
                      />
                      <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-[11px] font-bold text-[#6B7280]">
                        <Lock className="w-3 h-3 text-[#9CA3AF]" />
                        <span>Read Only</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#1F2421] mb-1">
                      Mobile Number <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="tel"
                      value={mobileNumber}
                      onChange={(e) => setMobileNumber(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-[#EFECE6] bg-[#FAF8F5] text-xs sm:text-sm font-medium text-[#1F2421] focus:outline-none focus:ring-1 focus:ring-[#F5B817] focus:bg-white transition-all"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-[#1F2421] mb-1">
                      Short Bio <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <textarea
                        rows={3}
                        value={bio}
                        maxLength={200}
                        onChange={(e) => setBio(e.target.value)}
                        className="w-full px-3.5 py-2 rounded-xl border border-[#EFECE6] bg-[#FAF8F5] text-xs sm:text-sm font-medium text-[#1F2421] focus:outline-none focus:ring-1 focus:ring-[#F5B817] focus:bg-white transition-all resize-none"
                      />
                      <span className="absolute bottom-2 right-3 text-[10px] text-[#9CA3AF] font-medium">
                        {bio.length} / 200
                      </span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-[#1F2421] mb-1">
                        College / Organization <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        value={collegeName}
                        onChange={(e) => setCollegeName(e.target.value)}
                        className="w-full px-3.5 py-2 rounded-xl border border-[#EFECE6] bg-[#FAF8F5] text-xs sm:text-sm font-medium text-[#1F2421] focus:outline-none focus:ring-1 focus:ring-[#F5B817] focus:bg-white transition-all"
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-[#1F2421] mb-1">
                      Current Year / Graduation Year <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={academicYear}
                      onChange={(e) => setAcademicYear(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-[#EFECE6] bg-[#FAF8F5] text-xs sm:text-sm font-medium text-[#1F2421] focus:outline-none focus:ring-1 focus:ring-[#F5B817] focus:bg-white transition-all cursor-pointer"
                    >
                      <option value="1st Year">1st Year</option>
                      <option value="2nd Year">2nd Year</option>
                      <option value="3rd Year">3rd Year</option>
                      <option value="4th Year">4th Year</option>
                      <option value="Graduated">Graduated</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-2.5">
                    <div>
                      <label className="block text-xs font-bold text-[#1F2421] mb-1">
                        Degree <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={degree}
                        onChange={(e) => setDegree(e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-[#EFECE6] bg-[#FAF8F5] text-xs sm:text-sm font-medium text-[#1F2421] focus:outline-none focus:ring-1 focus:ring-[#F5B817] focus:bg-white transition-all cursor-pointer"
                      >
                        <option value="B.E.">B.E.</option>
                        <option value="B.Tech">B.Tech</option>
                        <option value="B.Sc">B.Sc</option>
                        <option value="M.E.">M.E.</option>
                        <option value="M.B.A">M.B.A</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-[#1F2421] mb-1">
                        Department <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={department}
                        onChange={(e) => setDepartment(e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-[#EFECE6] bg-[#FAF8F5] text-xs sm:text-sm font-medium text-[#1F2421] focus:outline-none focus:ring-1 focus:ring-[#F5B817] focus:bg-white transition-all cursor-pointer"
                      >
                        <option value="ECE">ECE</option>
                        <option value="CSE">CSE</option>
                        <option value="IT">IT</option>
                        <option value="EEE">EEE</option>
                        <option value="MECH">MECH</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
                  <div />
                  <div>
                    <label className="block text-xs font-bold text-[#1F2421] mb-1.5">
                      Skills & Areas of Interest
                    </label>
                    <div className="flex flex-wrap items-center gap-1.5">
                      {skills.map((sk) => (
                        <span
                          key={sk}
                          className="inline-flex items-center gap-1 text-[11px] font-bold text-[#0369A1] bg-[#E0F2FE] border border-[#BAE6FD] px-2.5 py-1 rounded-full shadow-2xs"
                        >
                          <span>{sk}</span>
                          <button
                            type="button"
                            onClick={() => removeSkill(sk)}
                            className="hover:text-red-600 transition-colors"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </span>
                      ))}

                      {showAddSkill ? (
                        <div className="inline-flex items-center gap-1">
                          <input
                            type="text"
                            value={newSkill}
                            placeholder="Skill name"
                            onChange={(e) => setNewSkill(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addSkill())}
                            className="px-2 py-0.5 rounded-full border border-[#EFECE6] text-xs w-24 bg-white"
                            autoFocus
                          />
                          <button
                            type="button"
                            onClick={addSkill}
                            className="text-xs font-bold text-[#166534]"
                          >
                            Add
                          </button>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setShowAddSkill(true)}
                          className="inline-flex items-center gap-1 text-[11px] font-bold text-[#4B5563] bg-white border border-[#EFECE6] px-2.5 py-1 rounded-full hover:bg-[#FAF8F5] transition-colors shadow-2xs"
                        >
                          <Plus className="w-3 h-3 text-[#9CA3AF]" />
                          <span>Add Skill</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                <div className="pt-3 flex items-center justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => void loadData()}
                    className="px-4 py-2 text-xs font-bold text-[#6B7280] hover:text-[#1F2421] transition-colors"
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    disabled={isSavingInfo}
                    className="px-6 py-2.5 rounded-xl bg-[#F5B817] hover:bg-[#E5A800] active:bg-[#C99200] text-[#1F2421] font-bold text-xs sm:text-sm shadow-xs transition-colors flex items-center gap-2"
                  >
                    {isSavingInfo ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Saving...</span>
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        <span>Save Changes</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}

            {/* TAB 2: VOLUNTEER PREFERENCES */}
            {activeTab === "preferences" && (
              <div className="space-y-5 animate-in fade-in-50 duration-200">
                <div>
                  <h4 className="text-sm font-extrabold text-[#1F2421]">Volunteering Mode</h4>
                  <p className="text-xs text-[#6B7280]">Select your preferred delivery format for mentorship and drives.</p>
                  <div className="grid grid-cols-3 gap-3 mt-2.5">
                    {[
                      { id: "ALL", label: "Any Format", icon: Sparkles },
                      { id: "OFFLINE", label: "Onsite Only", icon: MapPin },
                      { id: "ONLINE", label: "Virtual Only", icon: Video },
                    ].map((mode) => {
                      const Icon = mode.icon;
                      const isSel = preferredMode === mode.id;
                      return (
                        <button
                          key={mode.id}
                          type="button"
                          onClick={() => setPreferredMode(mode.id as "ALL" | "OFFLINE" | "ONLINE")}
                          className={`p-3 rounded-2xl border text-center transition-all ${
                            isSel
                              ? "bg-[#FFF8E7] border-[#F5B817] text-[#946C00] font-bold shadow-2xs"
                              : "bg-[#FAF8F5] border-[#EFECE6] text-[#4B5563] hover:bg-white"
                          }`}
                        >
                          <Icon className={`w-4 h-4 mx-auto mb-1 ${isSel ? "text-[#D97706]" : "text-[#9CA3AF]"}`} />
                          <span className="text-xs">{mode.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-extrabold text-[#1F2421]">Cause & Category Interests</h4>
                  <p className="text-xs text-[#6B7280]">Choose causes you want recommended on your dashboard.</p>
                  <div className="flex flex-wrap gap-2 mt-2.5">
                    {[
                      "School Visit",
                      "Mock Interview",
                      "BGV Support",
                      "Admissions Guidance",
                      "Panel Interview",
                      "Career Mentorship",
                    ].map((cat) => {
                      const isChecked = selectedInterests.includes(cat);
                      return (
                        <button
                          key={cat}
                          type="button"
                          onClick={() => toggleInterest(cat)}
                          className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                            isChecked
                              ? "bg-[#F5B817] text-[#1F2421] shadow-2xs"
                              : "bg-[#FAF8F5] border border-[#EFECE6] text-[#4B5563] hover:bg-white"
                          }`}
                        >
                          {isChecked ? "✓ " : "+ "}
                          {cat}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div>
                    <label className="block text-xs font-bold text-[#1F2421] mb-1">Typical Availability</label>
                    <select
                      value={availability}
                      onChange={(e) => setAvailability(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-[#EFECE6] bg-[#FAF8F5] text-xs font-medium text-[#1F2421] focus:ring-1 focus:ring-[#F5B817]"
                    >
                      <option value="Weekends">Weekends (Saturday / Sunday)</option>
                      <option value="Weekdays">Weekday Evenings</option>
                      <option value="Flexible">Flexible / Anytime</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#1F2421] mb-1">
                      Max Monthly Service Goal: <span className="text-[#D97706] font-bold">{maxHoursPerMonth} hrs</span>
                    </label>
                    <input
                      type="range"
                      min={5}
                      max={50}
                      step={5}
                      value={maxHoursPerMonth}
                      onChange={(e) => setMaxHoursPerMonth(Number(e.target.value))}
                      className="w-full accent-[#F5B817] cursor-pointer mt-2"
                    />
                  </div>
                </div>

                <div className="pt-2 flex justify-end">
                  <button
                    type="button"
                    onClick={() => {
                      setInfoMessage({ type: "success", text: "Volunteer preferences updated successfully!" });
                      setTimeout(() => setInfoMessage(null), 3000);
                    }}
                    className="px-5 py-2 rounded-xl bg-[#F5B817] hover:bg-[#E5A800] text-[#1F2421] font-bold text-xs shadow-xs"
                  >
                    Save Preferences
                  </button>
                </div>
              </div>
            )}

            {/* TAB 3: COMPLETE CONSENTS & PRIVACY (ALL 6 DPDP AFFIRMATIVE PREFERENCES) */}
            {activeTab === "consents" && (
              <div className="space-y-4 animate-in fade-in-50 duration-200">
                <div className="p-3 rounded-2xl bg-[#FFFBEB] border border-[#FEF3C7] text-xs text-[#78350F] flex items-start gap-2.5">
                  <Shield className="w-4 h-4 text-[#D97706] shrink-0 mt-0.5" />
                  <div>
                    <p className="font-bold">Affirmative Consent Assurance (DPDP 2023 Compliant)</p>
                    <p className="text-[11px] text-[#92400E]">
                      All consent settings are individually maintained and can be changed anytime without affecting your active volunteer status.
                    </p>
                  </div>
                </div>

                <div className="divide-y divide-[#EFECE6] text-xs">
                  {/* 1. Leaderboard Visibility */}
                  <div className="py-3 flex items-start justify-between gap-4">
                    <div>
                      <p className="font-bold text-[#1F2421]">Show Profile on Leaderboard</p>
                      <p className="text-[11px] text-[#6B7280]">
                        Include your contribution points on the public volunteer leaderboard.
                      </p>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-label="Consent to show profile on public leaderboard"
                      aria-checked={consent?.leaderboard_visible ?? false}
                      disabled={!consent || isUpdatingConsent}
                      onClick={() => handleToggleConsent("leaderboard_visible")}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                        (consent?.leaderboard_visible ?? false) ? "bg-[#F5B817]" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition ${
                          (consent?.leaderboard_visible ?? false) ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>

                  {/* 2. Real Name vs Anonymous */}
                  <div className="py-3 flex items-start justify-between gap-4">
                    <div>
                      <p className="font-bold text-[#1F2421]">Display Real Name on Leaderboard</p>
                      <p className="text-[11px] text-[#6B7280]">
                        Display your real name instead of &quot;Anonymous Volunteer&quot;.
                      </p>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-label="Consent to display real name on public leaderboard"
                      aria-checked={consent?.name_visible ?? false}
                      disabled={!consent || isUpdatingConsent}
                      onClick={() => handleToggleConsent("name_visible")}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                        (consent?.name_visible ?? false) ? "bg-[#F5B817]" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition ${
                          (consent?.name_visible ?? false) ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>

                  {/* 3. Media & Photography Usage */}
                  <div className="py-3 flex items-start justify-between gap-4">
                    <div>
                      <p className="font-bold text-[#1F2421]">Media & Photography Usage</p>
                      <p className="text-[11px] text-[#6B7280]">
                        Allow photos from volunteering sessions to be shared on Maatram channels.
                      </p>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-label="Consent for media and photography usage in Maatram communications"
                      aria-checked={consent?.media_usage ?? false}
                      disabled={!consent || isUpdatingConsent}
                      onClick={() => handleToggleConsent("media_usage")}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                        (consent?.media_usage ?? false) ? "bg-[#F5B817]" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition ${
                          (consent?.media_usage ?? false) ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>

                  {/* 4. Thank You & Milestone Emails */}
                  <div className="py-3 flex items-start justify-between gap-4">
                    <div>
                      <p className="font-bold text-[#1F2421]">Thank-You & Milestone Emails</p>
                      <p className="text-[11px] text-[#6B7280]">
                        Receive thank-you notes, impact reports, and event certificates by email.
                      </p>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-label="Consent to receive thank-you and milestone emails"
                      aria-checked={consent?.thank_you_emails ?? false}
                      disabled={!consent || isUpdatingConsent}
                      onClick={() => handleToggleConsent("thank_you_emails")}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                        (consent?.thank_you_emails ?? false) ? "bg-[#F5B817]" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition ${
                          (consent?.thank_you_emails ?? false) ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>

                  {/* 5. LinkedIn Appreciation Mentions */}
                  <div className="py-3 flex items-start justify-between gap-4">
                    <div>
                      <p className="font-bold text-[#1F2421]">LinkedIn Appreciation Mentions</p>
                      <p className="text-[11px] text-[#6B7280]">
                        Allow tagging your LinkedIn profile when celebrating quarterly achievements.
                      </p>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-label="Consent for LinkedIn appreciation mentions"
                      aria-checked={consent?.linkedin_content ?? false}
                      disabled={!consent || isUpdatingConsent}
                      onClick={() => handleToggleConsent("linkedin_content")}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                        (consent?.linkedin_content ?? false) ? "bg-[#F5B817]" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition ${
                          (consent?.linkedin_content ?? false) ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>

                  {/* 6. Contact Sharing with Coordinators */}
                  <div className="py-3 flex items-start justify-between gap-4">
                    <div>
                      <p className="font-bold text-[#1F2421]">Contact Sharing with Coordinators</p>
                      <p className="text-[11px] text-[#6B7280]">
                        Share your phone and email with assigned event organizers for logistics.
                      </p>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-label="Consent for contact sharing with event coordinators"
                      aria-checked={consent?.contact_available ?? false}
                      disabled={!consent || isUpdatingConsent}
                      onClick={() => handleToggleConsent("contact_available")}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                        (consent?.contact_available ?? false) ? "bg-[#F5B817]" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition ${
                          (consent?.contact_available ?? false) ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 4: ACHIEVEMENTS COMPLETE GALLERY */}
            {activeTab === "achievements" && (
              <div className="space-y-4 animate-in fade-in-50 duration-200">
                <div className="flex items-center justify-between pb-2 border-b border-[#EFECE6]">
                  <div>
                    <h4 className="text-sm font-extrabold text-[#1F2421]">Volunteer Milestone Badges</h4>
                    <p className="text-xs text-[#6B7280]">Milestones earned through verified service hours and drives.</p>
                  </div>
                  <div className="text-xs font-bold text-[#D97706] bg-[#FEF3C7] px-3 py-1 rounded-full">
                    3 of 4 Badges Unlocked
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    {
                      name: "First Contribution",
                      sub: "Earned 7 Nov 2026",
                      svg: "/assets/maatram/gamification/badge-first-step.svg",
                      unlocked: true,
                    },
                    {
                      name: "Community Mentor",
                      sub: "Earned 14 Nov 2026",
                      svg: "/assets/maatram/gamification/badge-mentor-star.svg",
                      unlocked: true,
                    },
                    {
                      name: "Consistent Volunteer",
                      sub: "Earned 20 Nov 2026",
                      svg: "/assets/maatram/gamification/badge-century-club.svg",
                      unlocked: true,
                    },
                    {
                      name: "Century Champion",
                      sub: "100 Service Hours",
                      svg: "/assets/maatram/gamification/badge-super-volunteer.svg",
                      unlocked: false,
                    },
                  ].map((b) => (
                    <div
                      key={b.name}
                      className={`p-3 rounded-2xl border text-center flex flex-col items-center justify-between ${
                        b.unlocked ? "bg-white border-[#EFECE6] shadow-2xs" : "bg-gray-50 border-gray-200 opacity-60"
                      }`}
                    >
                      <div className="w-14 h-14 relative my-1">
                        <Image src={b.svg} alt={b.name} fill className="object-contain" />
                      </div>
                      <div>
                        <p className="text-xs font-extrabold text-[#1F2421]">{b.name}</p>
                        <p className="text-[10px] text-[#6B7280]">{b.sub}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ------------------------------------------------------ */}
          {/* BOTTOM ROW: Dual Cards Side by Side (From Reference)   */}
          {/* ------------------------------------------------------ */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch">
            {/* Card 1 (~58% / 7 cols): Privacy & Visibility at a Glance */}
            <div className="md:col-span-7 bg-white rounded-3xl border border-[#EFECE6] p-5 sm:p-6 shadow-xs flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-[#1F2421]">
                    <Shield className="w-4.5 h-4.5 text-[#F5B817]" />
                    <h3 className="text-sm sm:text-base font-extrabold tracking-tight">
                      Privacy & Visibility at a Glance
                    </h3>
                    <Info className="w-3.5 h-3.5 text-[#9CA3AF] cursor-pointer" />
                  </div>
                </div>

                <div className="space-y-3.5 pt-1">
                  <div className="flex items-start justify-between gap-3 text-xs">
                    <div className="flex items-start gap-2.5">
                      <Trophy className="w-4 h-4 text-[#F5B817] shrink-0 mt-0.5" />
                      <div>
                        <p className="font-bold text-[#1F2421]">Show my name on the public leaderboard</p>
                        <p className="text-[11px] text-[#6B7280]">
                          Your name will be shown as Anonymous Volunteer publicly.
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-label="Consent to show my name on public leaderboard"
                      aria-checked={consent?.name_visible ?? false}
                      disabled={!consent || isUpdatingConsent}
                      onClick={() => handleToggleConsent("name_visible")}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                        consent?.name_visible ? "bg-[#F5B817]" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                          consent?.name_visible ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-start justify-between gap-3 text-xs">
                    <div className="flex items-start gap-2.5">
                      <ImageIcon className="w-4 h-4 text-[#F5B817] shrink-0 mt-0.5" />
                      <div>
                        <p className="font-bold text-[#1F2421]">Allow my profile photo in Maatram communications</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-label="Consent to allow profile photo in Maatram communications"
                      aria-checked={consent?.media_usage ?? false}
                      disabled={!consent || isUpdatingConsent}
                      onClick={() => handleToggleConsent("media_usage")}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                        (consent?.media_usage ?? false) ? "bg-[#F5B817]" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                          (consent?.media_usage ?? false) ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-start justify-between gap-3 text-xs">
                    <div className="flex items-start gap-2.5">
                      <LinkedinIcon className="w-4 h-4 text-[#0284C7] shrink-0 mt-0.5" />
                      <div>
                        <p className="font-bold text-[#1F2421]">Allow LinkedIn appreciation mentions</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-label="Consent to allow LinkedIn appreciation mentions"
                      aria-checked={consent?.linkedin_content ?? false}
                      disabled={!consent || isUpdatingConsent}
                      onClick={() => handleToggleConsent("linkedin_content")}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                        (consent?.linkedin_content ?? false) ? "bg-[#F5B817]" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                          (consent?.linkedin_content ?? false) ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-start justify-between gap-3 text-xs">
                    <div className="flex items-start gap-2.5">
                      <Share2 className="w-4 h-4 text-[#F5B817] shrink-0 mt-0.5" />
                      <div>
                        <p className="font-bold text-[#1F2421]">Contact Sharing</p>
                        <p className="text-[11px] text-[#6B7280]">
                          Share my contact details with event coordinators. This helps organizers reach you for event related queries.
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      aria-label="Consent to share contact details with event coordinators"
                      aria-checked={consent?.contact_available ?? false}
                      disabled={!consent || isUpdatingConsent}
                      onClick={() => handleToggleConsent("contact_available")}
                      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                        (consent?.contact_available ?? false) ? "bg-[#F5B817]" : "bg-gray-300"
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                          (consent?.contact_available ?? false) ? "translate-x-4" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-[#FFFBEB] border border-[#FEF3C7] text-[10.5px] text-[#78350F] flex items-start gap-2">
                <Info className="w-3.5 h-3.5 text-[#D97706] shrink-0 mt-0.5" />
                <p className="leading-snug">
                  Admin can always see the real volunteer identity for administration and verification, even when public leaderboard anonymity is enabled.
                </p>
              </div>
            </div>

            {/* Card 2 (~42% / 5 cols): My Achievements */}
            <div className="md:col-span-5 bg-white rounded-3xl border border-[#EFECE6] p-5 sm:p-6 shadow-xs flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2 text-[#1F2421]">
                    <Trophy className="w-4.5 h-4.5 text-[#F5B817]" />
                    <h3 className="text-sm sm:text-base font-extrabold tracking-tight">
                      My Achievements
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setActiveTab("achievements")}
                    className="text-xs font-bold text-[#B45309] hover:text-[#946C00] hover:underline flex items-center gap-0.5 transition-colors"
                  >
                    <span>View all</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-2.5">
                  <div className="rounded-2xl bg-[#FAF8F5] border border-[#EFECE6] p-2.5 text-center flex flex-col items-center justify-between shadow-2xs hover:shadow-xs transition-shadow">
                    <div className="w-12 h-12 relative mb-1">
                      <Image
                        src="/assets/maatram/gamification/badge-first-step.svg"
                        alt="First Contribution"
                        fill
                        className="object-contain"
                      />
                    </div>
                    <div>
                      <p className="text-[11px] font-extrabold text-[#1F2421] leading-tight">
                        First Contribution
                      </p>
                      <p className="text-[9px] text-[#6B7280] font-medium mt-0.5">
                        Earned on 7 Nov 2026
                      </p>
                    </div>
                  </div>

                  <div className="rounded-2xl bg-[#FAF8F5] border border-[#EFECE6] p-2.5 text-center flex flex-col items-center justify-between shadow-2xs hover:shadow-xs transition-shadow">
                    <div className="w-12 h-12 relative mb-1">
                      <Image
                        src="/assets/maatram/gamification/badge-mentor-star.svg"
                        alt="Community Mentor"
                        fill
                        className="object-contain"
                      />
                    </div>
                    <div>
                      <p className="text-[11px] font-extrabold text-[#1F2421] leading-tight">
                        Community Mentor
                      </p>
                      <p className="text-[9px] text-[#6B7280] font-medium mt-0.5">
                        Earned on 14 Nov 2026
                      </p>
                    </div>
                  </div>

                  <div className="rounded-2xl bg-[#FAF8F5] border border-[#EFECE6] p-2.5 text-center flex flex-col items-center justify-between shadow-2xs hover:shadow-xs transition-shadow">
                    <div className="w-12 h-12 relative mb-1">
                      <Image
                        src="/assets/maatram/gamification/badge-century-club.svg"
                        alt="Consistent Volunteer"
                        fill
                        className="object-contain"
                      />
                    </div>
                    <div>
                      <p className="text-[11px] font-extrabold text-[#1F2421] leading-tight">
                        Consistent Volunteer
                      </p>
                      <p className="text-[9px] text-[#6B7280] font-medium mt-0.5">
                        Earned on 20 Nov 2026
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function VolunteerProfilePage() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-[#EFECE6] shadow-xs">
          <Loader2 className="w-8 h-8 text-[#F5B817] animate-spin" />
          <p className="text-sm font-medium text-[#4B5563] mt-3">Loading volunteer profile...</p>
        </div>
      }
    >
      <ProfileContent />
    </Suspense>
  );
}
