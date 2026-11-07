"use client";

import React, { Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  XCircle,
  Mail,
  Home,
  HelpCircle,
  RefreshCw,
  FileText,
  AlertTriangle,
} from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function RejectedContent() {
  const searchParams = useSearchParams();
  const reason =
    searchParams.get("reason") ||
    "Your application did not meet our verification criteria or category eligibility requirements at this time.";
  const name = searchParams.get("name") || "Volunteer Applicant";

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <Card className="p-8 sm:p-10 bg-white border-[#EBE6DD] shadow-xl rounded-3xl space-y-8 text-center">
        {/* Soft Red Indicator */}
        <div className="relative mx-auto w-20 h-20 flex items-center justify-center">
          <div className="relative w-20 h-20 rounded-full bg-gradient-to-tr from-[#FEE2E2] to-[#FEF2F2] border-2 border-[#EF4444] flex items-center justify-center shadow-md">
            <XCircle className="w-10 h-10 text-[#DC2626]" />
          </div>
        </div>

        {/* Heading & Context */}
        <div className="space-y-3">
          <Badge variant="error" className="px-3.5 py-1 text-xs font-bold tracking-wide uppercase">
            Application Status Notice
          </Badge>
          <h1 className="text-2xl sm:text-3xl font-black text-[#1F2421]">
            Application Update for {name}
          </h1>
          <p className="text-sm text-[#4B5563] max-w-lg mx-auto leading-relaxed">
            Thank you for your sincere interest in mentoring with the <span className="font-bold text-[#1F2421]">Maatram Foundation</span>. Following administrative review, we regret to inform you that we are unable to accept your volunteering application at this time.
          </p>
        </div>

        {/* Official Reason Card */}
        <div className="bg-[#FEF2F2] border border-[#FCA5A5] rounded-2xl p-6 text-left space-y-3">
          <h2 className="text-xs font-black uppercase tracking-wider text-[#991B1B] flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-[#DC2626]" />
            Administrative Feedback / Reason
          </h2>
          <p className="text-xs sm:text-sm text-[#7F1D1D] leading-relaxed font-medium bg-white/70 p-3.5 rounded-xl border border-[#F87171]/40">
            &ldquo;{reason}&rdquo;
          </p>
          <p className="text-[11px] text-[#991B1B]">
            All volunteer intake decisions are reviewed according to strict safety, institutional guidelines, and volunteer cohort quotas.
          </p>
        </div>

        {/* Reapplication & Inquiries Support */}
        <div className="p-4 rounded-xl bg-[#FAF8F3] border border-[#EFECE6] text-xs text-[#4B5563] flex flex-col sm:flex-row items-center justify-between gap-3 text-left">
          <div className="flex items-center gap-2.5">
            <HelpCircle className="w-4 h-4 text-[#B45309] shrink-0" />
            <span>Believe this decision was reached in error or wish to provide updated documentation?</span>
          </div>
          <a
            href="mailto:volunteers@maatramfoundation.org?subject=Application%20Inquiry"
            className="font-bold text-[#B45309] hover:underline flex items-center gap-1 shrink-0"
          >
            <Mail className="w-3.5 h-3.5" />
            Inquire via Email
          </a>
        </div>

        {/* Navigation Actions */}
        <div className="pt-2 flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/">
            <Button variant="outline" size="md" className="w-full sm:w-auto text-xs font-bold gap-2">
              <Home className="w-4 h-4" />
              Return to Home
            </Button>
          </Link>
          <Link href="/register">
            <Button variant="primary" size="md" className="w-full sm:w-auto text-xs font-bold gap-2">
              <RefreshCw className="w-4 h-4" />
              Submit New Application
            </Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}

export default function OnboardingRejectedPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="volunteer" />
      <main className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <Suspense
          fallback={
            <div className="w-full max-w-xl bg-white rounded-3xl p-10 border border-[#EBE6DD] animate-pulse space-y-4 text-center">
              <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto" />
              <div className="h-6 bg-gray-200 rounded w-1/2 mx-auto" />
              <div className="h-4 bg-gray-100 rounded w-3/4 mx-auto" />
            </div>
          }
        >
          <RejectedContent />
        </Suspense>
      </main>
      <PublicFooter />
    </div>
  );
}

