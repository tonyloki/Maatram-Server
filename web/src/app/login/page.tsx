"use client";

import React, { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Lock,
  Mail,
  AlertCircle,
  Clock,
  Ban,
} from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/lib/auth-context";
import { Logo } from "@/components/ui/logo";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectPath = searchParams.get("redirect") || "/";

  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusNotice, setStatusNotice] = useState<{
    status: string;
    message: string;
    tone: "warning" | "error" | "info";
  } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setErrorMessage("Please enter both email address and password.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setStatusNotice(null);

    try {
      const response = await login(email.trim().toLowerCase(), password);

      // Inspect account status according to backend enum
      const userStatus = response.user.status;

      if (userStatus === "PENDING" || userStatus === "PENDING_APPROVAL") {
        setStatusNotice({
          status: userStatus,
          message:
            "Your volunteer application is currently under administrative review. Once approved, you will have full access to event registrations and dashboards.",
          tone: "warning",
        });
        setIsLoading(false);
        return;
      }

      if (userStatus === "REJECTED") {
        setStatusNotice({
          status: userStatus,
          message:
            "Your volunteer application was not accepted at this time. Please contact volunteers@maatramfoundation.org for inquiries.",
          tone: "error",
        });
        setIsLoading(false);
        return;
      }

      if (userStatus === "SUSPENDED") {
        setStatusNotice({
          status: userStatus,
          message:
            "Your account has been temporarily suspended by an administrator. Please reach out to support for resolution.",
          tone: "error",
        });
        setIsLoading(false);
        return;
      }

      // Approved volunteer or staff member
      router.push(redirectPath);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Invalid email or password. Please try again.";
      setErrorMessage(msg);
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
        <h1 className="text-2xl font-extrabold text-[#1F2421]">Welcome Back</h1>
        <p className="text-xs text-[#6B7280]">
          Sign in to your Maatram volunteering account
        </p>
      </div>

      {/* Generic Error Alert */}
      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-[#FEF2F2] border border-[#FCA5A5] text-[#991B1B] text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Account Status Notice */}
      {statusNotice && (
        <div
          className={`p-4 rounded-xl border text-xs space-y-2 ${
            statusNotice.tone === "warning"
              ? "bg-[#FFFBEB] border-[#FCD34D] text-[#92400E]"
              : "bg-[#FEF2F2] border-[#F87171] text-[#991B1B]"
          }`}
        >
          <div className="flex items-center gap-2 font-bold uppercase tracking-wider">
            {statusNotice.tone === "warning" ? (
              <Clock className="w-4 h-4 text-[#D97706]" />
            ) : (
              <Ban className="w-4 h-4 text-[#DC2626]" />
            )}
            <span>Status: {statusNotice.status}</span>
          </div>
          <p className="leading-relaxed">{statusNotice.message}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-[#374151] mb-1.5">
            Email Address
          </label>
          <div className="relative">
            <Mail className="w-4 h-4 text-[#9CA3AF] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="email"
              required
              autoComplete="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full text-xs bg-[#FAF8F3] border border-[#D1D5DB] rounded-xl pl-9 pr-3 py-2.5 text-[#1F2421] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:bg-white transition-all"
            />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-xs font-semibold text-[#374151]">
              Password
            </label>
          </div>
          <div className="relative">
            <Lock className="w-4 h-4 text-[#9CA3AF] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="password"
              required
              autoComplete="current-password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
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
          {isLoading ? "Signing in..." : "Sign In"}
        </Button>
      </form>

      {/* Register Prompt */}
      <div className="pt-4 border-t border-[#EBE6DD] text-center text-xs text-[#6B7280]">
        <span>Don&apos;t have a volunteer account? </span>
        <Link href="/register" className="font-bold text-[#B45309] hover:underline">
          Register here
        </Link>
      </div>
    </Card>
  );
}

export default function LoginPage() {
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
            <LoginForm />
          </Suspense>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
}
