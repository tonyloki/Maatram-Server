"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface ConsentSwitchProps {
  id?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  title?: string;
  label?: string;
  description: string;
  disabled?: boolean;
  className?: string;
}

/**
 * Granular Affirmative Consent Switch Component.
 * Implements strict affirmative privacy toggling (Module 4) with explicit plain-language descriptions.
 */
export function ConsentSwitch({
  id,
  checked,
  onChange,
  title,
  label,
  description,
  disabled = false,
  className,
}: ConsentSwitchProps) {
  const switchTitle = title || label || "";
  const switchId = id || `switch-${switchTitle.toLowerCase().replace(/[^a-z0-9]/g, "-")}`;

  return (
    <div
      className={cn(
        "flex items-start justify-between gap-4 p-4 rounded-xl border border-[#EBE6DD] bg-white transition-all hover:border-[#D8D2C6]",
        disabled && "opacity-60 pointer-events-none",
        className
      )}
    >
      <div className="flex flex-col space-y-1 pr-2">
        <label htmlFor={switchId} className="text-sm font-semibold text-[#1F2421] cursor-pointer">
          {switchTitle}
        </label>
        <p className="text-xs text-[#6B7280] leading-relaxed">{description}</p>
      </div>

      <button
        id={switchId}
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={cn(
          "relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:ring-offset-2",
          checked ? "bg-[#F5B817]" : "bg-[#E5E7EB]"
        )}
      >
        <span
          aria-hidden="true"
          className={cn(
            "pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out",
            checked ? "translate-x-5" : "translate-x-0"
          )}
        />
      </button>
    </div>
  );
}

