"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, ArrowLeft, ArrowRight, AlertCircle, CheckCircle2 } from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Logo } from "@/components/ui/logo";
import { apiClient } from "@/lib/api-client";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setErrorMessage("Please enter your registered email address.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      await apiClient.post("/auth/password-reset/request", {
        email: email.trim().toLowerCase(),
      });
      setIsSuccess(true);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setErrorMessage(e.message || "Failed to initiate password reset. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="home" />

      <main className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <Card className="p-8 sm:p-10 bg-white border-[#EBE6DD] shadow-lg rounded-3xl space-y-6">
            <div className="text-center space-y-2">
              <div className="flex justify-center mb-2">
                <Logo href="/" width={120} height={55} priority />
              </div>
              <h1 className="text-2xl font-extrabold text-[#1F2421]">Reset Password</h1>
              <p className="text-xs text-[#6B7280]">
                Enter your email address and we&apos;ll send you a 6-digit verification OTP.
              </p>
            </div>

            {errorMessage && (
              <div className="p-3.5 rounded-xl bg-[#FEF2F2] border border-[#FCA5A5] text-[#991B1B] text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            {isSuccess ? (
              <div className="space-y-6 text-center">
                <div className="p-4 rounded-xl bg-[#ECFDF5] border border-[#A7F3D0] text-[#065F46] text-xs space-y-2 text-left">
                  <div className="flex items-center gap-2 font-bold">
                    <CheckCircle2 className="w-4 h-4 text-[#059669]" />
                    <span>OTP Dispatched Successfully</span>
                  </div>
                  <p className="leading-relaxed">
                    If an active volunteer account exists for <span className="font-semibold text-[#064E3B]">{email}</span>, a 6-digit numeric OTP has been generated. Please check your inbox and enter the code to choose a new password.
                  </p>
                </div>

                <Link
                  href={`/reset-password?email=${encodeURIComponent(email.trim().toLowerCase())}`}
                  className="block w-full"
                >
                  <Button variant="primary" size="md" className="w-full h-11 text-xs font-bold gap-2">
                    <span>Enter 6-Digit OTP</span>
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </Link>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-[#374151] mb-1.5">
                    Registered Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 w-4 h-4 text-[#9CA3AF]" />
                    <input
                      type="email"
                      required
                      placeholder="name@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full text-xs bg-[#FAF8F3] border border-[#D1D5DB] rounded-xl pl-9 pr-3 py-2.5 text-[#1F2421] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:bg-white transition-all"
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  className="w-full h-11 text-sm font-bold shadow-md shadow-[#F5B817]/20 mt-2"
                  disabled={isLoading}
                >
                  {isLoading ? "Sending OTP..." : "Send Reset Code"}
                </Button>
              </form>
            )}

            <div className="pt-4 border-t border-[#EBE6DD] text-center text-xs text-[#6B7280]">
              <Link
                href="/login"
                className="font-bold text-[#B45309] hover:underline inline-flex items-center gap-1.5"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back to Sign In</span>
              </Link>
            </div>
          </Card>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
}

