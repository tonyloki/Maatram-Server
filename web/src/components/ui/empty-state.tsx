import React from "react";
import { cn } from "@/lib/utils";

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: React.ReactNode;
  illustration?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({
  icon,
  illustration,
  title,
  description,
  action,
  className,
  ...props
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center text-center p-8 md:p-12 max-w-md mx-auto",
        className
      )}
      {...props}
    >
      {illustration ? (
        <div className="mb-6 flex items-center justify-center">{illustration}</div>
      ) : icon ? (
        <div className="w-16 h-16 rounded-3xl bg-[#FFF8E7] text-[#946C00] flex items-center justify-center mb-5 shadow-xs">
          {icon}
        </div>
      ) : null}

      <h3 className="text-xl font-bold text-[#1F2421] tracking-tight">{title}</h3>
      <p className="text-sm text-[#4B5563] mt-2 mb-6 leading-relaxed max-w-sm">
        {description}
      </p>

      {action && <div className="flex items-center justify-center">{action}</div>}
    </div>
  );
}

