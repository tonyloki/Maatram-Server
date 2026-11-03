"use client";

import React from "react";
import Link from "next/link";
import {
  GraduationCap,
  ShieldCheck,
  Users,
  Target,
  ArrowRight,
  BookOpen,
  CheckCircle2,
} from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function AboutPage() {
  const values = [
    {
      title: "Educational Equity",
      description:
        "Every deserving student should have access to higher education regardless of financial background or geographic barriers.",
      icon: GraduationCap,
    },
    {
      title: "Ethical Safeguarding",
      description:
        "Strict background verification, parental consent for young scholars, and full DPDP compliance ensure a safe environment.",
      icon: ShieldCheck,
    },
    {
      title: "Sustainable Mentorship",
      description:
        "Continuous engagement where students become mentors themselves, creating an enduring generational ripple effect.",
      icon: Users,
    },
    {
      title: "Holistic Development",
      description:
        "Beyond technical curricula, we focus on communication, interview preparation, emotional resilience, and ethics.",
      icon: Target,
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="about" />

      <main className="flex-1">
        {/* HERO BANNER */}
        <section className="py-16 md:py-24 border-b border-[#EBE6DD] bg-white">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <span className="text-xs font-bold uppercase tracking-wider text-[#B45309] bg-[#FFF8E7] px-3.5 py-1.5 rounded-full border border-[#F5B817]/30">
              Our Mission & Philosophy
            </span>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#1F2421] mt-5 tracking-tight">
              Empowering First-Generation Learners Through Community Mentorship
            </h1>
            <p className="text-base sm:text-lg text-[#4B5563] mt-5 leading-relaxed">
              Maatram Educational and Charitable Trust bridges the gap between rural and underprivileged youth and world-class
              higher education opportunities across premier engineering, arts, and science institutions.
            </p>
          </div>
        </section>

        {/* CORE STORY */}
        <section className="py-16 md:py-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
              <div className="space-y-5">
                <div className="inline-flex items-center gap-2 text-xs font-bold text-[#B45309] uppercase tracking-wider">
                  <BookOpen className="w-4 h-4" />
                  <span>The Maatram Story</span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold text-[#1F2421]">
                  Transforming Dreams Into Degree Certificates
                </h2>
                <p className="text-sm text-[#4B5563] leading-relaxed">
                  Founded with the conviction that education is the ultimate equalizer, Maatram Foundation identifies
                  economically vulnerable students who have achieved stellar academic scores but cannot afford college tuition,
                  hostel expenses, or study materials.
                </p>
                <p className="text-sm text-[#4B5563] leading-relaxed">
                  Through partnerships with reputed educational institutions and a vast network of dedicated volunteers,
                  Maatram provides 100% free higher education, continuous mentoring, and career launchpads.
                </p>
                <div className="pt-2">
                  <Link href="/register">
                    <Button variant="primary" size="md">
                      <span>Join as a Mentor</span>
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                </div>
              </div>

              <div className="bg-white rounded-3xl p-8 border border-[#EBE6DD] shadow-sm space-y-6">
                <h3 className="text-lg font-bold text-[#1F2421] border-b border-[#EBE6DD] pb-4">
                  What Sets Our Volunteering Apart
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-[#15803D] shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-semibold text-[#1F2421]">Direct Beneficiary Interaction</h4>
                      <p className="text-xs text-[#6B7280] mt-0.5">
                        Volunteers interact directly with students in school visits and mock interviews, seeing real change firsthand.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-[#15803D] shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-semibold text-[#1F2421]">Transparent Point & Hour Ledgers</h4>
                      <p className="text-xs text-[#6B7280] mt-0.5">
                        Every hour of service is digitally tracked, verified by event coordinators, and officially credited to your profile.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-[#15803D] shrink-0 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-semibold text-[#1F2421]">Alumni-Led Continuity</h4>
                      <p className="text-xs text-[#6B7280] mt-0.5">
                        Former Maatram scholars return as alumni mentors, providing empathetic, relatable guidance to the next batch.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CORE PILLARS */}
        <section className="py-16 bg-white border-y border-[#EBE6DD]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto mb-12">
              <span className="text-xs font-bold uppercase tracking-wider text-[#B45309]">
                Guiding Principles
              </span>
              <h2 className="text-3xl font-bold text-[#1F2421] mt-2">
                Our Core Values
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {values.map((val) => {
                const IconComponent = val.icon;
                return (
                  <Card key={val.title} className="p-6 border-[#EBE6DD] bg-[#FAF8F3]">
                    <div className="w-10 h-10 rounded-xl bg-white border border-[#EBE6DD] flex items-center justify-center text-[#B45309] mb-4">
                      <IconComponent className="w-5 h-5" />
                    </div>
                    <h3 className="text-base font-bold text-[#1F2421] mb-2">{val.title}</h3>
                    <p className="text-xs text-[#6B7280] leading-relaxed">{val.description}</p>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        {/* GET INVOLVED CTA */}
        <section className="py-16 text-center">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
            <h2 className="text-2xl sm:text-3xl font-bold text-[#1F2421]">
              Be Part of the Next Success Story
            </h2>
            <p className="text-sm text-[#4B5563] max-w-xl mx-auto">
              Whether you can contribute 2 hours a month or lead weekend school awareness drives, your time helps shape a student’s future.
            </p>
            <div className="pt-4 flex justify-center gap-4">
              <Link href="/register">
                <Button variant="primary" size="md">
                  Register as a Volunteer
                </Button>
              </Link>
              <Link href="/events">
                <Button variant="outline" size="md">
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
