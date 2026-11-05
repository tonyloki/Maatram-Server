import React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

export interface AvatarProps {
  src?: string | null;
  alt?: string;
  fallback: string;
  size?: "sm" | "md" | "lg" | "xl";
  status?: "online" | "offline" | "verified";
  className?: string;
}

export function Avatar({
  src,
  alt = "Avatar",
  fallback,
  size = "md",
  status,
  className,
}: AvatarProps) {
  const sizeStyles = {
    sm: "w-8 h-8 text-xs",
    md: "w-10 h-10 text-sm",
    lg: "w-14 h-14 text-base font-bold",
    xl: "w-20 h-20 text-xl font-bold",
  };

  const statusSizeStyles = {
    sm: "w-2 h-2 ring-1",
    md: "w-2.5 h-2.5 ring-2",
    lg: "w-3.5 h-3.5 ring-2",
    xl: "w-4 h-4 ring-2",
  };

  const statusColorStyles = {
    online: "bg-[#16A34A]",
    offline: "bg-[#9CA3AF]",
    verified: "bg-[#F5B817]",
  };

  const initials = fallback.slice(0, 2).toUpperCase();

  return (
    <div className={cn("relative inline-block shrink-0", className)}>
      <div
        className={cn(
          "rounded-full flex items-center justify-center overflow-hidden border border-[#EFECE6] bg-[#FFF8E7] text-[#946C00] font-bold select-none",
          sizeStyles[size]
        )}
      >
        {src ? (
          <Image
            src={src}
            alt={alt}
            width={80}
            height={80}
            className="w-full h-full object-cover"
          />
        ) : (
          <span>{initials}</span>
        )}
      </div>

      {status && (
        <span
          className={cn(
            "absolute bottom-0 right-0 rounded-full ring-white",
            statusSizeStyles[size],
            statusColorStyles[status]
          )}
        />
      )}
    </div>
  );
}

