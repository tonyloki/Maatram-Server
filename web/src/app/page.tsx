"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import {
  GraduationCap,
  Briefcase,
  Users,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  ShieldCheck,
  Award,
  Heart,
  Quote,
} from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  staggerContainer,
  fadeInUp,
} from "@/lib/animations";

export default function HomePage() {
  const opportunityCards = [
    {
      title: "Government School Visits",
      categoryTag: "School Education",
      description:
        "Travel to rural and semi-urban higher secondary schools to guide 11th and 12th standard students on college admissions, entrance exams, and scholarship opportunities.",
      image: "/assets/images/school-visit.jpg",
      icon: GraduationCap,
      format: "In-person school workshops",
      focus: "Career awareness & peer inspiration",
      link: "/events",
      accent: "border-[#F5B817]/40 bg-[#FFF8E7] text-[#946C00]",
    },
    {
      title: "1-on-1 Mock Interviews",
      categoryTag: "Career Readiness",
      description:
        "Conduct realistic technical, behavioral, and HR practice interviews with graduating scholars. Provide constructive resume critiques and confidence-building coaching.",
      image: "/assets/images/mock-interview.jpg",
      icon: Briefcase,
      format: "Online & weekend hybrid",
      focus: "Placement coaching & communication",
      link: "/events",
      accent: "border-[#93C5FD]/50 bg-[#EFF6FF] text-[#1D4ED8]",
    },
    {
      title: "Background Verification Drives",
      categoryTag: "Community Outreach",
      description:
        "Participate in home visits and community interactions to verify socio-economic eligibility for students applying for 100% free higher education scholarships.",
      image: "/assets/images/bgv-support.jpg",
      icon: Users,
      format: "Field visits & documentation",
      focus: "Integrity & ethical candidate selection",
      link: "/events",
      accent: "border-[#86EFAC]/50 bg-[#F0FDF4] text-[#15803D]",
    },
  ];

  const workflowSteps = [
    {
      step: "01",
      title: "Register & Choose Track",
      desc: "Join as a Student, Alumni, or Corporate Panelist and outline your background and mentoring preferences.",
    },
    {
      step: "02",
      title: "Discover Volunteering Drives",
      desc: "Browse upcoming school awareness camps, online mock interview rosters, and regional verification drives.",
    },
    {
      step: "03",
      title: "Guide Deserving Scholars",
      desc: "Share your knowledge and empathy directly with bright students taking the first big step in their families.",
    },
    {
      step: "04",
      title: "Earn Verified Recognition",
      desc: "Receive digitally verified volunteering credits, accumulate milestone achievement badges, and inspire others.",
    },
  ];

  const tracks = [
    {
      role: "Student Volunteers",
      badge: "Scholars Giving Back",
      summary:
        "Current college scholars studying at partner universities who return to inspire younger school students.",
      points: [
        "Peer-to-peer relatable guidance",
        "Higher education entrance awareness",
        "First-hand college transition sharing",
      ],
      link: "/register?category=STUDENT",
    },
    {
      role: "Alumni Volunteers",
      badge: "Industry Navigators",
      summary:
        "Graduated scholars now employed across IT, core engineering, and corporate sectors sharing career roadmaps.",
      points: [
        "Practical career trajectory advice",
        "Domain-specific technical roadmaps",
        "Workplace culture and readiness",
      ],
      link: "/register?category=ALUMNI",
    },
    {
      role: "Corporate Mentors",
      badge: "Executive Panelists",
      summary:
        "Experienced industry professionals, HR directors, and hiring managers leading mock interview panels.",
      points: [
        "Structured behavioral assessments",
        "Resume and communication critiques",
        "Industry hiring standards exposure",
      ],
      link: "/register?category=CORPORATE",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="home" />

      <main className="flex-1">
        {/* ================================================================= */}
        {/* 1. HERO SECTION (REFERENCE MATCH: Volunteer for a Better Tomorrow)*/}
        {/* ================================================================= */}
        <section className="relative overflow-hidden pt-6 pb-12 md:pt-10 md:pb-16 lg:pt-14 lg:pb-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-center">
              {/* LEFT COLUMN: Prominent Headline, Narrative & Call to Actions */}
              <motion.div
                className="lg:col-span-6 space-y-6"
                initial="hidden"
                animate="visible"
                variants={staggerContainer}
              >
                {/* Headline matching Mentor Reference */}
                <motion.h1
                  variants={fadeInUp}
                  className="text-4xl sm:text-5xl lg:text-[56px] font-extrabold tracking-tight text-[#1F2421] leading-[1.12]"
                >
                  Volunteer for a<br />
                  <span className="relative inline-block pb-3">
                    <span>Better Tomorrow</span>
                    {/* Golden Brush Underline Stroke */}
                    <svg
                      className="absolute -bottom-0.5 left-0 w-full h-3.5 text-[#F5B817] pointer-events-none select-none"
                      viewBox="0 0 260 12"
                      fill="none"
                      preserveAspectRatio="none"
                    >
                      <path
                        d="M2 9C55 3 160 2 258 7"
                        stroke="currentColor"
                        strokeWidth="5.5"
                        strokeLinecap="round"
                      />
                    </svg>
                  </span>
                </motion.h1>

                {/* Subtitle matching Mentor Reference */}
                <motion.p
                  variants={fadeInUp}
                  className="text-base sm:text-lg text-[#4B5563] max-w-lg leading-relaxed"
                >
                  Join Maatram Foundation&apos;s community of students, alumni and professionals to
                  create meaningful opportunities for students.
                </motion.p>

                {/* Action Buttons matching Mentor Reference */}
                <motion.div
                  variants={fadeInUp}
                  className="flex flex-wrap items-center gap-4 pt-1"
                >
                  <Link href="/register">
                    <button
                      type="button"
                      className="px-8 py-3.5 rounded-xl bg-[#F5B817] hover:bg-[#E0A714] text-[#1F2421] font-bold text-base transition-all shadow-xs flex items-center gap-2"
                    >
                      <span>Get Started</span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </Link>
                  <Link href="/login">
                    <button
                      type="button"
                      className="px-8 py-3.5 rounded-xl bg-white border border-[#D1D5DB] hover:bg-gray-50 text-[#1F2421] font-semibold text-base transition-all shadow-2xs"
                    >
                      Login
                    </button>
                  </Link>
                </motion.div>
              </motion.div>

              {/* RIGHT COLUMN: Iconic Volunteer Group Photo with Golden Swoop Wave */}
              <motion.div
                className="lg:col-span-6 relative flex justify-center lg:justify-end"
                initial={{ opacity: 1, scale: 1 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <div className="relative w-full max-w-[540px] aspect-[16/11] rounded-3xl overflow-hidden shadow-xl border-2 border-white/80 bg-white">
                  <Image
                    src="/assets/maatram/photography/volunteers-team-hero.jpg"
                    alt="Maatram volunteers facing nature"
                    fill
                    priority
                    className="object-cover object-center"
                    sizes="(max-width: 768px) 100vw, 50vw"
                  />
                  {/* Dynamic Vector Swoop Wave Accent across the bottom */}
                  <div className="absolute -bottom-1 inset-x-0 h-24 pointer-events-none select-none z-10">
                    <Image
                      src="/assets/maatram/decorations/landing-wave-swoop.svg"
                      alt="Golden wave swoop"
                      fill
                      className="object-fill object-bottom"
                    />
                  </div>
                </div>
              </motion.div>
            </div>

            {/* 3 Signature Pillar Columns matching Mentor Reference Bottom Strip */}
            <div className="mt-12 lg:mt-16 pt-8 border-t border-[#EBE6DD]/80 grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
              {/* Pillar 1: School Visits */}
              <div className="flex flex-col items-center space-y-2">
                <div className="w-12 h-12 rounded-2xl bg-[#FFF3D6] border border-[#FDE68A] flex items-center justify-center text-[#B45309] shadow-2xs">
                  <Users className="w-6 h-6 text-[#B45309]" />
                </div>
                <h3 className="font-bold text-base text-[#1F2421]">School Visits</h3>
                <p className="text-xs sm:text-sm text-[#4B5563]">Inspire and guide students</p>
              </div>

              {/* Pillar 2: Mock Interviews */}
              <div className="flex flex-col items-center space-y-2">
                <div className="w-12 h-12 rounded-2xl bg-[#FFF3D6] border border-[#FDE68A] flex items-center justify-center text-[#B45309] shadow-2xs">
                  <GraduationCap className="w-6 h-6 text-[#B45309]" />
                </div>
                <h3 className="font-bold text-base text-[#1F2421]">Mock Interviews</h3>
                <p className="text-xs sm:text-sm text-[#4B5563]">Support career readiness</p>
              </div>

              {/* Pillar 3: BGV Support */}
              <div className="flex flex-col items-center space-y-2">
                <div className="w-12 h-12 rounded-2xl bg-[#FFF3D6] border border-[#FDE68A] flex items-center justify-center text-[#B45309] shadow-2xs">
                  <Briefcase className="w-6 h-6 text-[#B45309]" />
                </div>
                <h3 className="font-bold text-base text-[#1F2421]">BGV Support</h3>
                <p className="text-xs sm:text-sm text-[#4B5563]">Help students take the next step</p>
              </div>
            </div>
          </div>
        </section>

        {/* ================================================================= */}
        {/* 2. SIGNATURE OPPORTUNITIES (VISUAL DIFFERENTIATION & PHOTOGRAPHY) */}
        {/* ================================================================= */}
        <section className="py-16 md:py-24 bg-white border-y border-[#EBE6DD]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl mx-auto text-center mb-14">
              <span className="text-xs font-bold uppercase tracking-wider text-[#B45309] bg-[#FFF8E7] px-3.5 py-1 rounded-full border border-[#F5B817]/30">
                Signature Volunteering Tracks
              </span>
              <h2 className="text-3xl font-extrabold text-[#1F2421] mt-3">
                Ways You Can Make an Impact
              </h2>
              <p className="text-sm text-[#4B5563] mt-2">
                Every track provides structured support at pivotal milestones in a student&apos;s academic journey.
              </p>
            </div>

            {/* Opportunity Cards with Integrated Visual Photography */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {opportunityCards.map((opp) => {
                const IconComponent = opp.icon;
                return (
                  <Card
                    key={opp.title}
                    className="overflow-hidden border-[#E5E7EB] bg-white flex flex-col justify-between hover:shadow-xl transition-all duration-300 group"
                  >
                    <div>
                      {/* Visual Header with Real Photography */}
                      <div className="relative w-full h-48 overflow-hidden bg-gray-100">
                        <Image
                          src={opp.image}
                          alt={opp.title}
                          fill
                          className="object-cover group-hover:scale-105 transition-transform duration-500"
                          sizes="(max-width: 768px) 100vw, 33vw"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                        
                        {/* Tag & Icon Pill */}
                        <div className="absolute top-3 left-3 flex items-center gap-2">
                          <span className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-white/95 text-[#1F2421] shadow-sm backdrop-blur-sm">
                            {opp.categoryTag}
                          </span>
                        </div>

                        <div className="absolute bottom-3 left-3 flex items-center gap-2 text-white text-xs font-medium">
                          <div className="w-6 h-6 rounded-lg bg-black/40 backdrop-blur-sm flex items-center justify-center text-[#F5B817]">
                            <IconComponent className="w-3.5 h-3.5" />
                          </div>
                          <span>{opp.format}</span>
                        </div>
                      </div>

                      {/* Content Body */}
                      <div className="p-6 space-y-3">
                        <h3 className="text-lg font-bold text-[#1F2421] group-hover:text-[#B45309] transition-colors">
                          {opp.title}
                        </h3>
                        <p className="text-xs text-[#4B5563] leading-relaxed">
                          {opp.description}
                        </p>
                        <div className="pt-2 text-[11px] text-[#6B7280] font-medium border-t border-[#F3F4F6]">
                          <span className="text-[#B45309] font-semibold">Core Focus: </span>
                          <span>{opp.focus}</span>
                        </div>
                      </div>
                    </div>

                    {/* Card Action Link */}
                    <div className="p-6 pt-0">
                      <Link
                        href={opp.link}
                        className="w-full inline-flex items-center justify-between px-4 py-2.5 rounded-xl bg-[#FAF8F3] hover:bg-[#FFF8E7] text-xs font-bold text-[#B45309] border border-[#EBE6DD] transition-all"
                      >
                        <span>View Volunteering Opportunities</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        {/* ================================================================= */}
        {/* 3. HOW VOLUNTEERING WORKS (TIMELINE WORKFLOW)                      */}
        {/* ================================================================= */}
        <section className="py-16 md:py-24 bg-[#FAF8F3]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl mx-auto text-center mb-16">
              <span className="text-xs font-bold uppercase tracking-wider text-[#B45309]">
                Structured & Transparent
              </span>
              <h2 className="text-3xl font-extrabold text-[#1F2421] mt-2">
                How Volunteering Works
              </h2>
              <p className="text-sm text-[#4B5563] mt-2">
                A streamlined process designed to respect your schedule while maximizing mentorship value.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {workflowSteps.map((step) => (
                <div
                  key={step.step}
                  className="bg-white rounded-3xl p-6 border border-[#EBE6DD] shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow relative"
                >
                  <div>
                    <span className="text-3xl font-black text-[#F5B817] block mb-3">
                      {step.step}
                    </span>
                    <h3 className="text-base font-bold text-[#1F2421] mb-2">{step.title}</h3>
                    <p className="text-xs text-[#6B7280] leading-relaxed">{step.desc}</p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-[#F3F4F6] text-[11px] text-[#15803D] flex items-center gap-1 font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Simple & Verified</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ================================================================= */}
        {/* 4. VOLUNTEER CATEGORIES (STUDENT, ALUMNI, CORPORATE)             */}
        {/* ================================================================= */}
        <section className="py-16 md:py-24 bg-white border-y border-[#EBE6DD]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl mx-auto text-center mb-16">
              <span className="text-xs font-bold uppercase tracking-wider text-[#B45309]">
                Tailored Engagement Tracks
              </span>
              <h2 className="text-3xl font-extrabold text-[#1F2421] mt-2">
                Who Can Volunteer?
              </h2>
              <p className="text-sm text-[#4B5563] mt-2">
                Each category brings a distinct vantage point to support student growth and career preparedness.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {tracks.map((t) => (
                <div
                  key={t.role}
                  className="bg-[#FAF8F3] rounded-3xl p-8 border border-[#EBE6DD] flex flex-col justify-between space-y-6 hover:border-[#D1D5DB] transition-all"
                >
                  <div className="space-y-4">
                    <div className="inline-block px-3 py-1 rounded-full bg-white border border-[#EBE6DD] text-[11px] font-bold text-[#B45309]">
                      {t.badge}
                    </div>
                    <h3 className="text-xl font-extrabold text-[#1F2421]">{t.role}</h3>
                    <p className="text-xs text-[#4B5563] leading-relaxed">{t.summary}</p>
                    <div className="space-y-2 pt-2 border-t border-[#EBE6DD]">
                      {t.points.map((pt) => (
                        <div key={pt} className="flex items-center gap-2 text-xs text-[#374151]">
                          <CheckCircle2 className="w-3.5 h-3.5 text-[#15803D] shrink-0" />
                          <span>{pt}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <Link href={t.link}>
                    <Button variant="outline" size="sm" className="w-full bg-white hover:bg-[#FFF8E7] font-semibold">
                      Register as {t.role.split(" ")[0]}
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ================================================================= */}
        {/* 5. ABOUT & MISSION STORYTELLING (QUALITATIVE PURPOSE)             */}
        {/* ================================================================= */}
        <section className="py-16 md:py-24 bg-[#FAF8F3]">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="bg-white rounded-3xl p-8 sm:p-12 border border-[#EBE6DD] shadow-sm grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
              <div className="md:col-span-8 space-y-4">
                <Quote className="w-8 h-8 text-[#F5B817]" />
                <blockquote className="text-base sm:text-lg font-medium text-[#1F2421] leading-relaxed italic">
                  “When a student from a rural government school meets an alumnus who sat in that same classroom just four years ago and is now an engineer, hope becomes tangible. That is the essence of Maatram.”
                </blockquote>
                <div className="pt-2">
                  <div className="text-sm font-bold text-[#1F2421]">Maatram Volunteering Council</div>
                  <div className="text-xs text-[#6B7280]">
                    Dedicated to educational enablement, ethical safeguarding, and generational progress.
                  </div>
                </div>
              </div>

              <div className="md:col-span-4 flex flex-col items-center sm:items-start md:items-end justify-center border-t md:border-t-0 md:border-l border-[#EBE6DD] pt-6 md:pt-0 md:pl-8">
                <Link href="/about">
                  <Button variant="primary" size="md" className="font-bold">
                    <span>Our Full Mission</span>
                    <ArrowRight className="w-4 h-4 ml-1.5" />
                  </Button>
                </Link>
                <span className="text-[11px] text-[#6B7280] mt-2">
                  Learn about our values & policies
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* ================================================================= */}
        {/* 6. CALL TO ACTION SECTION                                         */}
        {/* ================================================================= */}
        <section className="py-16 md:py-20 bg-gradient-to-br from-[#1F2421] to-[#2D332F] text-white text-center relative overflow-hidden">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 space-y-6">
            <span className="inline-block px-3.5 py-1 rounded-full bg-[#F5B817]/20 text-[#F5B817] text-xs font-bold uppercase tracking-wider">
              Start Your Mentorship Journey
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Ready to Shape the Future of Deserving Students?
            </h2>
            <p className="text-sm sm:text-base text-gray-300 max-w-xl mx-auto leading-relaxed">
              Create your volunteer profile, choose your preferred engagement track, and make a real difference where it matters most.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
              <Link href="/register">
                <Button variant="primary" size="lg" className="w-full sm:w-auto px-8 h-12 text-base font-bold shadow-lg shadow-[#F5B817]/30">
                  <span>Register as a Volunteer</span>
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
              <Link href="/events">
                <Button variant="outline" size="lg" className="w-full sm:w-auto px-8 h-12 text-base font-semibold text-white border-white/30 hover:bg-white/10">
                  Browse Opportunities
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
