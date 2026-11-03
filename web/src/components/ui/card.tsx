import React from "react";
import { cn } from "@/lib/utils";

export function Card({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "bg-white rounded-2xl border border-[#EBE6DD] p-6 shadow-sm hover:shadow-md transition-shadow",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("flex flex-col space-y-1.5 pb-4", className)} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn("text-lg font-semibold text-[#1F2421] tracking-tight", className)}
      {...props}
    >
      {children}
    </h3>
  );
}

export function CardDescription({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("text-sm text-[#6B7280]", className)} {...props}>
      {children}
    </p>
  );
}

export function CardContent({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("pt-0", className)} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("flex items-center pt-4 border-t border-[#EBE6DD]/60", className)} {...props}>
      {children}
    </div>
  );
}

interface KpiCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  subtitle?: string;
  trend?: string;
  trendPositive?: boolean;
  className?: string;
}

/**
 * Standard KPI Metric Card for Volunteer & Admin Dashboards
 */
export function KpiCard({
  title,
  value,
  icon,
  subtitle,
  trend,
  trendPositive,
  className,
}: KpiCardProps) {
  return (
    <Card className={cn("p-5 flex flex-col justify-between", className)}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#6B7280]">
          {title}
        </span>
        {icon && (
          <div className="w-9 h-9 rounded-xl bg-[#FFF8E7] text-[#946C00] flex items-center justify-center">
            {icon}
          </div>
        )}
      </div>

      <div className="my-3">
        <span className="text-3xl font-bold text-[#1F2421] tracking-tight">
          {value}
        </span>
      </div>

      <div className="flex items-center justify-between text-xs text-[#6B7280]">
        {subtitle && <span>{subtitle}</span>}
        {trend && (
          <span
            className={cn(
              "font-medium",
              trendPositive ? "text-[#03543F]" : "text-[#9B1C1C]"
            )}
          >
            {trend}
          </span>
        )}
      </div>
    </Card>
  );
}

