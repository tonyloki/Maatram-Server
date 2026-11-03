"use client";

import React from "react";
import Link from "next/link";
import {
  Sparkles,
  ArrowRight,
  Quote,
} from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function ImpactPage() {
  const stories = [
    {
      theme: "First-Generation College Scholars",
      focus: "Higher Education Enablement",
      narrative:
        "Students from families dependent on daily wage farming and manual labor who receive full scholarships to top-tier universities. Through Maatram, their entire higher education journey is supported alongside peer mentorship from senior scholars.",
      impactResult: "Generational transformation from rural subsistence to financial stability.",
    },
    {
      theme: "School Career Awareness Drives",
      focus: "Government School Outreach",
      narrative:
        "Volunteers conduct interactive workshops in rural higher secondary schools. Many students learn for the very first time about professional entrance examinations, college application processes, and scholarship avenues available to them.",
      impactResult: "Demystified higher education pathways for students with limited career exposure.",
    },
    {
      theme: "Corporate Mock Interviews & Readiness",
      focus: "Corporate Volunteer Engagement",
      narrative:
        "Industry professionals and HR managers volunteer their weekends to conduct realistic practice interviews. Scholars receive structured feedback on communication, body language, domain knowledge, and resume drafting.",
      impactResult: "Scholars enter campus placement drives with confidence and polished interview readiness.",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="impact" />

      <main className="flex-1">
        {/* HERO SECTION */}
        <section className="py-16 md:py-20 bg-white border-b border-[#EBE6DD]">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-4">
            <span className="text-xs font-bold uppercase tracking-wider text-[#B45309] bg-[#FFF8E7] px-3.5 py-1.5 rounded-full border border-[#F5B817]/30 inline-block">
              Qualitative Social Impact
            </span>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#1F2421] tracking-tight">
              Measuring Impact Through Changed Lives & Generational Progress
            </h1>
            <p className="text-base sm:text-lg text-[#4B5563] leading-relaxed max-w-2xl mx-auto">
              Behind every volunteering hour logged in our portal is a real student gaining the mentorship,
              confidence, and institutional support needed to lift their entire family out of poverty.
            </p>
          </div>
        </section>

        {/* NARRATIVE PILLARS */}
        <section className="py-16 md:py-24">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
            <div className="text-center max-w-2xl mx-auto">
              <h2 className="text-2xl sm:text-3xl font-bold text-[#1F2421]">
                Real Transformations, Real Opportunities
              </h2>
              <p className="text-sm text-[#6B7280] mt-2">
                Our volunteering initiatives focus on three critical milestones in a student’s educational lifecycle.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {stories.map((s) => (
                <Card key={s.theme} className="p-6 bg-white border-[#EBE6DD] flex flex-col justify-between shadow-sm">
                  <div>
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-[#FFF8E7] text-[#946C00] border border-[#F5B817]/30 inline-block mb-4">
                      {s.focus}
                    </span>
                    <h3 className="text-lg font-bold text-[#1F2421] mb-3">{s.theme}</h3>
                    <p className="text-xs text-[#4B5563] leading-relaxed mb-6">
                      {s.narrative}
                    </p>
                  </div>
                  <div className="pt-4 border-t border-[#F3F4F6]">
                    <span className="text-xs font-medium text-[#15803D] flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>{s.impactResult}</span>
                    </span>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* THE VOLUNTEER COMMITMENT */}
        <section className="py-16 bg-white border-y border-[#EBE6DD]">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="bg-[#FAF8F3] rounded-3xl p-8 sm:p-12 border border-[#EBE6DD] relative">
              <Quote className="w-10 h-10 text-[#F5B817]/40 mb-4" />
              <blockquote className="text-base sm:text-lg text-[#1F2421] font-medium leading-relaxed italic">
                “When an alumnus returns to conduct a mock interview with a student from the exact same rural government school they graduated from, the impact is immeasurable. The student realizes: If they did it, I can do it too.”
              </blockquote>
              <div className="mt-6 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#F5B817] flex items-center justify-center font-bold text-white text-sm">
                  M
                </div>
                <div>
                  <div className="text-sm font-bold text-[#1F2421]">Maatram Volunteering Council</div>
                  <div className="text-xs text-[#6B7280]">Community Mentorship & Education Program</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CALL TO ACTION */}
        <section className="py-16 text-center">
          <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
            <h2 className="text-2xl sm:text-3xl font-bold text-[#1F2421]">
              Create Your Own Impact Story
            </h2>
            <p className="text-sm text-[#4B5563]">
              Join our active community of student, alumni, and corporate volunteers today.
            </p>
            <div className="pt-2 flex justify-center gap-4">
              <Link href="/register">
                <Button variant="primary" size="md">
                  <span>Register Now</span>
                  <ArrowRight className="w-4 h-4 ml-1.5" />
                </Button>
              </Link>
              <Link href="/events">
                <Button variant="outline" size="md">
                  View Volunteering Drives
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
