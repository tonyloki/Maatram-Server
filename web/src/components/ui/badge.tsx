import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?:
    | "success"
    | "warning"
    | "error"
    | "attention"
    | "neutral"
    | "brand"
    | "onsite"
    | "online"
    | "school-visit"
    | "mock-interview"
    | "bgv"
    | "admissions"
    | "panel";
  size?: "sm" | "md";
  dot?: boolean;
}

export function Badge({
  className,
  variant = "neutral",
  size = "md",
  dot = false,
  children,
  ...props
}: BadgeProps) {
  const baseStyles =
    "inline-flex items-center justify-center font-semibold rounded-full border transition-colors select-none";

  const variantStyles = {
    // Semantic Status
    success: "bg-[#DEF7EC] text-[#03543F] border-[#BCF0DA]",
    warning: "bg-[#FEF08A] text-[#854D0E] border-[#FDE047]",
    error: "bg-[#FDE8E8] text-[#9B1C1C] border-[#F8B4B4]",
    attention: "bg-[#FFEDD5] text-[#9A3412] border-[#FDBA74]",
    neutral: "bg-[#F3F4F6] text-[#374151] border-[#E5E7EB]",
    brand: "bg-[#FFF8E7] text-[#946C00] border-[#F5B817]/40",

    // Delivery Format & Event Categories (Directly Sampled from Mentor References)
    onsite: "bg-[#DCFCE7] text-[#166534] border-[#BBF7D0]",
    online: "bg-[#E0F2FE] text-[#0369A1] border-[#BAE6FD]",
    "school-visit": "bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]",
    "mock-interview": "bg-[#E0F2FE] text-[#0369A1] border-[#BAE6FD]",
    bgv: "bg-[#EDE9FE] text-[#6D28D9] border-[#DDD6FE]",
    admissions: "bg-[#FFEDD5] text-[#C2410C] border-[#FED7AA]",
    panel: "bg-[#CCFBF1] text-[#0F766E] border-[#99F6E4]",
  };

  const dotColorStyles = {
    success: "bg-[#03543F]",
    warning: "bg-[#854D0E]",
    error: "bg-[#9B1C1C]",
    attention: "bg-[#9A3412]",
    neutral: "bg-[#6B7280]",
    brand: "bg-[#946C00]",
    onsite: "bg-[#166534]",
    online: "bg-[#0369A1]",
    "school-visit": "bg-[#92400E]",
    "mock-interview": "bg-[#0369A1]",
    bgv: "bg-[#6D28D9]",
    admissions: "bg-[#C2410C]",
    panel: "bg-[#0F766E]",
  };

  const sizeStyles = {
    sm: "text-[11px] px-2.5 py-0.5 gap-1.5",
    md: "text-xs px-3 py-1 gap-1.5",
  };

  return (
    <span className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)} {...props}>
      {dot && <span className={cn("w-1.5 h-1.5 rounded-full shrink-0", dotColorStyles[variant])} />}
      <span>{children}</span>
    </span>
  );
}
