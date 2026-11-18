"use client";

import React, { Suspense, useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Clock,
  ShieldCheck,
  Mail,
  Home,
  HelpCircle,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  LogOut,
  ArrowRight,
  User,
  GraduationCap,
  Calendar,
  Building2,
} from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import { ApplicationDetailResponse } from "@/types";

function ApplicationStatusContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, refreshUser, logout, isAuthenticated, isLoading: authLoading } = useAuth();

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [rejectionReason, setRejectionReason] = useState<string | null>(null);
  const [applicationData, setApplicationData] = useState<ApplicationDetailResponse | null>(null);

  // Status resolution
  const userStatus = user?.status || searchParams.get("status") || "PENDING_APPROVAL";
  const isApproved = userStatus === "APPROVED";
  const isRejected = userStatus === "REJECTED";
  const isPending = !isApproved && !isRejected;

  // Identity resolution
  const email = user?.email || searchParams.get("email") || "your registered email";
  const name =
    (user?.email ? user.email.split("@")[0] : null) ||
    searchParams.get("name") ||
    "Volunteer";

  // Load detailed application review if available
  const loadApplicationDetails = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const data = await apiClient<ApplicationDetailResponse>("/applications/me", {
        skipCache: true,
      });
      setApplicationData(data);
      if (data?.reviews && data.reviews.length > 0) {
        const latestReject = data.reviews
          .slice()
          .reverse()
          .find((r) => r.action === "REJECTED" && r.reason);
        if (latestReject?.reason) {
          setRejectionReason(latestReject.reason);
        }
      }
    } catch {
      // Non-blocking: fallback to generic status display
    }
  }, [isAuthenticated]);

  useEffect(() => {
    void loadApplicationDetails();
  }, [loadApplicationDetails]);

  // Interactive Live Status Refresh
  const handleRefreshStatus = async () => {
    setIsRefreshing(true);
    try {
      await refreshUser();
      await loadApplicationDetails();
      const me = await apiClient<{ user?: { status: string }; status?: string }>("/users/me", {
        skipCache: true,
      });
      const latestStatus = me.user?.status || me.status;
      if (latestStatus === "APPROVED") {
        router.push("/volunteer/dashboard");
      }
    } catch {
      // Non-blocking
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      router.push("/login");
    } catch {
      router.push("/login");
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <Card className="p-8 sm:p-10 bg-white border-[#EBE6DD] shadow-xl rounded-3xl space-y-8 text-center animate-in fade-in-50 duration-300">
        {/* ========================================================= */}
        {/* CASE A: APPROVED STATUS                                   */}
        {/* ========================================================= */}
        {isApproved && (
          <>
            <div className="relative mx-auto w-20 h-20 rounded-full bg-emerald-50 border-2 border-emerald-500 flex items-center justify-center shadow-md">
              <CheckCircle2 className="w-10 h-10 text-emerald-600" />
            </div>

            <div className="space-y-3">
              <Badge variant="success" className="px-3.5 py-1 text-xs font-bold tracking-wide uppercase">
                Application Status: Approved
              </Badge>
              <h1 className="text-2xl sm:text-3xl font-black text-[#1F2421]">
                Welcome to Maatram, {name}!
              </h1>
              <p className="text-sm text-[#4B5563] max-w-lg mx-auto leading-relaxed">
                Your volunteer application has been approved by the Maatram team. You now have full access to explore upcoming events, attend drives, and earn contribution points.
              </p>
            </div>

            <div className="pt-2 flex justify-center">
              <Link href="/volunteer/dashboard">
                <Button variant="primary" size="lg" className="text-sm font-bold gap-2">
                  <span>Go to Volunteer Dashboard</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </>
        )}

        {/* ========================================================= */}
        {/* CASE B: REJECTED STATUS                                   */}
        {/* ========================================================= */}
        {isRejected && (
          <>
            <div className="relative mx-auto w-20 h-20 flex items-center justify-center">
              <div className="relative w-20 h-20 rounded-full bg-gradient-to-tr from-[#FEE2E2] to-[#FEF2F2] border-2 border-[#EF4444] flex items-center justify-center shadow-md">
                <XCircle className="w-10 h-10 text-[#DC2626]" />
              </div>
            </div>

            <div className="space-y-3">
              <Badge variant="error" className="px-3.5 py-1 text-xs font-bold tracking-wide uppercase">
                Application Status: Not Accepted
              </Badge>
              <h1 className="text-2xl sm:text-3xl font-black text-[#1F2421]">
                Application Update for {name}
              </h1>
              <p className="text-sm text-[#4B5563] max-w-lg mx-auto leading-relaxed">
                Thank you for your interest in volunteering with the <span className="font-bold text-[#1F2421]">Maatram Foundation</span>. Following administrative review, we regret to inform you that we are unable to accept your application at this time.
              </p>
            </div>

            {/* Official Administrative Reason */}
            <div className="bg-[#FEF2F2] border border-[#FCA5A5] rounded-2xl p-6 text-left space-y-3">
              <h2 className="text-xs font-black uppercase tracking-wider text-[#991B1B] flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-[#DC2626]" />
                Administrative Feedback / Reason
              </h2>
              <p className="text-xs sm:text-sm text-[#7F1D1D] leading-relaxed font-medium bg-white/70 p-3.5 rounded-xl border border-[#F87171]/40">
                &ldquo;{rejectionReason || "Application did not meet our verification criteria or cohort quota requirements at this time."}&rdquo;
              </p>
            </div>
          </>
        )}

        {/* ========================================================= */}
        {/* CASE C: PENDING STATUS (DEFAULT FOR UNAPPROVED VOLUNTEER)  */}
        {/* ========================================================= */}
        {isPending && (
          <>
            {/* Animated Status Pulse Badge */}
            <div className="relative mx-auto w-20 h-20 flex items-center justify-center">
              <div className="absolute inset-0 rounded-full bg-[#FEF3C7] animate-ping opacity-25" />
              <div className="relative w-20 h-20 rounded-full bg-gradient-to-tr from-[#FDE68A] to-[#FEF3C7] border-2 border-[#F5B817] flex items-center justify-center shadow-md">
                <Clock className="w-10 h-10 text-[#B45309]" />
              </div>
            </div>

            {/* Heading & Context */}
            <div className="space-y-3">
              <Badge variant="warning" className="px-3.5 py-1 text-xs font-bold tracking-wide uppercase">
                Application Status: Pending Approval
              </Badge>
              <h1 className="text-2xl sm:text-3xl font-black text-[#1F2421]">
                Welcome, {name}!
              </h1>
              <p className="text-sm text-[#4B5563] max-w-lg mx-auto leading-relaxed">
                Thank you for registering with the <span className="font-bold text-[#1F2421]">Maatram Foundation</span> volunteering community. Our team will review your application and approve it within 2 days.
              </p>
            </div>

            {/* Review Stages Progress Card */}
            <div className="bg-[#FAF8F3] border border-[#EFECE6] rounded-2xl p-6 text-left space-y-4">
              <h2 className="text-xs font-black uppercase tracking-wider text-[#6B7280] flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-[#F5B817]" />
                Application Review Steps
              </h2>

              <div className="space-y-3.5 text-xs text-[#374151]">
                {/* Step 1: Registration Completed */}
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 font-black text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                    ✓
                  </div>
                  <div>
                    <p className="font-bold text-[#1F2421]">Registration Submitted</p>
                    <p className="text-[#6B7280]">Your details and volunteer preferences have been successfully recorded.</p>
                  </div>
                </div>

                {/* Step 2: Under Review */}
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full bg-[#FEF3C7] text-[#92400E] font-black text-[10px] flex items-center justify-center shrink-0 mt-0.5 animate-pulse">
                    2
                  </div>
                  <div>
                    <p className="font-bold text-[#1F2421]">Administrative Review (In Progress)</p>
                    <p className="text-[#6B7280]">Our coordinator team reviews your profile information, category eligibility, and background suitability.</p>
                  </div>
                </div>

                {/* Step 3: Approval & Unlocking */}
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full bg-stone-200 text-stone-600 font-black text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                    3
                  </div>
                  <div>
                    <p className="font-bold text-[#1F2421]">Decision & Dashboard Access</p>
                    <p className="text-[#6B7280]">
                      You will receive an official confirmation email at <span className="font-semibold text-[#1F2421]">{email}</span> once approved. Full event registrations and dashboard features unlock automatically.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Support Callout */}
            <div className="p-4 rounded-xl bg-[#FFFBEB] border border-[#FDE68A] text-xs text-[#92400E] flex flex-col sm:flex-row items-center justify-between gap-3 text-left">
              <div className="flex items-center gap-2.5">
                <HelpCircle className="w-4 h-4 text-[#D97706] shrink-0" />
                <span>Have an urgent question regarding your application status?</span>
              </div>
              <a
                href="mailto:volunteers@maatramfoundation.org"
                className="font-bold text-[#B45309] hover:underline flex items-center gap-1 shrink-0"
              >
                <Mail className="w-3.5 h-3.5" />
                Contact Team
              </a>
            </div>
          </>
        )}

        {/* ========================================================= */}
        {/* Navigation & Action Controls                               */}
        {/* ========================================================= */}
        <div className="pt-2 flex flex-col sm:flex-row gap-3 justify-center">
          {isAuthenticated && (
            <Button
              variant="outline"
              size="md"
              onClick={handleRefreshStatus}
              disabled={isRefreshing}
              className="w-full sm:w-auto text-xs font-bold gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
              {isRefreshing ? "Checking Status..." : "Refresh Status"}
            </Button>
          )}

          <Link href="/" className="w-full sm:w-auto">
            <Button variant="outline" size="md" className="w-full text-xs font-bold gap-2">
              <Home className="w-4 h-4" />
              Return to Home
            </Button>
          </Link>

          {isAuthenticated ? (
            <Button
              variant="secondary"
              size="md"
              onClick={handleLogout}
              className="w-full sm:w-auto text-xs font-bold gap-2 text-stone-700 hover:text-stone-900"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </Button>
          ) : (
            <Link href="/login" className="w-full sm:w-auto">
              <Button variant="primary" size="md" className="w-full text-xs font-bold gap-2">
                Sign In
              </Button>
            </Link>
          )}
        </div>
      </Card>
    </div>
  );
}

export default function ApplicationStatusPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="volunteer" />
      <main className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <Suspense
          fallback={
            <div className="w-full max-w-xl bg-white rounded-3xl p-10 border border-[#EBE6DD] animate-pulse space-y-4 text-center">
              <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto" />
              <div className="h-6 bg-gray-200 rounded w-1/2 mx-auto" />
              <div className="h-4 bg-gray-100 rounded w-3/4 mx-auto" />
            </div>
          }
        >
          <ApplicationStatusContent />
        </Suspense>
      </main>
      <PublicFooter />
    </div>
  );
}
