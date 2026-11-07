"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { CheckCircle2, XCircle, ArrowRight, Home, Loader2, Mail } from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { apiClient } from "@/lib/api-client";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";
  const email = searchParams.get("email") || "";

  const [status, setStatus] = useState<"loading" | "success" | "error">(
    token ? "loading" : "error"
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(
    token ? null : "Verification token is missing from the URL."
  );

  useEffect(() => {
    if (!token) return;

    let isMounted = true;

    const verify = async () => {
      try {
        await apiClient.post("/auth/verify-email", {
          token,
          email: email || undefined,
        });
        if (isMounted) {
          setStatus("success");
        }
      } catch (err: unknown) {
        if (isMounted) {
          const e = err as { message?: string };
          setStatus("error");
          setErrorMessage(
            e.message || "Email verification failed. The token may be invalid or expired."
          );
        }
      }
    };

    void verify();

    return () => {
      isMounted = false;
    };
  }, [token, email]);

  return (
    <Card className="p-8 sm:p-10 bg-white border-[#EBE6DD] shadow-lg rounded-3xl space-y-6 text-center max-w-lg mx-auto">
      {status === "loading" && (
        <div className="space-y-4 py-6">
          <Loader2 className="w-12 h-12 text-[#F5B817] animate-spin mx-auto" />
          <h1 className="text-xl font-bold text-[#1F2421]">Verifying Email Address...</h1>
          <p className="text-xs text-[#6B7280]">
            Please wait while we validate your token with the Maatram authentication server.
          </p>
        </div>
      )}

      {status === "success" && (
        <div className="space-y-6">
          <div className="w-16 h-16 rounded-full bg-[#ECFDF5] border-2 border-[#10B981] flex items-center justify-center mx-auto shadow-sm">
            <CheckCircle2 className="w-8 h-8 text-[#059669]" />
          </div>

          <div className="space-y-2">
            <h1 className="text-2xl font-extrabold text-[#1F2421]">Email Verified!</h1>
            <p className="text-xs text-[#4B5563] leading-relaxed max-w-sm mx-auto">
              Your email address has been successfully confirmed. Your volunteer account is now progressing through the verification pipeline.
            </p>
          </div>

          <div className="pt-2 flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/onboarding/pending">
              <Button variant="outline" size="md" className="w-full sm:w-auto text-xs font-bold gap-2">
                <span>View Application Status</span>
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="primary" size="md" className="w-full sm:w-auto text-xs font-bold gap-2">
                <span>Sign In to Account</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      )}

      {status === "error" && (
        <div className="space-y-6">
          <div className="w-16 h-16 rounded-full bg-[#FEF2F2] border-2 border-[#EF4444] flex items-center justify-center mx-auto shadow-sm">
            <XCircle className="w-8 h-8 text-[#DC2626]" />
          </div>

          <div className="space-y-2">
            <h1 className="text-2xl font-extrabold text-[#1F2421]">Verification Failed</h1>
            <p className="text-xs text-[#991B1B] bg-[#FEF2F2] border border-[#FCA5A5] p-3 rounded-xl max-w-md mx-auto">
              {errorMessage}
            </p>
          </div>

          <p className="text-xs text-[#6B7280] max-w-sm mx-auto">
            Verification tokens expire after 24 hours. If your link has expired, you can request a new verification link or sign in.
          </p>

          <div className="pt-2 flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/">
              <Button variant="outline" size="md" className="w-full sm:w-auto text-xs font-bold gap-2">
                <Home className="w-4 h-4" />
                <span>Return to Home</span>
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="primary" size="md" className="w-full sm:w-auto text-xs font-bold gap-2">
                <span>Sign In</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      )}
    </Card>
  );
}

export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="home" />

      <main className="flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-lg">
          <Suspense
            fallback={
              <div className="bg-white rounded-3xl p-10 border border-[#EBE6DD] animate-pulse space-y-4 text-center">
                <div className="w-12 h-12 bg-gray-200 rounded-full mx-auto" />
                <div className="h-6 bg-gray-200 rounded w-1/2 mx-auto" />
                <div className="h-4 bg-gray-100 rounded w-3/4 mx-auto" />
              </div>
            }
          >
            <VerifyEmailContent />
          </Suspense>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
}

