import React from "react";
import { cn } from "@/lib/utils";

export function Table({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLTableElement>) {
  return (
    <div className="w-full overflow-x-auto">
      <table
        className={cn("w-full text-left border-collapse text-sm", className)}
        {...props}
      >
        {children}
      </table>
    </div>
  );
}

export function TableHeader({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <thead
      className={cn("border-b border-[#EFECE6] bg-[#FAF8F5]/80", className)}
      {...props}
    >
      {children}
    </thead>
  );
}

export function TableBody({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <tbody className={cn("divide-y divide-[#EFECE6] bg-white", className)} {...props}>
      {children}
    </tbody>
  );
}

export function TableRow({
  className,
  highlight = false,
  children,
  ...props
}: React.HTMLAttributes<HTMLTableRowElement> & { highlight?: boolean }) {
  return (
    <tr
      className={cn(
        "transition-colors hover:bg-[#FAF8F5]",
        highlight && "bg-[#FEF9C3]/60 hover:bg-[#FEF9C3]/80",
        className
      )}
      {...props}
    >
      {children}
    </tr>
  );
}

export function TableHead({
  className,
  children,
  ...props
}: React.ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      className={cn(
        "px-4 py-3 text-xs font-bold uppercase tracking-wider text-[#4B5563] select-none",
        className
      )}
      {...props}
    >
      {children}
    </th>
  );
}

export function TableCell({
  className,
  children,
  ...props
}: React.TdHTMLAttributes<HTMLTableCellElement>) {
  return (
    <td
      className={cn("px-4 py-3.5 text-sm text-[#1F2421] align-middle", className)}
      {...props}
    >
      {children}
    </td>
  );
}

