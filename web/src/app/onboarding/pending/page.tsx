"use client";

import React, { Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  Clock,
  ShieldCheck,
  Mail,
  Home,
  CheckCircle2,
  HelpCircle,
  FileText,
} from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function PendingContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "your registered email address";
  const name = searchParams.get("name") || "Volunteer";

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      <Card className="p-8 sm:p-10 bg-white border-[#EBE6DD] shadow-xl rounded-3xl space-y-8 text-center">
        {/* Animated Amber Status Icon */}
        <div className="relative mx-auto w-20 h-20 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full bg-[#FEF3C7] animate-ping opacity-25" />
          <div className="relative w-20 h-20 rounded-full bg-gradient-to-tr from-[#FDE68A] to-[#FEF3C7] border-2 border-[#F5B817] flex items-center justify-center shadow-md">
            <Clock className="w-10 h-10 text-[#B45309]" />
          </div>
        </div>

        {/* Heading & Context */}
        <div className="space-y-3">
          <Badge variant="warning" className="px-3.5 py-1 text-xs font-bold tracking-wide uppercase">
            Application Under Review
          </Badge>
          <h1 className="text-2xl sm:text-3xl font-black text-[#1F2421]">
            Welcome, {name}!
          </h1>
          <p className="text-sm text-[#4B5563] max-w-lg mx-auto leading-relaxed">
            Thank you for registering with the <span className="font-bold text-[#1F2421]">Maatram Foundation</span> volunteering community. Your application is currently under administrative review by our verification team.
          </p>
        </div>

        {/* Verification Steps Card */}
        <div className="bg-[#FAF8F3] border border-[#EFECE6] rounded-2xl p-6 text-left space-y-4">
          <h2 className="text-xs font-black uppercase tracking-wider text-[#6B7280] flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#F5B817]" />
            What happens next?
          </h2>

          <div className="space-y-3 text-xs text-[#374151]">
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-[#FEF3C7] text-[#92400E] font-black text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                1
              </div>
              <div>
                <p className="font-bold text-[#1F2421]">Application Verification</p>
                <p className="text-[#6B7280]">Our coordinator team reviews your profile details, category documentation, and background suitability.</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-[#FEF3C7] text-[#92400E] font-black text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                2
              </div>
              <div>
                <p className="font-bold text-[#1F2421]">Decision Notification</p>
                <p className="text-[#6B7280]">
                  You will receive an official decision email at <span className="font-semibold text-[#1F2421]">{email}</span> within 2–3 business days.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-[#FEF3C7] text-[#92400E] font-black text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                3
              </div>
              <div>
                <p className="font-bold text-[#1F2421]">Event & Dashboard Unlocking</p>
                <p className="text-[#6B7280]">Once approved, your account grants complete access to browse volunteering drives, register for school visits, and log contributions.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Support Helpdesk Callout */}
        <div className="p-4 rounded-xl bg-[#FFFBEB] border border-[#FDE68A] text-xs text-[#92400E] flex items-center justify-between gap-3 text-left">
          <div className="flex items-center gap-2.5">
            <HelpCircle className="w-4 h-4 text-[#D97706] shrink-0" />
            <span>Have an urgent question regarding your application status?</span>
          </div>
          <a
            href="mailto:volunteers@maatramfoundation.org"
            className="font-bold text-[#B45309] hover:underline flex items-center gap-1 shrink-0"
          >
            <Mail className="w-3.5 h-3.5" />
            Contact Team
          </a>
        </div>

        {/* Navigation Action Buttons */}
        <div className="pt-2 flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/">
            <Button variant="outline" size="md" className="w-full sm:w-auto text-xs font-bold gap-2">
              <Home className="w-4 h-4" />
              Return to Home
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="primary" size="md" className="w-full sm:w-auto text-xs font-bold gap-2">
              Check Login Status
            </Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}

export default function OnboardingPendingPage() {
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
          <PendingContent />
        </Suspense>
      </main>
      <PublicFooter />
    </div>
  );
}

