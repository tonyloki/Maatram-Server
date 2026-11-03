"use client";

import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";
import { modalBackdropVariants, modalContentVariants } from "@/lib/animations";

export interface DialogProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: "sm" | "md" | "lg" | "xl";
}

export function Dialog({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  maxWidth = "md",
}: DialogProps) {
  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && open) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  const maxWidthStyles = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
          {/* Backdrop */}
          <motion.div
            variants={modalBackdropVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            onClick={onClose}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm"
          />

          {/* Modal Panel */}
          <motion.div
            variants={modalContentVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            role="dialog"
            aria-modal="true"
            aria-labelledby="dialog-title"
            aria-describedby={description ? "dialog-desc" : undefined}
            className={cn(
              "relative w-full rounded-2xl bg-white p-6 shadow-2xl border border-[#EBE6DD] z-10 overflow-hidden",
              maxWidthStyles[maxWidth]
            )}
          >
            {/* Header */}
            <div className="flex items-start justify-between pb-3">
              <div>
                <h3 id="dialog-title" className="text-lg font-bold text-[#1F2421]">{title}</h3>
                {description && <p id="dialog-desc" className="text-xs text-[#6B7280] mt-1">{description}</p>}
              </div>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close dialog"
                className="rounded-full p-1 text-[#9CA3AF] hover:text-[#1F2421] hover:bg-black/5 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content Body */}
            <div className="py-3 text-sm text-[#1F2421]">{children}</div>

            {/* Footer Actions */}
            {footer && <div className="mt-4 pt-3 flex items-center justify-end gap-2.5 border-t border-[#EBE6DD]">{footer}</div>}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

