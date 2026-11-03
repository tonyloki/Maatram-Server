import React, { Suspense } from "react";
import { VolunteerShell } from "@/components/navigation/volunteer-shell";

export default function VolunteerPortalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#FAF8F3]">
          <div className="w-10 h-10 border-3 border-primary-500 border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <VolunteerShell>{children}</VolunteerShell>
    </Suspense>
  );
}
