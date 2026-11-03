import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "Maatram — Volunteering & Gamification Portal",
  description:
    "Official volunteering portal for Maatram Educational Aid Foundation. Empowering students through school visits, mock interviews, and scholarship enablement.",
  icons: {
    icon: "/maatram_logo-removebg-preview.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-[#FAF8F3] text-[#1F2421]">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
