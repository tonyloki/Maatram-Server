import React, { forwardRef } from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = "text", error, label, helperText, id, ...props }, ref) => {
    const inputId = id || props.name;

    return (
      <div className="w-full flex flex-col space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-[#1F2421]">
            {label}
            {props.required && <span className="text-[#9B1C1C] ml-1">*</span>}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          type={type}
          className={cn(
            "w-full rounded-xl border border-[#EBE6DD] bg-white px-4 py-2.5 text-sm text-[#1F2421] placeholder-[#9CA3AF] transition-all focus:outline-none focus:ring-2 focus:ring-[#F5B817]/30 focus:border-[#F5B817] disabled:opacity-50 disabled:bg-[#FAF8F3]",
            error && "border-[#F8B4B4] focus:ring-[#F8B4B4]/40 focus:border-[#9B1C1C]",
            className
          )}
          {...props}
        />
        {error && <span className="text-xs text-[#9B1C1C] font-medium">{error}</span>}
        {helperText && !error && <span className="text-xs text-[#6B7280]">{helperText}</span>}
      </div>
    );
  }
);

Input.displayName = "Input";

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: string;
  label?: string;
  options?: Array<{ label: string; value: string | number }>;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, error, label, id, children, options, ...props }, ref) => {
    const selectId = id || props.name;

    return (
      <div className="w-full flex flex-col space-y-1.5">
        {label && (
          <label htmlFor={selectId} className="text-sm font-medium text-[#1F2421]">
            {label}
            {props.required && <span className="text-[#9B1C1C] ml-1">*</span>}
          </label>
        )}
        <select
          id={selectId}
          ref={ref}
          className={cn(
            "w-full rounded-xl border border-[#EBE6DD] bg-white px-4 py-2.5 text-sm text-[#1F2421] transition-all focus:outline-none focus:ring-2 focus:ring-[#F5B817]/30 focus:border-[#F5B817] disabled:opacity-50",
            error && "border-[#F8B4B4] focus:ring-[#F8B4B4]/40 focus:border-[#9B1C1C]",
            className
          )}
          {...props}
        >
          {options
            ? options.map((opt) => (
                <option key={String(opt.value)} value={opt.value}>
                  {opt.label}
                </option>
              ))
            : children}
        </select>
        {error && <span className="text-xs text-[#9B1C1C] font-medium">{error}</span>}
      </div>
    );
  }
);

Select.displayName = "Select";

