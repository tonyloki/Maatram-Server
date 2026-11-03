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
        {/* 1. HERO SECTION (REDESIGNED TWO-COLUMN EDITORIAL COMPOSITION)     */}
        {/* ================================================================= */}
        <section className="relative overflow-hidden pt-8 pb-16 md:pt-14 md:pb-24 lg:pt-20 lg:pb-28">
          {/* Subtle Warm Background Glows */}
          <div className="absolute top-0 right-1/4 -mt-20 w-96 h-96 rounded-full bg-[#F5B817]/10 blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 rounded-full bg-[#F5B817]/15 blur-3xl pointer-events-none" />

          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
              {/* LEFT COLUMN: Prominent Headline, Narrative & Call to Actions */}
              <motion.div
                className="lg:col-span-7 space-y-6"
                initial="hidden"
                animate="visible"
                variants={staggerContainer}
              >
                {/* Community Label */}
                <motion.div variants={fadeInUp} className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#FFF8E7] border border-[#F5B817]/40 text-xs font-semibold text-[#946C00]">
                  <Sparkles className="w-3.5 h-3.5 text-[#F5B817]" />
                  <span>Maatram Volunteering & Mentorship Community</span>
                </motion.div>

                {/* Strong Headline */}
                <motion.h1
                  variants={fadeInUp}
                  className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-[#1F2421] leading-[1.12]"
                >
                  Transform Education Through{" "}
                  <span className="relative inline-block text-[#B45309]">
                    <span>Meaningful Mentorship</span>
                    <span className="absolute bottom-1 left-0 w-full h-3 bg-[#F5B817]/35 -rotate-1 rounded-sm -z-10" />
                  </span>
                </motion.h1>

                {/* Description */}
                <motion.p
                  variants={fadeInUp}
                  className="text-base sm:text-lg text-[#4B5563] max-w-xl leading-relaxed"
                >
                  Join a passionate community of students, alumni, and industry professionals guiding
                  first-generation scholars across rural and underserved schools to achieve higher education and career success.
                </motion.p>

                {/* CTAs */}
                <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2">
                  <Link href="/register">
                    <Button
                      variant="primary"
                      size="lg"
                      className="w-full sm:w-auto px-8 h-12 shadow-lg shadow-[#F5B817]/25 text-base font-bold"
                    >
                      <span>Become a Volunteer</span>
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                  <Link href="/events">
                    <Button
                      variant="outline"
                      size="lg"
                      className="w-full sm:w-auto px-8 h-12 text-base font-semibold border-[#D1D5DB] hover:bg-white"
                    >
                      Explore Opportunities
                    </Button>
                  </Link>
                </motion.div>

                {/* Factually Supported Trust Badges */}
                <motion.div
                  variants={fadeInUp}
                  className="pt-4 border-t border-[#EBE6DD] flex flex-wrap items-center gap-6 text-xs text-[#6B7280]"
                >
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[#15803D]" />
                    <span className="font-medium text-[#374151]">Verified Service Hours</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-[#15803D]" />
                    <span className="font-medium text-[#374151]">Safe & Ethical Mentorship</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Award className="w-4 h-4 text-[#15803D]" />
                    <span className="font-medium text-[#374151]">Milestone Recognition</span>
                  </div>
                </motion.div>
              </motion.div>

              {/* RIGHT COLUMN: Authentic Photography with Editorial Accent */}
              <motion.div
                className="lg:col-span-5 relative"
                initial={{ opacity: 1, scale: 1 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <div className="relative mx-auto max-w-md lg:max-w-none">
                  {/* Outer Framed Container */}
                  <div className="relative rounded-3xl overflow-hidden shadow-2xl border-2 border-white/80 bg-white">
                    {/* Real Education Volunteering Photo */}
                    <div className="relative w-full h-[340px] sm:h-[400px]">
                      <Image
                        src="/assets/images/hero-volunteering.jpg"
                        alt="Education volunteers mentoring students in a classroom"
                        fill
                        priority
                        className="object-cover"
                        sizes="(max-width: 768px) 100vw, 40vw"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                    </div>

                    {/* Editorial Supporting Card at Bottom of Image */}
                    <div className="absolute bottom-4 left-4 right-4 bg-white/95 backdrop-blur-md rounded-2xl p-4 border border-[#EBE6DD] shadow-lg">
                      <div className="flex items-start gap-3">
                        <div className="w-9 h-9 rounded-xl bg-[#FFF8E7] border border-[#F5B817]/40 text-[#B45309] flex items-center justify-center shrink-0 mt-0.5">
                          <Heart className="w-4 h-4 fill-[#F5B817]" />
                        </div>
                        <div className="space-y-0.5">
                          <h4 className="text-xs font-bold text-[#1F2421]">
                            Direct Impact on Young Lives
                          </h4>
                          <p className="text-[11px] text-[#4B5563] leading-relaxed">
                            Connecting rural school scholars directly with role models who pave the path to higher education.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Decorative Background Offset Frame */}
                  <div className="absolute -bottom-3 -right-3 -z-10 w-full h-full rounded-3xl bg-[#F5B817]/20 border border-[#F5B817]/40" />
                </div>
              </motion.div>
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
