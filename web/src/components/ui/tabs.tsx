"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  badge?: string | number;
}

export interface SegmentedTabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

/**
 * Segmented Pill Tabs (Directly Matching Mentor Reference 4: My Activity & Reference 5: Leaderboard)
 */
export function SegmentedTabs({
  tabs,
  activeTab,
  onChange,
  className,
}: SegmentedTabsProps) {
  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    let targetIndex = -1;
    if (e.key === "ArrowRight") {
      targetIndex = (index + 1) % tabs.length;
    } else if (e.key === "ArrowLeft") {
      targetIndex = (index - 1 + tabs.length) % tabs.length;
    } else if (e.key === "Home") {
      targetIndex = 0;
    } else if (e.key === "End") {
      targetIndex = tabs.length - 1;
    }
    if (targetIndex !== -1) {
      e.preventDefault();
      onChange(tabs[targetIndex].id);
      const buttons = (e.currentTarget.parentElement as HTMLElement)?.querySelectorAll<HTMLButtonElement>('[role="tab"]');
      buttons?.[targetIndex]?.focus();
    }
  };

  return (
    <div
      role="tablist"
      aria-orientation="horizontal"
      className={cn("flex flex-wrap items-center gap-2", className)}
    >
      {tabs.map((tab, idx) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            role="tab"
            aria-selected={isActive}
            aria-controls={`panel-${tab.id}`}
            tabIndex={isActive ? 0 : -1}
            onClick={() => onChange(tab.id)}
            onKeyDown={(e) => handleKeyDown(e, idx)}
            className={cn(
              "inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs md:text-sm font-semibold transition-all duration-150 cursor-pointer select-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#F5B817] focus-visible:ring-offset-2",
              isActive
                ? "bg-[#F5B817] text-[#1F2421] shadow-xs"
                : "bg-white text-[#4B5563] border border-[#E5E7EB] hover:bg-[#FAF8F5] hover:text-[#1F2421]"
            )}
          >
            {tab.icon && <span className="shrink-0">{tab.icon}</span>}
            <span>{tab.label}</span>
            {tab.badge !== undefined && (
              <span
                className={cn(
                  "text-[10px] font-bold px-1.5 py-0.2 rounded-full",
                  isActive ? "bg-white/40 text-[#1F2421]" : "bg-stone-100 text-[#4B5563]"
                )}
              >
                {tab.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export interface UnderlineTabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

/**
 * Underline Tabs (Directly Matching Mentor Reference 6: Profile Panels)
 */
export function UnderlineTabs({
  tabs,
  activeTab,
  onChange,
  className,
}: UnderlineTabsProps) {
  const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
    let targetIndex = -1;
    if (e.key === "ArrowRight") {
      targetIndex = (index + 1) % tabs.length;
    } else if (e.key === "ArrowLeft") {
      targetIndex = (index - 1 + tabs.length) % tabs.length;
    } else if (e.key === "Home") {
      targetIndex = 0;
    } else if (e.key === "End") {
      targetIndex = tabs.length - 1;
    }
    if (targetIndex !== -1) {
      e.preventDefault();
      onChange(tabs[targetIndex].id);
      const buttons = (e.currentTarget.parentElement as HTMLElement)?.querySelectorAll<HTMLButtonElement>('[role="tab"]');
      buttons?.[targetIndex]?.focus();
    }
  };

  return (
    <div
      role="tablist"
      aria-orientation="horizontal"
      className={cn("flex items-center gap-6 border-b border-[#EFECE6] overflow-x-auto", className)}
    >
      {tabs.map((tab, idx) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            role="tab"
            aria-selected={isActive}
            aria-controls={`panel-${tab.id}`}
            tabIndex={isActive ? 0 : -1}
            onClick={() => onChange(tab.id)}
            onKeyDown={(e) => handleKeyDown(e, idx)}
            className={cn(
              "inline-flex items-center gap-2 py-3 text-sm font-semibold transition-all cursor-pointer select-none border-b-2 whitespace-nowrap focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#F5B817] focus-visible:ring-offset-2",
              isActive
                ? "border-[#F5B817] text-[#1F2421] font-bold"
                : "border-transparent text-[#6B7280] hover:text-[#1F2421] hover:border-[#D1D5DB]"
            )}
          >
            {tab.icon && <span className="shrink-0">{tab.icon}</span>}
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
}

