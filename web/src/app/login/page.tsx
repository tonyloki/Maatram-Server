"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import {
  Lock,
  Mail,
  AlertCircle,
  Eye,
  EyeOff,
  ArrowRight,
  Loader2,
  Clock,
  Ban,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectPath = searchParams.get("redirect") || "/";

  const { user, isAuthenticated, isLoading: authLoading, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusNotice, setStatusNotice] = useState<{
    status: string;
    message: string;
    tone: "warning" | "error" | "info";
  } | null>(null);

  // If already authenticated, redirect to appropriate portal
  useEffect(() => {
    if (!authLoading && isAuthenticated && user) {
      if (
        redirectPath &&
        redirectPath !== "/" &&
        redirectPath !== "/events" &&
        redirectPath !== "/login"
      ) {
        router.replace(redirectPath);
      } else if (user.role === "SUPER_ADMIN" || user.role === "ADMIN") {
        router.replace("/admin/dashboard");
      } else {
        router.replace("/volunteer/dashboard");
      }
    }
  }, [authLoading, isAuthenticated, user, redirectPath, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setErrorMessage("Please enter both your email address and password.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setStatusNotice(null);

    try {
      const response = await login(email.trim().toLowerCase(), password);
      const userStatus = response.user.status;

      if (userStatus === "PENDING" || userStatus === "PENDING_APPROVAL" || userStatus === "PENDING_VERIFICATION") {
        const queryParams = new URLSearchParams({
          email: response.user.email || email.trim(),
          name: (response.user.email || email).split("@")[0],
        });
        router.push(`/onboarding/pending?${queryParams.toString()}`);
        return;
      }

      if (userStatus === "REJECTED") {
        const queryParams = new URLSearchParams({
          email: response.user.email || email.trim(),
          name: (response.user.email || email).split("@")[0],
        });
        router.push(`/onboarding/rejected?${queryParams.toString()}`);
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

      // Approved volunteer or staff member: direct to portal
      if (
        redirectPath &&
        redirectPath !== "/" &&
        redirectPath !== "/events" &&
        redirectPath !== "/login"
      ) {
        router.push(redirectPath);
      } else {
        const role = response.user.role;
        if (role === "SUPER_ADMIN" || role === "ADMIN") {
          router.push("/admin/dashboard");
        } else {
          router.push("/volunteer/dashboard");
        }
      }
    } catch (err: unknown) {
      let msg = "Invalid email or password. Please try again.";
      if (err instanceof Error) {
        msg = err.message;
      } else if (typeof err === "object" && err !== null && "message" in err) {
        msg = String((err as { message: unknown }).message);
      }
      setErrorMessage(msg);
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#FAF8F0] flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-5xl bg-white rounded-3xl sm:rounded-[36px] border border-[#EBE7DF] shadow-[0_10px_35px_-5px_rgba(0,0,0,0.05)] overflow-hidden grid grid-cols-1 lg:grid-cols-12 min-h-[640px]">
        {/* Left Side: Welcome Panel matching Reference */}
        <div className="lg:col-span-6 bg-[#FAF8F0] p-8 sm:p-12 lg:p-14 flex flex-col justify-between relative overflow-hidden border-b lg:border-b-0 lg:border-r border-[#EFECE6]">
          {/* Subtle Organic Background Accents */}
          <div className="absolute top-0 right-0 w-80 h-80 bg-[#FFF5DA] rounded-full blur-3xl opacity-60 pointer-events-none -mr-20 -mt-20" />
          <div className="absolute bottom-0 left-0 w-60 h-60 bg-[#F5EED9] rounded-full blur-2xl opacity-50 pointer-events-none -ml-10 -mb-10" />

          {/* Logo & Top Copy */}
          <div className="relative z-10">
            <Link href="/" className="inline-block transition-opacity hover:opacity-90 mb-8 sm:mb-12">
              <Image
                src="/maatram_logo-removebg-preview.png"
                alt="Maatram Foundation"
                width={150}
                height={55}
                priority
                className="h-10 sm:h-12 w-auto object-contain"
              />
            </Link>

            <h1 className="text-3xl sm:text-4xl lg:text-[40px] font-extrabold text-[#1F2421] tracking-tight leading-[1.2]">
              Welcome Back
            </h1>
            <p className="text-xl sm:text-2xl font-bold text-[#1F2421] mt-2">
              Together for a <span className="text-[#D97706]">Better Tomorrow</span>
            </p>

            <p className="mt-4 text-sm sm:text-base text-[#555E58] leading-relaxed max-w-md">
              Log in to continue your volunteering journey and make an impact.
            </p>
          </div>

          {/* Volunteer Group Photo at Bottom */}
          <div className="relative z-10 mt-8 sm:mt-12">
            <div className="relative w-full rounded-2xl overflow-hidden shadow-sm border border-[#EBE7DF] bg-stone-100 aspect-[16/9]">
              <Image
                src="/assets/maatram/photography/volunteers-team-hero.jpg"
                alt="Maatram Volunteers Group"
                fill
                priority
                sizes="(max-width: 1024px) 100vw, 480px"
                className="object-cover object-center"
              />
            </div>
          </div>
        </div>

        {/* Right Side: Login Form Card matching Reference */}
        <div className="lg:col-span-6 p-8 sm:p-12 lg:p-14 flex flex-col justify-center bg-white relative">
          <div className="w-full max-w-md mx-auto">
            {/* Center Logo on mobile / top of right card */}
            <div className="text-center mb-6">
              <div className="inline-block mb-3">
                <Image
                  src="/maatram_logo-removebg-preview.png"
                  alt="Maatram Foundation"
                  width={130}
                  height={48}
                  className="h-9 sm:h-10 w-auto object-contain mx-auto"
                />
              </div>
              <h2 className="text-2xl sm:text-[26px] font-extrabold text-[#1F2421] tracking-tight">
                Login to Your Account
              </h2>
              <p className="text-xs sm:text-sm text-[#6B7280] mt-1">
                Welcome back! Please sign in to continue.
              </p>
            </div>

            {/* Account Status / Lifecycle Notice */}
            {statusNotice && (
              <div
                className={`mb-5 p-4 rounded-2xl text-xs sm:text-sm flex items-start gap-3 border ${
                  statusNotice.tone === "warning"
                    ? "bg-amber-50 border-amber-200 text-amber-900"
                    : statusNotice.tone === "error"
                    ? "bg-red-50 border-red-200 text-red-900"
                    : "bg-blue-50 border-blue-200 text-blue-900"
                }`}
              >
                {statusNotice.tone === "warning" && (
                  <Clock className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                )}
                {statusNotice.tone === "error" && (
                  <Ban className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                )}
                <div className="flex-1">
                  <p className="font-bold">
                    {statusNotice.status === "PENDING"
                      ? "Application Under Review"
                      : "Account Notice"}
                  </p>
                  <p className="mt-0.5 opacity-90 leading-relaxed">
                    {statusNotice.message}
                  </p>
                </div>
              </div>
            )}

            {/* Error Message */}
            {errorMessage && (
              <div className="mb-5 p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs sm:text-sm flex items-center gap-2.5">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
                <span>{errorMessage}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
              {/* Email Address */}
              <div>
                <label
                  htmlFor="email"
                  className="block text-xs sm:text-sm font-semibold text-[#1F2421] mb-1.5"
                >
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#9CA3AF] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email address"
                    className="w-full pl-10 pr-4 py-2.5 sm:py-3 rounded-xl border border-[#D5D0C7] text-sm text-[#1F2421] placeholder-[#9CA3AF] bg-[#FAF8F0]/40 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:border-transparent transition-all"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label
                    htmlFor="password"
                    className="block text-xs sm:text-sm font-semibold text-[#1F2421]"
                  >
                    Password
                  </label>
                  <Link
                    href="/forgot-password"
                    className="text-xs font-semibold text-[#D97706] hover:text-[#B45309] transition-colors"
                  >
                    Forgot password?
                  </Link>
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#9CA3AF] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full pl-10 pr-11 py-2.5 sm:py-3 rounded-xl border border-[#D5D0C7] text-sm text-[#1F2421] placeholder-[#9CA3AF] bg-[#FAF8F0]/40 focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:border-transparent transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-[#9CA3AF] hover:text-[#4B5563] focus:outline-none transition-colors"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full mt-2 inline-flex items-center justify-center gap-2 py-3 sm:py-3.5 px-4 rounded-xl bg-[#F5B817] hover:bg-[#E5A807] text-[#1F2421] font-bold text-sm sm:text-base shadow-sm transition-all transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
                    <span>Signing In...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In</span>
                    <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
                  </>
                )}
              </button>
            </form>

            {/* Registration link */}
            <p className="mt-8 text-center text-xs sm:text-sm text-[#6B7280]">
              Don&apos;t have a volunteer account?{" "}
              <Link
                href="/register"
                className="font-bold text-[#D97706] hover:text-[#B45309] hover:underline transition-colors"
              >
                Register here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#FAF8F0] flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-[#F5B817] animate-spin" />
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
