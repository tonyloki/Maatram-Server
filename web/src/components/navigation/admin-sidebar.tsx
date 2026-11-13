"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  UserCheck,
  Users,
  CalendarDays,
  Clock,
  BarChart3,
  Send,
  ScrollText,
  Settings,
  LogOut,
  ShieldCheck,
} from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";

const ADMIN_NAV_ITEMS = [
  {
    label: "Dashboard",
    href: "/admin/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Volunteers",
    href: "/admin/volunteers",
    icon: Users,
  },
  {
    label: "Manage Events",
    href: "/admin/events",
    icon: CalendarDays,
  },
  {
    label: "Audit Logs",
    href: "/admin/audit-logs",
    icon: ScrollText,
  },
  {
    label: "Settings",
    href: "/admin/settings",
    icon: Settings,
  },
];

interface AdminSidebarProps {
  onNavigate?: () => void;
  className?: string;
  adminName?: string;
  adminRole?: string;
}

export function AdminSidebar({
  onNavigate,
  className,
  adminName,
  adminRole,
}: AdminSidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    if (onNavigate) onNavigate();
    await logout();
  };

  const displayName = adminName || (user?.email ? user.email.split("@")[0] : "Administrator");
  const displayRole = adminRole || user?.role || "ADMIN";
  const displayInitials = displayName.slice(0, 2).toUpperCase();

  return (
    <aside
      className={cn(
        "w-full h-full bg-[#16171A] text-white flex flex-col justify-between border-r border-charcoal-800 shadow-xl select-none min-h-screen",
        className
      )}
    >
      {/* Top Section: Brand Header & Navigation Items */}
      <div className="flex flex-col flex-1 min-h-0">
        {/* Brand Header */}
        <div className="p-6 border-b border-charcoal-800/80 flex flex-col gap-1.5">
          <div className="flex items-center gap-3">
            <div className="bg-white rounded-xl px-2.5 py-1.5 inline-flex items-center justify-center shadow-xs">
              <Logo width={110} height={45} href="/admin/dashboard" priority unoptimized />
            </div>
          </div>
          <div className="flex items-center gap-2 pt-1">
            <span className="text-xs font-black uppercase tracking-wider text-[#F5B817] flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              Admin Portal
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-charcoal-800 text-charcoal-300 border border-charcoal-700">
              {displayRole}
            </span>
          </div>
        </div>

        {/* Navigation Rail */}
        <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto scrollbar-thin scrollbar-thumb-charcoal-800">
          {ADMIN_NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== "/admin/dashboard" && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onNavigate}
                className={`flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  isActive
                    ? "bg-[#F5B817] text-charcoal-950 font-bold shadow-md shadow-[#F5B817]/10"
                    : "text-charcoal-300 hover:text-white hover:bg-charcoal-800/60"
                }`}
              >
                <Icon
                  className={`w-5 h-5 flex-shrink-0 transition-colors ${
                    isActive ? "text-charcoal-950" : "text-charcoal-400 group-hover:text-white"
                  }`}
                />
                <span className="truncate">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Section: Current Administrator Info & Logout */}
      <div className="p-4 border-t border-charcoal-800/80 bg-charcoal-950/40">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-full bg-[#F5B817]/20 border border-[#F5B817]/40 text-[#F5B817] font-bold text-xs flex items-center justify-center flex-shrink-0">
              {displayInitials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-white truncate">
                {displayName}
              </p>
              <p className="text-[10px] text-charcoal-400 uppercase tracking-wider font-semibold">
                {displayRole}
              </p>
            </div>
          </div>

          <button
            onClick={handleLogout}
            title="Sign out of Admin Portal"
            className="p-2 rounded-xl text-charcoal-400 hover:text-red-400 hover:bg-charcoal-800/80 transition-colors"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
