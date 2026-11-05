import React, { forwardRef } from "react";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: React.ReactNode;
  description?: string;
  error?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, description, error, id, checked, disabled, ...props }, ref) => {
    const checkboxId = id || props.name;

    return (
      <div className={cn("flex items-start gap-3", className)}>
        <div className="relative flex items-center justify-center mt-0.5">
          <input
            id={checkboxId}
            ref={ref}
            type="checkbox"
            checked={checked}
            disabled={disabled}
            className="peer sr-only"
            {...props}
          />
          <label
            htmlFor={checkboxId}
            className={cn(
              "flex h-5 w-5 cursor-pointer items-center justify-center rounded-md border border-[#D1D5DB] bg-white transition-all peer-focus-visible:ring-2 peer-focus-visible:ring-[#F5B817] peer-focus-visible:ring-offset-2 peer-checked:border-[#F5B817] peer-checked:bg-[#F5B817] peer-disabled:cursor-not-allowed peer-disabled:opacity-50",
              error && "border-[#F8B4B4]"
            )}
          >
            <Check className="h-3.5 w-3.5 text-[#1F2421] opacity-0 transition-opacity peer-checked:opacity-100" strokeWidth={3} />
          </label>
        </div>

        {(label || description) && (
          <div className="flex flex-col space-y-0.5">
            {label && (
              <label
                htmlFor={checkboxId}
                className={cn(
                  "text-sm font-semibold text-[#1F2421] cursor-pointer select-none",
                  disabled && "cursor-not-allowed opacity-50"
                )}
              >
                {label}
              </label>
            )}
            {description && (
              <p className={cn("text-xs text-[#4B5563] leading-relaxed", disabled && "opacity-50")}>
                {description}
              </p>
            )}
            {error && <span className="text-xs text-[#9B1C1C] font-semibold">{error}</span>}
          </div>
        )}
      </div>
    );
  }
);

Checkbox.displayName = "Checkbox";

