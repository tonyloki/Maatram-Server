"use client";

import React, { Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  CheckCircle2,
  ShieldAlert,
  ArrowRight,
  Home,
} from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function ConfirmationContent() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "your email address";
  const status = searchParams.get("status") || "PENDING_APPROVAL";
  const parentalClaimed = searchParams.get("parental_consent_claimed") === "true";

  return (
    <Card className="max-w-2xl mx-auto p-8 sm:p-12 bg-white border-[#EBE6DD] shadow-xl rounded-3xl text-center space-y-6">
      <div className="w-16 h-16 rounded-full bg-[#F0FDF4] border border-[#86EFAC] flex items-center justify-center text-[#15803D] mx-auto">
        <CheckCircle2 className="w-9 h-9" />
      </div>

      <div className="space-y-2">
        <div className="inline-flex items-center gap-2">
          <Badge variant="warning">
            Status: {status.replace(/_/g, " ")}
          </Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#1F2421]">
          Volunteer Application Submitted!
        </h1>
        <p className="text-sm text-[#4B5563] max-w-lg mx-auto leading-relaxed">
          Thank you for joining the Maatram community. Your registration for <span className="font-semibold text-[#1F2421]">{email}</span> has been received and logged in our system.
        </p>
      </div>

      {/* Safeguarding Notice if Under-18 */}
      {parentalClaimed && (
        <div className="text-left p-4 rounded-2xl bg-[#FFFBEB] border border-[#FCD34D] space-y-2 text-xs text-[#92400E]">
          <div className="flex items-center gap-2 font-bold uppercase tracking-wider">
            <ShieldAlert className="w-4 h-4 text-[#D97706]" />
            <span>Under-18 Parental Consent Verification Notice</span>
          </div>
          <p className="leading-relaxed">
            You indicated that you are under 18 years of age. While your parental consent declaration has been recorded, full event eligibility remains <span className="font-bold">PENDING</span> until our safeguarding team verifies consent with your parent/guardian.
          </p>
        </div>
      )}

      {/* What Happens Next Roadmap */}
      <div className="text-left p-6 rounded-2xl bg-[#FAF8F3] border border-[#EBE6DD] space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-[#1F2421]">
          What Happens Next?
        </h3>
        <div className="space-y-3 text-xs text-[#4B5563]">
          <div className="flex items-start gap-3">
            <div className="w-5 h-5 rounded-full bg-[#F5B817] text-white flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
              1
            </div>
            <div>
              <span className="font-bold text-[#1F2421]">Administrative Review: </span>
              Maatram team members verify your academic college/registration number or employer details.
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-5 h-5 rounded-full bg-[#F5B817] text-white flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
              2
            </div>
            <div>
              <span className="font-bold text-[#1F2421]">Account Approval: </span>
              Upon successful verification, your account status transitions to <span className="font-semibold text-[#15803D]">APPROVED</span>.
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-5 h-5 rounded-full bg-[#F5B817] text-white flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
              3
            </div>
            <div>
              <span className="font-bold text-[#1F2421]">Event Participation: </span>
              You can sign in, subscribe for upcoming school visits or mock interviews, and earn verified volunteering credits!
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
        <Link href="/login" className="w-full sm:w-auto">
          <Button variant="primary" size="md" className="w-full sm:w-auto px-6">
            <span>Proceed to Login</span>
            <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        </Link>
        <Link href="/" className="w-full sm:w-auto">
          <Button variant="outline" size="md" className="w-full sm:w-auto px-6">
            <Home className="w-4 h-4 mr-1.5" />
            <span>Return to Home</span>
          </Button>
        </Link>
      </div>
    </Card>
  );
}

export default function ConfirmationPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="home" />

      <main className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <Suspense
          fallback={
            <div className="bg-white rounded-3xl p-10 border border-[#EBE6DD] animate-pulse space-y-4 text-center max-w-xl mx-auto w-full">
              <div className="h-12 bg-gray-200 rounded-full w-12 mx-auto" />
              <div className="h-6 bg-gray-200 rounded w-1/2 mx-auto" />
              <div className="h-4 bg-gray-100 rounded w-3/4 mx-auto" />
            </div>
          }
        >
          <ConfirmationContent />
        </Suspense>
      </main>

      <PublicFooter />
    </div>
  );
}
