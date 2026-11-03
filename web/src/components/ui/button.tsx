"use client";

import React, { forwardRef } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "outline" | "ghost" | "destructive";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      isLoading = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium rounded-full transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98] cursor-pointer select-none";

    const variantStyles = {
      primary:
        "bg-[#F5B817] text-[#1F2421] font-semibold hover:bg-[#E5A800] focus:ring-[#F5B817] shadow-sm",
      outline:
        "bg-white text-[#1F2421] border border-[#EBE6DD] hover:bg-[#FAF8F3] hover:border-[#D8D2C6] focus:ring-[#F5B817] shadow-sm",
      ghost:
        "bg-transparent text-[#6B7280] hover:text-[#1F2421] hover:bg-black/5 focus:ring-[#F5B817]",
      destructive:
        "bg-white text-[#9B1C1C] border border-[#F8B4B4] hover:bg-[#FDE8E8] focus:ring-[#9B1C1C] shadow-sm",
    };

    const sizeStyles = {
      sm: "text-xs px-3.5 py-1.5 gap-1.5 h-8",
      md: "text-sm px-5 py-2.5 gap-2 h-10",
      lg: "text-base px-6 py-3 gap-2.5 h-12",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
        {...props}
      >
        {isLoading && <Loader2 className="w-4 h-4 animate-spin text-current" />}
        <span>{children}</span>
      </button>
    );
  }
);

Button.displayName = "Button";

