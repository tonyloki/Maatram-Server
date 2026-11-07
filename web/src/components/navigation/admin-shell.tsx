"use client";

import React, { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import {
  Menu,
  X,
  Bell,
  ShieldAlert,
  ArrowLeft,
  ShieldCheck,
} from "lucide-react";
import { AdminSidebar } from "@/components/navigation/admin-sidebar";
import { Logo } from "@/components/ui/logo";
import { useAuth } from "@/lib/auth-context";

export function AdminShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isAuthenticated, isLoading } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Authentication check
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(`/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [isLoading, isAuthenticated, router, pathname]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF8F3]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-3 border-charcoal-900 border-t-[#F5B817] rounded-full animate-spin" />
          <p className="text-sm font-bold text-charcoal-700">Verifying Administrative Credentials...</p>
        </div>
      </div>
    );
  }

  // RBAC check: Only ADMIN and SUPER_ADMIN allowed
  const isAuthorizedAdmin = user?.role === "ADMIN" || user?.role === "SUPER_ADMIN";

  if (!isAuthorizedAdmin) {
    return (
      <div className="min-h-screen bg-[#FAF8F3] flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-3xl border border-red-200 p-8 text-center shadow-lg space-y-4">
          <div className="w-14 h-14 bg-red-100 rounded-2xl flex items-center justify-center mx-auto text-red-600">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-charcoal-950">Administrative Access Denied</h2>
          <p className="text-sm text-charcoal-600 leading-relaxed">
            Your authenticated account (<span className="font-semibold text-charcoal-900">{user?.email}</span>) does not
            have permission to access the Administrative Operations Portal.
          </p>
          <div className="pt-2">
            <Link
              href="/volunteer/dashboard"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-charcoal-900 hover:bg-charcoal-800 text-white font-bold text-sm shadow-xs transition-colors"
            >
              <ArrowLeft className="w-4 h-4" /> Go to Volunteer Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAF8F3] text-charcoal-900 flex flex-col md:flex-row antialiased selection:bg-[#F5B817]/30">
      {/* Desktop Fixed Dark Sidebar Rail */}
      <div className="hidden md:block w-64 lg:w-72 flex-shrink-0">
        <div className="fixed top-0 bottom-0 w-64 lg:w-72 h-screen z-30">
          <AdminSidebar />
        </div>
      </div>

      {/* Main Content Workspace */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Top Header */}
        <header className="md:hidden sticky top-0 z-40 bg-[#16171A] border-b border-charcoal-800 px-4 py-3 flex items-center justify-between text-white shadow-md">
          <Logo width={100} height={45} href="/admin/dashboard" />
          <div className="flex items-center gap-2">
            <Link
              href="/admin/operations"
              className="p-2 rounded-xl text-charcoal-300 hover:bg-charcoal-800 transition-colors"
              title="Operations"
            >
              <Bell className="w-5 h-5" />
            </Link>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl text-charcoal-300 hover:bg-charcoal-800 transition-colors"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </header>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-50 md:hidden bg-charcoal-950/60 backdrop-blur-xs flex">
            <div className="w-72 max-w-[80vw] h-full bg-[#16171A] shadow-2xl flex flex-col">
              <div className="p-4 border-b border-charcoal-800 flex items-center justify-between text-white">
                <Logo width={100} height={45} href="/admin/dashboard" />
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1.5 rounded-lg text-charcoal-400 hover:bg-charcoal-800"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto">
                <AdminSidebar onNavigate={() => setMobileMenuOpen(false)} />
              </div>
            </div>
            <div className="flex-1" onClick={() => setMobileMenuOpen(false)} />
          </div>
        )}

        {/* Desktop Top Workspace Bar */}
        <header className="hidden md:flex sticky top-0 z-20 h-16 bg-[#FAF8F3]/90 backdrop-blur-md border-b border-charcoal-200/60 px-6 lg:px-10 items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold text-charcoal-500 uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4 text-[#F5B817]" />
            Administrative Operations & Governance
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/admin/operations"
              className="relative p-2 rounded-xl text-charcoal-600 hover:text-charcoal-950 hover:bg-charcoal-100/70 transition-colors"
              title="Transactional Outbox & Operations"
            >
              <Bell className="w-5 h-5" />
            </Link>

            <div className="h-6 w-px bg-charcoal-200" />

            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-[#16171A] text-[#F5B817] font-black text-xs flex items-center justify-center border border-charcoal-800 shadow-2xs">
                {user?.email ? user.email.slice(0, 2).toUpperCase() : "AD"}
              </div>
              <span className="text-xs font-bold text-charcoal-900">
                {user?.email?.split("@")[0] || "Administrator"}
              </span>
              <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full bg-charcoal-900 text-[#F5B817]">
                {user?.role || "ADMIN"}
              </span>
            </div>
          </div>
        </header>

        {/* Page Inner Container */}
        <main id="main-content" tabIndex={-1} className="flex-1 p-4 md:p-6 lg:p-10 focus:outline-none">{children}</main>
      </div>
    </div>
  );
}

