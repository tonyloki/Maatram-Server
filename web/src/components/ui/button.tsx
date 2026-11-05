"use client";

import React, { forwardRef } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "destructive" | "gold";
  size?: "sm" | "md" | "lg";
  rounded?: "full" | "xl" | "lg";
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      rounded = "full",
      isLoading = false,
      disabled,
      leftIcon,
      rightIcon,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-semibold transition-all duration-150 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98] cursor-pointer select-none group";

    const roundedStyles = {
      full: "rounded-full",
      xl: "rounded-xl",
      lg: "rounded-lg",
    };

    const variantStyles = {
      primary:
        "bg-[#F5B817] text-[#1F2421] hover:bg-[#E5A800] active:bg-[#C99200] hover:-translate-y-0.5 active:translate-y-0 focus-visible:ring-[#F5B817] shadow-xs hover:shadow-sm",
      gold:
        "bg-[#F5B817] text-[#1F2421] hover:bg-[#E5A800] active:bg-[#C99200] hover:-translate-y-0.5 active:translate-y-0 focus-visible:ring-[#F5B817] shadow-xs hover:shadow-sm",
      secondary:
        "bg-[#FFF8E7] text-[#946C00] border border-[#F5B817]/40 hover:bg-[#FEF08A] active:bg-[#FDE047] focus-visible:ring-[#F5B817]",
      outline:
        "bg-white text-[#1F2421] border border-[#EFECE6] hover:bg-[#FAF8F5] hover:border-[#E5E0D8] hover:-translate-y-0.5 active:translate-y-0 focus-visible:ring-[#F5B817] shadow-xs",
      ghost:
        "bg-transparent text-[#4B5563] hover:text-[#1F2421] hover:bg-stone-200/50 focus-visible:ring-[#F5B817]",
      destructive:
        "bg-white text-[#9B1C1C] border border-[#F8B4B4] hover:bg-[#FDE8E8] active:bg-[#FCD2D2] focus-visible:ring-[#9B1C1C] shadow-xs",
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
        className={cn(baseStyles, roundedStyles[rounded], variantStyles[variant], sizeStyles[size], className)}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin text-current" />
        ) : (
          leftIcon && <span className="shrink-0">{leftIcon}</span>
        )}
        <span>{children}</span>
        {!isLoading && rightIcon && (
          <span className="shrink-0 transition-transform duration-150 group-hover:translate-x-0.5">
            {rightIcon}
          </span>
        )}
      </button>
    );
  }
);

Button.displayName = "Button";
