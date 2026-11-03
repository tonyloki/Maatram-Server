"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Compass,
  CalendarCheck,
  Trophy,
  User,
  Bell,
  LogOut,
} from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import { UnreadCountResponse } from "@/types";

interface VolunteerSidebarProps {
  className?: string;
  onNavigate?: () => void;
}

export function VolunteerSidebar({ className, onNavigate }: VolunteerSidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState<number>(0);

  useEffect(() => {
    let isMounted = true;
    async function fetchUnread() {
      try {
        const data = await apiClient<UnreadCountResponse>("/notifications/unread-count");
        if (isMounted) {
          setUnreadCount(data.unread_count || 0);
        }
      } catch {
        // Silently fail if unauthenticated or offline
      }
    }
    void fetchUnread();
    return () => {
      isMounted = false;
    };
  }, [pathname]);

  const navItems = [
    { label: "Dashboard", href: "/volunteer/dashboard", icon: Home },
    { label: "Discover Events", href: "/volunteer/events", icon: Compass },
    { label: "My Activity", href: "/volunteer/activity", icon: CalendarCheck },
    { label: "Leaderboard", href: "/volunteer/leaderboard", icon: Trophy },
    { label: "My Profile", href: "/volunteer/profile", icon: User },
    {
      label: "Notifications",
      href: "/volunteer/notifications",
      icon: Bell,
      badge: unreadCount > 0 ? unreadCount : undefined,
    },
  ];

  const userInitial = user?.email?.charAt(0).toUpperCase() || "V";

  return (
    <aside
      className={cn(
        "w-64 flex-shrink-0 flex flex-col justify-between border-r border-[#EBE6DD] bg-[#FAF8F3] p-4 min-h-screen",
        className
      )}
    >
      <div>
        {/* Brand Logo Container */}
        <div className="flex items-center px-3 py-4 mb-4">
          <Logo href="/volunteer/dashboard" width={130} height={55} priority />
        </div>

        {/* Navigation Rail */}
        <nav className="flex flex-col space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== "/volunteer/dashboard" && pathname.startsWith(`${item.href}`));

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onNavigate}
                className={cn(
                  "flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all group",
                  isActive
                    ? "bg-[#FFF8E7] text-[#946C00] font-semibold border-l-4 border-[#F5B817] shadow-xs"
                    : "text-[#6B7280] hover:text-[#1F2421] hover:bg-white/80"
                )}
              >
                <div className="flex items-center gap-3.5">
                  <Icon
                    className={cn(
                      "w-5 h-5 transition-colors",
                      isActive ? "text-[#946C00]" : "text-[#9CA3AF] group-hover:text-[#1F2421]"
                    )}
                  />
                  <span>{item.label}</span>
                </div>

                {item.badge !== undefined && (
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#B45309] text-white">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom User Account Menu & Support */}
      <div className="space-y-3 pt-4 border-t border-[#EBE6DD]">
        {/* User Card */}
        {user && (
          <div className="flex items-center justify-between p-3 rounded-2xl bg-white border border-[#EBE6DD] shadow-xs">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="w-9 h-9 rounded-full bg-[#FFF8E7] border border-[#F5B817]/40 text-[#946C00] font-bold text-sm flex items-center justify-center shrink-0">
                {userInitial}
              </div>
              <div className="overflow-hidden text-left">
                <p className="text-xs font-bold text-[#1F2421] truncate">{user.email}</p>
                <span className="inline-block text-[10px] font-semibold text-[#15803D] uppercase">
                  {user.role}
                </span>
              </div>
            </div>

            <button
              type="button"
              onClick={() => logout()}
              title="Sign Out"
              className="p-1.5 rounded-lg text-[#9CA3AF] hover:text-[#DC2626] hover:bg-red-50 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Support Help Chip */}
        <div className="px-3.5 py-2.5 bg-white/60 rounded-xl border border-[#EBE6DD] text-[11px] text-[#6B7280]">
          <span className="font-semibold text-[#1F2421] block">Volunteer Helpdesk</span>
          <a
            href="mailto:volunteers@maatramfoundation.org"
            className="text-[#946C00] font-medium hover:underline inline-block mt-0.5"
          >
            volunteers@maatramfoundation.org
          </a>
        </div>
      </div>
    </aside>
  );
}
