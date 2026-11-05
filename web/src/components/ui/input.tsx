import React, { forwardRef } from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = "text", error, label, helperText, leftIcon, rightIcon, id, ...props }, ref) => {
    const inputId = id || props.name;

    return (
      <div className="w-full flex flex-col space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-semibold text-[#1F2421]">
            {label}
            {props.required && <span className="text-[#9B1C1C] ml-1">*</span>}
          </label>
        )}
        <div className="relative flex items-center w-full">
          {leftIcon && (
            <div className="absolute left-3.5 pointer-events-none text-[#9CA3AF] flex items-center justify-center">
              {leftIcon}
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            type={type}
            className={cn(
              "w-full rounded-xl border border-[#E5E7EB] bg-white px-4 py-2.5 text-sm text-[#1F2421] placeholder-[#9CA3AF] transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:border-transparent disabled:opacity-50 disabled:bg-[#FAF8F5]",
              leftIcon && "pl-10",
              rightIcon && "pr-10",
              error && "border-[#F8B4B4] focus:ring-[#9B1C1C]/30 focus:border-[#9B1C1C]",
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3.5 pointer-events-none text-[#9CA3AF] flex items-center justify-center">
              {rightIcon}
            </div>
          )}
        </div>
        {error && <span className="text-xs text-[#9B1C1C] font-semibold">{error}</span>}
        {helperText && !error && <span className="text-xs text-[#4B5563]">{helperText}</span>}
      </div>
    );
  }
);

Input.displayName = "Input";

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string;
  label?: string;
  helperText?: string;
  maxLength?: number;
  currentLength?: number;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, label, helperText, maxLength, currentLength, id, ...props }, ref) => {
    const textareaId = id || props.name;

    return (
      <div className="w-full flex flex-col space-y-1.5">
        <div className="flex items-center justify-between">
          {label && (
            <label htmlFor={textareaId} className="text-sm font-semibold text-[#1F2421]">
              {label}
              {props.required && <span className="text-[#9B1C1C] ml-1">*</span>}
            </label>
          )}
          {maxLength !== undefined && currentLength !== undefined && (
            <span className="text-xs text-[#9CA3AF]">
              {currentLength} / {maxLength}
            </span>
          )}
        </div>
        <textarea
          id={textareaId}
          ref={ref}
          maxLength={maxLength}
          rows={props.rows || 3}
          className={cn(
            "w-full rounded-xl border border-[#E5E7EB] bg-white px-4 py-2.5 text-sm text-[#1F2421] placeholder-[#9CA3AF] transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:border-transparent disabled:opacity-50 disabled:bg-[#FAF8F5] resize-y",
            error && "border-[#F8B4B4] focus:ring-[#9B1C1C]/30 focus:border-[#9B1C1C]",
            className
          )}
          {...props}
        />
        {error && <span className="text-xs text-[#9B1C1C] font-semibold">{error}</span>}
        {helperText && !error && <span className="text-xs text-[#4B5563]">{helperText}</span>}
      </div>
    );
  }
);

Textarea.displayName = "Textarea";

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: string;
  label?: string;
  helperText?: string;
  options?: Array<{ label: string; value: string | number }>;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, error, label, helperText, id, children, options, ...props }, ref) => {
    const selectId = id || props.name;

    return (
      <div className="w-full flex flex-col space-y-1.5">
        {label && (
          <label htmlFor={selectId} className="text-sm font-semibold text-[#1F2421]">
            {label}
            {props.required && <span className="text-[#9B1C1C] ml-1">*</span>}
          </label>
        )}
        <div className="relative">
          <select
            id={selectId}
            ref={ref}
            className={cn(
              "w-full rounded-xl border border-[#E5E7EB] bg-white px-4 py-2.5 text-sm text-[#1F2421] transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:border-transparent disabled:opacity-50 appearance-none pr-10 cursor-pointer",
              error && "border-[#F8B4B4] focus:ring-[#9B1C1C]/30 focus:border-[#9B1C1C]",
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
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-[#4B5563]">
            <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
              <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
            </svg>
          </div>
        </div>
        {error && <span className="text-xs text-[#9B1C1C] font-semibold">{error}</span>}
        {helperText && !error && <span className="text-xs text-[#4B5563]">{helperText}</span>}
      </div>
    );
  }
);

Select.displayName = "Select";
