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
} from "lucide-react";
import { VolunteerSidebar } from "@/components/navigation/volunteer-sidebar";
import { Logo } from "@/components/ui/logo";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import { UnreadCountResponse } from "@/types";

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

  // Authentication check
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(`/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [isLoading, isAuthenticated, router, pathname]);

  // Fetch unread count for topbar
  useEffect(() => {
    let isMounted = true;
    async function loadUnread() {
      if (!isAuthenticated) return;
      try {
        const data = await apiClient<UnreadCountResponse>("/notifications/unread-count");
        if (isMounted) {
          setUnreadCount(data.unread_count || 0);
        }
      } catch {
        // Silently fail
      }
    }
    void loadUnread();
    return () => {
      isMounted = false;
    };
  }, [isAuthenticated, pathname]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF8F3]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-3 border-primary-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium text-charcoal-600">Loading Maatram Volunteer Portal...</p>
        </div>
      </div>
    );
  }

  const isPendingApproval = user?.status === "PENDING_APPROVAL" || user?.status === "PENDING_VERIFICATION";
  const isRejected = user?.status === "REJECTED";
  const isSuspended = user?.status === "SUSPENDED" || user?.status === "INACTIVE";

  return (
    <div className="min-h-screen bg-[#FAF8F3] text-charcoal-900 flex flex-col md:flex-row antialiased selection:bg-primary-200">
      {/* Desktop Sidebar Rail */}
      <div className="hidden md:block w-64 lg:w-72 flex-shrink-0">
        <div className="fixed top-0 bottom-0 w-64 lg:w-72 h-screen z-30">
          <VolunteerSidebar />
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 md:pl-0">
        {/* Mobile Header */}
        <header className="md:hidden sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-charcoal-200/80 px-4 py-3 flex items-center justify-between shadow-2xs">
          <Logo width={110} height={55} />
          <div className="flex items-center gap-2">
            <Link
              href="/volunteer/notifications"
              className="relative p-2 rounded-xl text-charcoal-700 hover:bg-charcoal-100 transition-colors"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-600 ring-2 ring-white" />
              )}
            </Link>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl text-charcoal-700 hover:bg-charcoal-100 transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </header>

        {/* Mobile Slide-over Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-50 md:hidden bg-charcoal-950/40 backdrop-blur-xs flex">
            <div className="w-72 max-w-[80vw] h-full bg-white shadow-2xl flex flex-col">
              <div className="p-4 border-b border-charcoal-100 flex items-center justify-between">
                <Logo width={110} height={55} />
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1.5 rounded-lg text-charcoal-500 hover:bg-charcoal-100"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto">
                <VolunteerSidebar onNavigate={() => setMobileMenuOpen(false)} />
              </div>
            </div>
            <div className="flex-1" onClick={() => setMobileMenuOpen(false)} />
          </div>
        )}

        {/* Desktop Top Header Bar */}
        <header className="hidden md:flex sticky top-0 z-20 h-16 bg-[#FAF8F3]/90 backdrop-blur-md border-b border-charcoal-200/60 px-6 lg:px-10 items-center justify-between">
          <div className="text-xs font-semibold text-charcoal-400 uppercase tracking-wider">
            Maatram Volunteering & Mentorship Portal
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/volunteer/notifications"
              className="relative p-2 rounded-xl text-charcoal-600 hover:text-charcoal-950 hover:bg-charcoal-100/70 transition-colors"
              title="Notifications"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 min-w-4 h-4 px-1 rounded-full bg-red-600 text-[10px] font-bold text-white flex items-center justify-center ring-2 ring-white">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </Link>
            <div className="h-6 w-px bg-charcoal-200" />
            <Link
              href="/volunteer/profile"
              className="flex items-center gap-2.5 p-1 rounded-full hover:bg-charcoal-100/70 transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-primary-100 text-primary-900 border border-primary-300 font-bold text-xs flex items-center justify-center">
                {user?.email ? user.email.slice(0, 2).toUpperCase() : "VL"}
              </div>
              <span className="text-xs font-bold text-charcoal-800 pr-2">
                {user?.email?.split("@")[0] || "Volunteer"}
              </span>
            </Link>
          </div>
        </header>

        {/* Status Notification Banners for Inactive/Pending/Suspended Profiles */}
        {isPendingApproval && (
          <div className="bg-amber-50 border-b border-amber-200 px-4 py-3 text-amber-900 text-xs md:text-sm font-medium flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-600 flex-shrink-0" />
              <span>
                <strong>Application In Review:</strong> Your volunteer application is being reviewed by Maatram administrators. You can browse upcoming events while your verification is in progress.
              </span>
            </div>
            <Link
              href="/volunteer/profile"
              className="hidden sm:inline-flex items-center gap-1 font-bold text-amber-900 underline hover:no-underline ml-4 whitespace-nowrap"
            >
              View Application Status <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        )}

        {isRejected && (
          <div className="bg-red-50 border-b border-red-200 px-4 py-3 text-red-900 text-xs md:text-sm font-medium flex items-center gap-2">
            <Ban className="w-4 h-4 text-red-600 flex-shrink-0" />
            <span>
              <strong>Application Status:</strong> Your volunteering profile was not approved. For questions or to re-apply, please contact support@maatramfoundation.org.
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

        {/* Page Inner Container */}
        <main className="flex-1 p-4 md:p-6 lg:p-10">{children}</main>
      </div>
    </div>
  );
}
