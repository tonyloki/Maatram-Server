import React from "react";
import Link from "next/link";
import { Logo } from "@/components/ui/logo";
import { Heart, Mail, MapPin, ExternalLink } from "lucide-react";

export function PublicFooter() {
  return (
    <footer className="border-t border-[#EBE6DD] bg-white text-[#1F2421]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand & Purpose */}
          <div className="md:col-span-2 space-y-4">
            <Logo href="/" width={140} height={65} priority />
            <p className="text-sm text-[#6B7280] max-w-md leading-relaxed">
              Maatram Educational and Charitable Trust empowers students from rural and economically disadvantaged
              backgrounds through higher education scholarships, life-skills mentoring, and professional career readiness.
            </p>
            <div className="flex items-center gap-2 text-xs text-[#9CA3AF]">
              <span>Made with dedication for social transformation</span>
              <Heart className="w-3.5 h-3.5 text-[#F5B817] fill-[#F5B817]" />
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-xs font-bold tracking-wider uppercase text-[#1F2421] mb-4">
              Explore Portal
            </h3>
            <ul className="space-y-2.5 text-sm text-[#4B5563]">
              <li>
                <Link href="/" className="hover:text-[#F5B817] transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-[#F5B817] transition-colors">
                  About Maatram
                </Link>
              </li>
              <li>
                <Link href="/events" className="hover:text-[#F5B817] transition-colors">
                  Volunteer Opportunities
                </Link>
              </li>
              <li>
                <Link href="/impact" className="hover:text-[#F5B817] transition-colors">
                  Our Impact
                </Link>
              </li>
              <li>
                <Link href="/register" className="hover:text-[#F5B817] transition-colors font-medium text-[#B45309]">
                  Become a Volunteer
                </Link>
              </li>
            </ul>
          </div>

          {/* Community & Contact */}
          <div>
            <h3 className="text-xs font-bold tracking-wider uppercase text-[#1F2421] mb-4">
              Connect With Us
            </h3>
            <ul className="space-y-3 text-sm text-[#4B5563]">
              <li className="flex items-start gap-2.5">
                <MapPin className="w-4 h-4 text-[#F5B817] shrink-0 mt-0.5" />
                <span>Chennai, Tamil Nadu, India</span>
              </li>
              <li className="flex items-start gap-2.5">
                <Mail className="w-4 h-4 text-[#F5B817] shrink-0 mt-0.5" />
                <span>volunteers@maatramfoundation.org</span>
              </li>
              <li className="pt-2">
                <a
                  href="https://maatramfoundation.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#B45309] hover:underline"
                >
                  <span>Official Maatram Trust</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-[#EBE6DD] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#9CA3AF]">
          <p>© 2026 Maatram Educational and Charitable Trust. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span>Volunteer & Gamification Portal</span>
            <span>•</span>
            <span>Privacy & DPDP Compliant</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
