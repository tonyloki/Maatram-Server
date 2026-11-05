import React from "react";
import { cn } from "@/lib/utils";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  interactive?: boolean;
  rounded?: "xl" | "2xl" | "3xl";
}

export function Card({
  className,
  interactive = false,
  rounded = "2xl",
  children,
  ...props
}: CardProps) {
  const roundedStyles = {
    xl: "rounded-xl",
    "2xl": "rounded-2xl",
    "3xl": "rounded-3xl",
  };

  return (
    <div
      className={cn(
        "bg-white border border-[#EFECE6] p-6 shadow-xs transition-all duration-200",
        roundedStyles[rounded],
        interactive && "hover:-translate-y-0.5 hover:shadow-sm hover:border-[#E5E0D8] cursor-pointer",
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
      className={cn("text-lg font-bold text-[#1F2421] tracking-tight", className)}
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
    <p className={cn("text-sm text-[#4B5563] leading-relaxed", className)} {...props}>
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
    <div className={cn("flex items-center pt-4 border-t border-[#EFECE6]", className)} {...props}>
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
        <span className="text-xs font-bold uppercase tracking-wider text-[#4B5563]">
          {title}
        </span>
        {icon && (
          <div className="w-10 h-10 rounded-2xl bg-[#FFF8E7] text-[#946C00] flex items-center justify-center shrink-0">
            {icon}
          </div>
        )}
      </div>

      <div className="my-3">
        <span className="text-3xl font-bold text-[#1F2421] tracking-tight">
          {value}
        </span>
      </div>

      <div className="flex items-center justify-between text-xs text-[#4B5563]">
        {subtitle && <span>{subtitle}</span>}
        {trend && (
          <span
            className={cn(
              "font-semibold",
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
