"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface SwitchProps {
  id?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  size?: "sm" | "md";
  className?: string;
}

/**
 * Standard Accessible Switch Primitive
 */
export function Switch({
  id,
  checked,
  onChange,
  disabled = false,
  size = "md",
  className,
}: SwitchProps) {
  const sizeStyles = {
    sm: "h-5 w-9",
    md: "h-6 w-11",
  };

  const thumbSizeStyles = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
  };

  const thumbTranslateStyles = {
    sm: checked ? "translate-x-4" : "translate-x-0.5",
    md: checked ? "translate-x-5" : "translate-x-0.5",
  };

  return (
    <button
      id={id}
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={cn(
        "relative inline-flex flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#F5B817] focus-visible:ring-offset-2",
        sizeStyles[size],
        checked ? "bg-[#F5B817]" : "bg-[#D1D5DB]",
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
    >
      <span
        aria-hidden="true"
        className={cn(
          "pointer-events-none inline-block transform rounded-full bg-white shadow-xs ring-0 transition duration-200 ease-in-out",
          thumbSizeStyles[size],
          thumbTranslateStyles[size]
        )}
      />
    </button>
  );
}

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
 * Implements strict affirmative privacy toggling with explicit plain-language descriptions.
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
        "flex items-start justify-between gap-4 p-4 rounded-xl border border-[#EFECE6] bg-white transition-all hover:border-[#E5E0D8]",
        disabled && "opacity-60 pointer-events-none",
        className
      )}
    >
      <div className="flex flex-col space-y-1 pr-2">
        <label htmlFor={switchId} className="text-sm font-bold text-[#1F2421] cursor-pointer">
          {switchTitle}
        </label>
        <p className="text-xs text-[#4B5563] leading-relaxed">{description}</p>
      </div>

      <Switch
        id={switchId}
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        className="mt-0.5"
      />
    </div>
  );
}
