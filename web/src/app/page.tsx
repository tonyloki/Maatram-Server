"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { ArrowRight, GraduationCap, Briefcase, ShieldCheck } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#FAF8F0] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
      <div className="w-full max-w-6xl bg-white rounded-3xl sm:rounded-[36px] border border-[#EBE7DF] shadow-[0_10px_35px_-5px_rgba(0,0,0,0.05)] overflow-hidden">
        {/* Main Hero Card Interior */}
        <div className="p-6 sm:p-10 lg:p-14">
          {/* Top Logo */}
          <div className="mb-8 sm:mb-12">
            <Link href="/" className="inline-block transition-opacity hover:opacity-90">
              <Image
                src="/maatram_logo-removebg-preview.png"
                alt="Maatram Foundation Logo"
                width={150}
                height={55}
                priority
                className="h-10 sm:h-12 w-auto object-contain"
              />
            </Link>
          </div>

          {/* Hero Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
            {/* Left Content Column */}
            <div className="lg:col-span-7 flex flex-col justify-center">
              <h1 className="text-3xl sm:text-5xl lg:text-[54px] font-extrabold text-[#1F2421] tracking-tight leading-[1.12]">
                Volunteer for a <br className="hidden sm:inline" />
                <span className="text-[#1F2421]">Better Tomorrow</span>
              </h1>

              <p className="mt-4 sm:mt-5 text-sm sm:text-base lg:text-[17px] text-[#555E58] leading-relaxed max-w-xl">
                Join Maatram Foundation&apos;s community of students, alumni and
                professionals to create meaningful opportunities for students.
              </p>

              {/* Action Buttons */}
              <div className="mt-7 sm:mt-9 flex flex-wrap items-center gap-3 sm:gap-4">
                <Link
                  href="/register"
                  className="inline-flex items-center justify-center gap-2 px-6 sm:px-7 py-3 sm:py-3.5 rounded-xl bg-[#F5B817] hover:bg-[#E5A807] text-[#1F2421] font-bold text-sm sm:text-base shadow-sm transition-all transform hover:-translate-y-0.5 active:translate-y-0"
                >
                  <span>Get Started</span>
                  <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
                </Link>

                <Link
                  href="/login"
                  className="inline-flex items-center justify-center px-6 sm:px-7 py-3 sm:py-3.5 rounded-xl bg-white hover:bg-stone-50 border border-[#D5D0C7] text-[#1F2421] font-bold text-sm sm:text-base shadow-xs transition-all transform hover:-translate-y-0.5 active:translate-y-0"
                >
                  Login
                </Link>
              </div>
            </div>

            {/* Right Photo Column */}
            <div className="lg:col-span-5 flex justify-center">
              <div className="relative w-full max-w-md lg:max-w-none rounded-2xl sm:rounded-3xl overflow-hidden shadow-md border border-[#EFECE6] bg-stone-100 aspect-[4/3] sm:aspect-[16/11]">
                <Image
                  src="/assets/maatram/photography/volunteers-team-hero.jpg"
                  alt="Maatram Foundation Volunteers Team"
                  fill
                  priority
                  sizes="(max-width: 1024px) 100vw, 450px"
                  className="object-cover object-center"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Feature Strip with 3 Key Highlights */}
        <div className="border-t border-[#F0ECE1] bg-[#FAF8F2]/60 px-6 sm:px-10 lg:px-14 py-6 sm:py-8">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 sm:gap-8">
            {/* Feature 1 */}
            <div className="flex flex-col items-center sm:items-center text-center">
              <div className="w-11 h-11 rounded-full bg-[#FFF3D6] text-[#D97706] flex items-center justify-center mb-2.5 shadow-2xs">
                <GraduationCap className="w-5 h-5 text-[#F5B817]" />
              </div>
              <h2 className="text-base font-bold text-[#1F2421]">School Visits</h2>
              <p className="text-xs sm:text-sm text-[#6B7280] mt-0.5">Inspire and guide students</p>
            </div>

            {/* Feature 2 */}
            <div className="flex flex-col items-center sm:items-center text-center">
              <div className="w-11 h-11 rounded-full bg-[#FFF3D6] text-[#D97706] flex items-center justify-center mb-2.5 shadow-2xs">
                <Briefcase className="w-5 h-5 text-[#F5B817]" />
              </div>
              <h2 className="text-base font-bold text-[#1F2421]">Mock Interviews</h2>
              <p className="text-xs sm:text-sm text-[#6B7280] mt-0.5">Support career readiness</p>
            </div>

            {/* Feature 3 */}
            <div className="flex flex-col items-center sm:items-center text-center">
              <div className="w-11 h-11 rounded-full bg-[#FFF3D6] text-[#D97706] flex items-center justify-center mb-2.5 shadow-2xs">
                <ShieldCheck className="w-5 h-5 text-[#F5B817]" />
              </div>
              <h2 className="text-base font-bold text-[#1F2421]">BGV Support</h2>
              <p className="text-xs sm:text-sm text-[#6B7280] mt-0.5">Help students take the next step</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
