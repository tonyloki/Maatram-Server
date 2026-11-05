"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { CheckCircle2, ArrowRight } from "lucide-react";

interface HeroWelcomeBannerProps {
  displayName: string;
  category: string;
  status: string;
}

export function HeroWelcomeBanner({
  displayName,
  category,
  status,
}: HeroWelcomeBannerProps) {
  const categoryLabel = category.toLowerCase().includes("volunteer")
    ? category
    : `${category} Volunteer`;

  const isApproved = status === "APPROVED" || status === "ACTIVE";

  return (
    <section
      aria-label="Welcome Banner"
      className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#FFFDF7] via-[#FFF3D6] to-[#FDE6B2] border border-[#FDE68A]/80 py-5 px-6 sm:px-8 shadow-xs"
    >
      {/* Decorative Tree Silhouette in Background */}
      <div className="absolute -bottom-6 right-64 w-36 h-36 pointer-events-none opacity-20 select-none hidden lg:block z-0">
        <Image
          src="/assets/maatram/decorations/tree-silhouette.svg"
          alt=""
          width={144}
          height={144}
          className="w-full h-full object-contain"
        />
      </div>

      <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        {/* Left Content Area */}
        <div className="max-w-xl space-y-2.5">
          {/* Status Badges */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center text-[11px] font-extrabold text-[#78350F] uppercase tracking-wider bg-[#FEF3C7] border border-[#FDE68A] px-3 py-0.5 rounded-full shadow-2xs">
              {categoryLabel}
            </span>

            <span className="inline-flex items-center gap-1 text-[11px] font-bold text-[#166534] bg-[#DCFCE7] border border-[#BBF7D0] px-2.5 py-0.5 rounded-full shadow-2xs">
              <CheckCircle2 className="w-3 h-3 text-[#16A34A]" />
              {isApproved ? "Approved" : status}
            </span>
          </div>

          {/* Heading */}
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1F2421] tracking-tight">
            Welcome back, {displayName}!
          </h1>

          {/* Subtitle */}
          <p className="text-xs sm:text-sm text-[#4B5563] leading-relaxed max-w-lg">
            Thank you for mentoring scholars and supporting higher education access across government schools and colleges.
          </p>

          {/* CTA Action */}
          <div className="pt-1.5">
            <Link
              href="/volunteer/events"
              className="inline-flex items-center gap-2 bg-[#F5B817] hover:bg-[#E5A800] active:bg-[#C99200] text-[#1F2421] font-extrabold text-xs sm:text-sm px-5 py-2.5 rounded-full shadow-sm shadow-[#F5B817]/35 transition-all transform hover:-translate-y-0.5"
            >
              <span>Discover Opportunities</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* Right Photographic Visual Composition matching Mentor Reference */}
        <div className="relative shrink-0 hidden md:block">
          {/* Framed authentic volunteer photograph */}
          <div className="w-72 lg:w-80 h-38 lg:h-42 relative rounded-2xl overflow-hidden shadow-sm border-2 border-white/90 bg-white">
            <Image
              src="/assets/maatram/photography/hero-volunteering.jpg"
              alt="Maatram volunteers mentoring students in a scenic community setting"
              fill
              priority
              sizes="(max-width: 1024px) 288px, 320px"
              className="object-cover object-center"
            />
            {/* Subtle warm gradient scrim at bottom */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent pointer-events-none" />

            {/* Flying birds silhouette watermark */}
            <div className="absolute top-2 left-2.5 w-14 h-7 pointer-events-none opacity-85">
              <Image
                src="/assets/maatram/decorations/birds-flock.svg"
                alt=""
                width={56}
                height={28}
                className="w-full h-full object-contain"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

