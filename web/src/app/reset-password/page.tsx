"use client";

import React, { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Lock, Mail, KeyRound, ArrowLeft, AlertCircle, CheckCircle2 } from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Logo } from "@/components/ui/logo";
import { apiClient } from "@/lib/api-client";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialEmail = searchParams.get("email") || "";

  const [email, setEmail] = useState(initialEmail);
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email.trim() || !otp.trim() || !newPassword) {
      setErrorMessage("Please fill in all required fields.");
      return;
    }

    if (otp.trim().length !== 6 || !/^\d{6}$/.test(otp.trim())) {
      setErrorMessage("OTP must be exactly 6 numeric digits.");
      return;
    }

    if (newPassword.length < 8) {
      setErrorMessage("New password must be at least 8 characters long.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setErrorMessage("Passwords do not match. Please re-enter identical passwords.");
      return;
    }

    setIsLoading(true);

    try {
      await apiClient.post("/auth/password-reset/confirm", {
        email: email.trim().toLowerCase(),
        otp: otp.trim(),
        new_password: newPassword,
      });
      setIsSuccess(true);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setErrorMessage(e.message || "Failed to reset password. OTP may be invalid or expired.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="p-8 sm:p-10 bg-white border-[#EBE6DD] shadow-lg rounded-3xl space-y-6">
      <div className="text-center space-y-2">
        <div className="flex justify-center mb-2">
          <Logo href="/" width={120} height={55} priority />
        </div>
        <h1 className="text-2xl font-extrabold text-[#1F2421]">Create New Password</h1>
        <p className="text-xs text-[#6B7280]">
          Enter the 6-digit OTP sent to your email and your new secure password.
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
              <span>Password Reset Completed</span>
            </div>
            <p className="leading-relaxed">
              Your account password has been updated securely. You can now sign in with your new credentials.
            </p>
          </div>

          <Link href="/login" className="block w-full">
            <Button variant="primary" size="md" className="w-full h-11 text-xs font-bold gap-2">
              Proceed to Sign In
            </Button>
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#374151] mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-4 h-4 text-[#9CA3AF]" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full text-xs bg-[#FAF8F3] border border-[#D1D5DB] rounded-xl pl-9 pr-3 py-2.5 text-[#1F2421] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:bg-white transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#374151] mb-1.5">
              6-Digit Verification OTP
            </label>
            <div className="relative">
              <KeyRound className="absolute left-3 top-3 w-4 h-4 text-[#9CA3AF]" />
              <input
                type="text"
                maxLength={6}
                required
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                placeholder="123456"
                className="w-full text-xs font-mono tracking-widest bg-[#FAF8F3] border border-[#D1D5DB] rounded-xl pl-9 pr-3 py-2.5 text-[#1F2421] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:bg-white transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#374151] mb-1.5">
              New Password (min. 8 characters)
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-4 h-4 text-[#9CA3AF]" />
              <input
                type="password"
                required
                minLength={8}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full text-xs bg-[#FAF8F3] border border-[#D1D5DB] rounded-xl pl-9 pr-3 py-2.5 text-[#1F2421] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:bg-white transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#374151] mb-1.5">
              Confirm New Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-4 h-4 text-[#9CA3AF]" />
              <input
                type="password"
                required
                minLength={8}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
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
            {isLoading ? "Updating Password..." : "Reset Password"}
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
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="home" />

      <main className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <Suspense
            fallback={
              <div className="bg-white rounded-3xl p-10 border border-[#EBE6DD] animate-pulse space-y-4 text-center">
                <div className="h-8 bg-gray-200 rounded w-1/2 mx-auto" />
                <div className="h-4 bg-gray-100 rounded w-3/4 mx-auto" />
                <div className="h-10 bg-gray-200 rounded" />
              </div>
            }
          >
            <ResetPasswordForm />
          </Suspense>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
}

