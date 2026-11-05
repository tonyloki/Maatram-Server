import React from "react";
import Image from "next/image";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface LogoProps {
  variant?: "transparent" | "with-bg";
  width?: number;
  height?: number;
  href?: string;
  className?: string;
  priority?: boolean;
  unoptimized?: boolean;
}

/**
 * Official Maatram Foundation Brand Logo.
 * Preserves the canonical 2.014:1 aspect ratio without stretching or distortion.
 */
export function Logo({
  variant = "transparent",
  width = 140,
  height = 70,
  href,
  className,
  priority = false,
  unoptimized = true,
}: LogoProps) {
  const src =
    variant === "transparent"
      ? "/maatram_logo-removebg-preview.png"
      : "/Maatramlogowithbg.jpeg";

  const imageElement = (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <Image
        src={src}
        alt="Maatram Educational Aid Foundation"
        width={width}
        height={height}
        className="object-contain"
        priority={priority}
        unoptimized={unoptimized}
      />
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="inline-flex items-center focus:outline-none focus:ring-2 focus:ring-[#F5B817] rounded-lg">
        {imageElement}
      </Link>
    );
  }

  return imageElement;
}

