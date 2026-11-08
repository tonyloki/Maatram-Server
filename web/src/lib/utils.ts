import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility to conditionally combine and merge Tailwind CSS classes
 * without style precedence conflicts.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

