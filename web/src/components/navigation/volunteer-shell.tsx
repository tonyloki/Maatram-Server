"use client";

import React, { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import {
  Menu,
  X,
  Bell,
  Clock,
  Ban,
  ArrowRight,
  ChevronDown,
} from "lucide-react";
import { VolunteerSidebar } from "@/components/navigation/volunteer-sidebar";
import { Logo } from "@/components/ui/logo";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import { UnreadCountResponse, VolunteerProfileResponse } from "@/types";

export function VolunteerShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, isLoading } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [profile, setProfile] = useState<VolunteerProfileResponse | null>(null);

  // Authentication check
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(`/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [isLoading, isAuthenticated, router, pathname]);

  // Fetch unread count & volunteer profile for topbar
  useEffect(() => {
    let isMounted = true;
    async function loadShellData() {
      if (!isAuthenticated) return;
      try {
        const [unreadData, profileData] = await Promise.allSettled([
          apiClient<UnreadCountResponse>("/notifications/unread-count"),
          apiClient<VolunteerProfileResponse>("/volunteers/me"),
        ]);
        if (isMounted) {
          if (unreadData.status === "fulfilled") {
            setUnreadCount(unreadData.value.unread_count || 0);
          }
          if (profileData.status === "fulfilled") {
            setProfile(profileData.value);
          }
        }
      } catch {
        // Silently fail
      }
    }
    void loadShellData();
    return () => {
      isMounted = false;
    };
  }, [isAuthenticated, pathname]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF8F5]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-3 border-[#F5B817] border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium text-[#4B5563]">Loading Maatram Volunteer Portal...</p>
        </div>
      </div>
    );
  }

  const isPendingApproval =
    user?.status === "PENDING_APPROVAL" || user?.status === "PENDING_VERIFICATION";
  const isRejected = user?.status === "REJECTED";
  const isSuspended = user?.status === "SUSPENDED" || user?.status === "INACTIVE";

  const displayName = profile
    ? `${profile.first_name} ${profile.last_name}`.trim()
    : user?.email?.split("@")[0] || "Volunteer";

  const initials = profile?.first_name
    ? `${profile.first_name.charAt(0)}${profile.last_name ? profile.last_name.charAt(0) : ""}`.toUpperCase()
    : user?.email?.slice(0, 2).toUpperCase() || "VL";

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-[#1F2421] flex flex-col md:flex-row antialiased selection:bg-[#FDE68A]">
      {/* Desktop Sidebar Rail with Floating Card Presentation matching Mentor Reference */}
      <div className="hidden md:block w-60 lg:w-64 flex-shrink-0 p-3">
        <div className="fixed top-3 bottom-3 w-[calc(15rem-1.5rem)] lg:w-[calc(16rem-1.5rem)] h-[calc(100vh-1.5rem)] z-30">
          <VolunteerSidebar />
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 md:pl-0">
        {/* Mobile Header */}
        <header className="md:hidden sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-[#EFECE6] px-4 py-3 flex items-center justify-between shadow-2xs">
          <Logo width={115} height={48} />
          <div className="flex items-center gap-2">
            <Link
              href="/volunteer/notifications"
              className="relative p-2 rounded-xl text-[#4B5563] hover:bg-[#FAF8F5] transition-colors"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-600 ring-2 ring-white" />
              )}
            </Link>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl text-[#4B5563] hover:bg-[#FAF8F5] transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </header>

        {/* Mobile Slide-over Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-50 md:hidden bg-black/40 backdrop-blur-xs flex">
            <div className="w-72 max-w-[85vw] h-full bg-white shadow-2xl flex flex-col p-3">
              <div className="p-2 border-b border-[#EFECE6] flex items-center justify-between">
                <Logo width={115} height={48} />
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1.5 rounded-lg text-[#6B7280] hover:bg-[#FAF8F5]"
                  aria-label="Close menu"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto pt-2">
                <VolunteerSidebar onNavigate={() => setMobileMenuOpen(false)} />
              </div>
            </div>
            <div className="flex-1" onClick={() => setMobileMenuOpen(false)} />
          </div>
        )}

        {/* Desktop Top Header Bar matching Mentor Reference */}
        <header className="hidden md:flex sticky top-0 z-20 h-14 bg-[#FAF8F5]/90 backdrop-blur-md border-b border-[#EFECE6] px-6 lg:px-8 items-center justify-between">
          <div className="text-xs font-bold text-[#6B7280] uppercase tracking-wider">
            MAATRAM VOLUNTEERING & MENTORSHIP PORTAL
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/volunteer/notifications"
              className="relative p-2 rounded-xl text-[#4B5563] hover:text-[#1F2421] hover:bg-white transition-colors"
              title="Notifications"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 min-w-4 h-4 px-1 rounded-full bg-red-600 text-[10px] font-bold text-white flex items-center justify-center ring-2 ring-white">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </Link>

            <div className="h-5 w-px bg-[#EFECE6]" />

            {/* Profile Avatar Pill matching Reference */}
            <Link
              href="/volunteer/profile"
              className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-[#EFECE6] hover:border-[#F5B817] shadow-2xs hover:shadow-xs transition-all group"
            >
              <div className="w-7 h-7 rounded-full bg-[#FFF8E7] text-[#946C00] border border-[#F5B817]/60 font-extrabold text-[11px] flex items-center justify-center shrink-0">
                {initials}
              </div>
              <span className="text-xs font-bold text-[#1F2421] group-hover:text-[#946C00] transition-colors truncate max-w-[130px]">
                {displayName}
              </span>
              <ChevronDown className="w-3.5 h-3.5 text-[#9CA3AF] group-hover:text-[#1F2421]" />
            </Link>
          </div>
        </header>

        {/* Status Notification Banners for Inactive/Pending/Suspended Profiles */}
        {isPendingApproval && (
          <div className="bg-[#FEF3C7] border-b border-[#FDE68A] px-4 py-3 text-[#78350F] text-xs md:text-sm font-medium flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#D97706] flex-shrink-0" />
              <span>
                <strong>Application In Review:</strong> Your volunteer application is being reviewed by Maatram administrators. You can browse upcoming opportunities while verification is in progress.
              </span>
            </div>
            <Link
              href="/volunteer/profile"
              className="hidden sm:inline-flex items-center gap-1 font-bold text-[#92400E] underline hover:no-underline ml-4 whitespace-nowrap"
            >
              View Application Status <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        )}

        {isRejected && (
          <div className="bg-red-50 border-b border-red-200 px-4 py-3 text-red-900 text-xs md:text-sm font-medium flex items-center gap-2">
            <Ban className="w-4 h-4 text-red-600 flex-shrink-0" />
            <span>
              <strong>Application Status:</strong> Your volunteering profile was not approved. For questions or to re-apply, please contact volunteers@maatramfoundation.org.
            </span>
          </div>
        )}

        {isSuspended && (
          <div className="bg-red-50 border-b border-red-200 px-4 py-3 text-red-900 text-xs md:text-sm font-medium flex items-center gap-2">
            <Ban className="w-4 h-4 text-red-600 flex-shrink-0" />
            <span>
              <strong>Account Inactive:</strong> Your volunteer account is currently suspended. Please contact the administrator desk.
            </span>
          </div>
        )}

        {/* Page Inner Container matching Reference proportions */}
        <main id="main-content" tabIndex={-1} className="flex-1 p-4 sm:p-5 lg:p-6 w-full max-w-[1260px] mx-auto focus:outline-none">{children}</main>
      </div>
    </div>
  );
}
