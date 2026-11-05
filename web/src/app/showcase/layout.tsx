import { Metadata } from "next";
import React from "react";

export const metadata: Metadata = {
  title: "Maatram Design Showcase (Internal QA Only)",
  description: "Internal design system showcase and visual asset gallery for development review only.",
  robots: {
    index: false,
    follow: false,
  },
};

export default function ShowcaseLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

