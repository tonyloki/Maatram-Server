import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "success" | "warning" | "error" | "attention" | "neutral" | "brand";
  size?: "sm" | "md";
}

export function Badge({
  className,
  variant = "neutral",
  size = "md",
  children,
  ...props
}: BadgeProps) {
  const baseStyles =
    "inline-flex items-center justify-center font-medium rounded-full border transition-colors select-none";

  const variantStyles = {
    success: "bg-[#DEF7EC] text-[#03543F] border-[#BCF0DA]",
    warning: "bg-[#FEF08A] text-[#854D0E] border-[#FDE047]",
    error: "bg-[#FDE8E8] text-[#9B1C1C] border-[#F8B4B4]",
    attention: "bg-[#FFEDD5] text-[#9A3412] border-[#FDBA74]",
    neutral: "bg-[#F3F4F6] text-[#374151] border-[#E5E7EB]",
    brand: "bg-[#FFF8E7] text-[#946C00] border-[#F5B817]/30 font-semibold",
  };

  const sizeStyles = {
    sm: "text-[11px] px-2.5 py-0.5",
    md: "text-xs px-3 py-1",
  };

  return (
    <span className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)} {...props}>
      {children}
    </span>
  );
}

