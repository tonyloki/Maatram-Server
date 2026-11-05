"use client";

import React from "react";
import Image from "next/image";
import { Compass } from "lucide-react";

export function VolunteeringGuideCard() {
  const steps = [
    {
      number: "1",
      title: "Apply for an event",
      desc: "Browse upcoming drives and express your interest.",
    },
    {
      number: "2",
      title: "Wait for selection",
      desc: "Coordinators review and confirm your participation.",
    },
    {
      number: "3",
      title: "Check in & contribute",
      desc: "Attend on time, log your service, and earn impact points.",
    },
  ];

  return (
    <div className="bg-white rounded-2xl p-6 border border-[#EFECE6] shadow-xs flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center gap-2 text-[#1F2421] mb-5">
          <div className="w-8 h-8 rounded-xl bg-[#FFF8E7] text-[#946C00] flex items-center justify-center">
            <Compass className="w-4 h-4 text-[#F5B817]" />
          </div>
          <h3 className="text-base font-extrabold tracking-tight">
            Volunteering Guide
          </h3>
        </div>

        {/* 3 Numbered Steps */}
        <div className="space-y-4">
          {steps.map((st) => (
            <div key={st.number} className="flex items-start gap-3.5">
              <div className="w-7 h-7 rounded-full bg-[#F5B817] text-[#1F2421] font-black text-xs flex items-center justify-center shrink-0 shadow-2xs mt-0.5">
                {st.number}
              </div>
              <div className="space-y-0.5">
                <h4 className="text-xs sm:text-sm font-bold text-[#1F2421]">
                  {st.title}
                </h4>
                <p className="text-[11px] sm:text-xs text-[#6B7280] leading-relaxed">
                  {st.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Slogan Banner with Together Heart Illustration */}
      <div className="mt-6 p-3.5 rounded-xl bg-[#FFF8E7] border border-[#FDE68A]/60 flex items-center gap-3.5">
        <div className="w-11 h-11 relative shrink-0">
          <Image
            src="/assets/maatram/illustrations/together-heart.svg"
            alt="Hand holding heart with sunburst rays"
            fill
            className="object-contain"
          />
        </div>
        <div>
          <p className="text-xs font-extrabold text-[#946C00] leading-snug">
            Together for a better tomorrow
          </p>
          <p className="text-[10px] text-[#78350F] font-medium">
            Empowering first-generation scholars
          </p>
        </div>
      </div>
    </div>
  );
}

