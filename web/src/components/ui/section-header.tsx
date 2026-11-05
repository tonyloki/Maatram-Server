import React from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SectionHeaderProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  actionHref?: string;
  actionLabel?: string;
  actionOnClick?: () => void;
  className?: string;
}

export function SectionHeader({
  icon,
  title,
  description,
  actionHref,
  actionLabel,
  actionOnClick,
  className,
}: SectionHeaderProps) {
  return (
    <div className={cn("flex flex-wrap items-center justify-between gap-3 mb-4", className)}>
      <div className="flex items-center gap-2.5">
        {icon && <span className="text-[#946C00] shrink-0">{icon}</span>}
        <div>
          <h2 className="text-lg md:text-xl font-bold text-[#1F2421] tracking-tight">
            {title}
          </h2>
          {description && (
            <p className="text-xs text-[#4B5563] mt-0.5 leading-relaxed">{description}</p>
          )}
        </div>
      </div>

      {actionLabel && (
        <div>
          {actionHref ? (
            <Link
              href={actionHref}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#946C00] hover:text-[#78350F] hover:underline transition-colors"
            >
              <span>{actionLabel}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          ) : actionOnClick ? (
            <button
              type="button"
              onClick={actionOnClick}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#946C00] hover:text-[#78350F] hover:underline transition-colors cursor-pointer"
            >
              <span>{actionLabel}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : null}
        </div>
      )}
    </div>
  );
}

