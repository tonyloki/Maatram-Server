"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { LogOut, Headphones } from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import { apiClient } from "@/lib/api-client";
import { UnreadCountResponse, VolunteerProfileResponse } from "@/types";

interface VolunteerSidebarProps {
  className?: string;
  onNavigate?: () => void;
}

export function VolunteerSidebar({ className, onNavigate }: VolunteerSidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [profile, setProfile] = useState<VolunteerProfileResponse | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
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
        // Silently fail if unauthenticated or offline
      }
    }
    void loadData();
    return () => {
      isMounted = false;
    };
  }, [pathname]);

  const navItems = [
    {
      label: "Dashboard",
      href: "/volunteer/dashboard",
      iconSrc: "/assets/maatram/icons/nav-dashboard.svg",
    },
    {
      label: "Discover Events",
      href: "/volunteer/events",
      iconSrc: "/assets/maatram/icons/nav-discover.svg",
    },
    {
      label: "My Activity",
      href: "/volunteer/activity",
      iconSrc: "/assets/maatram/icons/nav-activity.svg",
    },
    {
      label: "Leaderboard",
      href: "/volunteer/leaderboard",
      iconSrc: "/assets/maatram/icons/nav-leaderboard.svg",
    },
    {
      label: "My Profile",
      href: "/volunteer/profile",
      iconSrc: "/assets/maatram/icons/nav-profile.svg",
    },
    {
      label: "Notifications",
      href: "/volunteer/notifications",
      iconSrc: "/assets/maatram/icons/nav-notifications.svg",
      badge: unreadCount > 0 ? unreadCount : undefined,
    },
  ];

  const displayName = profile
    ? `${profile.first_name} ${profile.last_name}`.trim()
    : user?.email?.split("@")[0] || "Volunteer";

  const userInitial = profile?.first_name
    ? profile.first_name.charAt(0).toUpperCase()
    : user?.email?.charAt(0).toUpperCase() || "V";

  const volunteerCategory = profile?.category || user?.role || "VOLUNTEER";

  return (
    <aside
      className={cn(
        "h-full flex flex-col justify-between bg-white rounded-2xl lg:rounded-3xl border border-[#EFECE6] p-4 lg:p-5 shadow-xs relative overflow-hidden",
        className
      )}
    >
      {/* Decorative Wheat Stalks Watermark */}
      <div className="absolute -bottom-6 -right-6 w-32 h-48 pointer-events-none opacity-[0.14] select-none z-0">
        <Image
          src="/assets/maatram/decorations/wheat-stalks.svg"
          alt=""
          width={128}
          height={192}
          className="w-full h-full object-contain"
        />
      </div>

      <div className="relative z-10">
        {/* Brand Logo Container */}
        <div className="flex items-center px-2 py-3 mb-4">
          <Logo href="/volunteer/dashboard" width={135} height={56} priority />
        </div>

        {/* Navigation Rail */}
        <nav className="flex flex-col space-y-1.5" aria-label="Volunteer Portal Navigation">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/volunteer/dashboard" && pathname.startsWith(`${item.href}`));

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onNavigate}
                className={cn(
                  "flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group",
                  isActive
                    ? "bg-[#FFF8E7] text-[#946C00] font-bold shadow-2xs"
                    : "text-[#4B5563] hover:text-[#1F2421] hover:bg-[#FAF8F5]"
                )}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={cn(
                      "w-5 h-5 flex items-center justify-center shrink-0 transition-opacity",
                      isActive ? "opacity-100" : "opacity-70 group-hover:opacity-100"
                    )}
                  >
                    <Image
                      src={item.iconSrc}
                      alt=""
                      width={20}
                      height={20}
                      className="w-5 h-5 object-contain"
                    />
                  </span>
                  <span className="truncate">{item.label}</span>
                </div>

                {item.badge !== undefined && (
                  <span className="text-[11px] font-extrabold px-2 py-0.5 rounded-full bg-[#EF4444] text-white shadow-2xs">
                    {item.badge > 9 ? "9+" : item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Section: User Identity Card & Volunteer Helpdesk */}
      <div className="relative z-10 space-y-3 pt-4 border-t border-[#EFECE6]">
        {/* On Profile page, render user identity card; on other portal pages, render reference "Together for a Better Tomorrow" card */}
        {pathname !== "/volunteer/profile" ? (
          <div className="p-4 rounded-2xl bg-[#FFF9EA] border border-[#FDE68A] shadow-2xs text-center flex flex-col items-center">
            <div className="w-16 h-16 relative mb-2">
              <Image
                src="/assets/maatram/illustrations/together-heart.svg"
                alt="Together for a Better Tomorrow"
                width={64}
                height={64}
                className="w-full h-full object-contain"
              />
            </div>
            <p className="font-serif italic font-extrabold text-sm text-[#1F2421] leading-tight">
              Together<br />for a Better<br />Tomorrow
            </p>
          </div>
        ) : (
          /* User Profile Card */
          user && (
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-[#FAF8F5] border border-[#EFECE6]/80">
              <Link
                href="/volunteer/profile"
                onClick={onNavigate}
                className="flex items-center gap-2.5 overflow-hidden group flex-1 mr-2"
                title="View Profile"
              >
                <div className="w-9 h-9 rounded-full bg-[#FFF8E7] border border-[#F5B817]/60 text-[#946C00] font-extrabold text-xs flex items-center justify-center shrink-0 shadow-2xs group-hover:scale-105 transition-transform">
                  {userInitial}
                </div>
                <div className="overflow-hidden text-left">
                  <p className="text-xs font-bold text-[#1F2421] truncate group-hover:text-[#946C00] transition-colors">
                    {displayName}
                  </p>
                  <span className="inline-block text-[10px] font-semibold text-[#15803D] uppercase tracking-wider">
                    {volunteerCategory}
                  </span>
                </div>
              </Link>

              <button
                type="button"
                onClick={() => logout()}
                title="Sign Out"
                className="p-1.5 rounded-lg text-[#9CA3AF] hover:text-[#DC2626] hover:bg-red-50 transition-colors shrink-0"
                aria-label="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )
        )}

        {/* Volunteer Helpdesk Support Chip */}
        <div className="px-3 py-2.5 bg-white rounded-xl border border-[#EFECE6] text-[11px] text-[#6B7280]">
          <div className="flex items-center gap-1.5 text-[#1F2421] font-semibold">
            <Headphones className="w-3.5 h-3.5 text-[#F5B817]" />
            <span>Volunteer Helpdesk</span>
          </div>
          <a
            href="mailto:volunteers@maatramfoundation.org"
            className="text-[#946C00] font-medium hover:underline block truncate mt-1"
          >
            volunteers@maatramfoundation.org
          </a>
        </div>
      </div>
    </aside>
  );
}
