import React, { Suspense } from "react";
import { AdminShell } from "@/components/navigation/admin-shell";

export default function AdminPortalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#FAF8F3]">
          <div className="w-10 h-10 border-3 border-charcoal-900 border-t-[#F5B817] rounded-full animate-spin" />
        </div>
      }
    >
      <AdminShell>{children}</AdminShell>
    </Suspense>
  );
}

