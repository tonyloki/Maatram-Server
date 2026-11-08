"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Menu, X, LogOut, ArrowRight, LayoutDashboard } from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

interface PublicHeaderProps {
  activeNav?: string;
}

export function PublicHeader({ activeNav = "home" }: PublicHeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();

  const portalHref = user?.role?.includes("ADMIN")
    ? "/admin/dashboard"
    : "/volunteer/dashboard";
  const eventsHref = user?.role?.includes("ADMIN")
    ? "/admin/events"
    : "/volunteer/events";

  const navLinks = [
    { key: "home", label: "Home", href: "/" },
    { key: "about", label: "About", href: "/about" },
    { key: "volunteer", label: "Volunteer", href: isAuthenticated ? eventsHref : "/events" },
    { key: "impact", label: "Impact", href: "/impact" },
    ...(isAuthenticated ? [{ key: "dashboard", label: "Dashboard", href: portalHref }] : []),
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#EBE6DD] bg-[#FAF8F3]/95 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex h-20 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo */}
        <div className="flex items-center gap-3">
          <Logo href="/" width={130} height={60} priority />
        </div>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.key}
              href={link.href}
              className={`text-sm font-medium transition-colors hover:text-[#1F2421] ${
                activeNav === link.key ? "text-[#1F2421] font-semibold" : "text-[#4B5563]"
              }`}
            >
              {link.label}
            </Link>
          ))}
          {!isAuthenticated && (
            <Link
              href="/login"
              className={`text-sm font-medium transition-colors hover:text-[#1F2421] ${
                activeNav === "login" ? "text-[#1F2421] font-semibold" : "text-[#4B5563]"
              }`}
            >
              Login
            </Link>
          )}
        </nav>

        {/* Desktop Action Buttons */}
        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated && user ? (
            <div className="flex items-center gap-3">
              <Link href={portalHref}>
                <button
                  type="button"
                  className="px-5 py-2.5 rounded-xl bg-[#F5B817] hover:bg-[#E0A714] text-[#1F2421] font-bold text-sm transition-all shadow-xs flex items-center gap-1.5"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  <span>Dashboard</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
              <Link
                href={user.role.includes("ADMIN") ? "/admin/settings" : "/volunteer/profile"}
                className="text-xs font-medium text-[#4B5563] hover:text-[#1F2421] bg-white border border-[#EBE6DD] px-3 py-1.5 rounded-full transition-colors"
                title="View Profile"
              >
                {user.email}
              </Link>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => logout()}
                className="text-[#6B7280] hover:text-[#DC2626]"
              >
                <LogOut className="w-4 h-4 mr-1.5" />
                Logout
              </Button>
            </div>
          ) : (
            <Link href="/register">
              <button
                type="button"
                className="px-6 py-2.5 rounded-xl bg-[#F5B817] hover:bg-[#E0A714] text-[#1F2421] font-bold text-sm transition-all shadow-xs"
              >
                Get Started
              </button>
            </Link>
          )}
        </div>

        {/* Mobile Hamburger Button */}
        <div className="flex md:hidden">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg text-[#1F2421] hover:bg-black/5"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-[#EBE6DD] bg-white px-4 pt-2 pb-6 space-y-3">
          <div className="flex flex-col space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.key}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2 rounded-lg text-base font-medium ${
                  activeNav === link.key
                    ? "bg-[#FFF8E7] text-[#946C00] font-semibold"
                    : "text-[#6B7280] hover:bg-[#FAF8F3]"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
          <div className="pt-4 border-t border-[#EBE6DD] flex flex-col gap-2.5">
            {isAuthenticated && user ? (
              <>
                <Link href={portalHref} onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="primary" className="w-full font-bold justify-center">
                    <LayoutDashboard className="w-4 h-4 mr-2" />
                    Go to Dashboard
                  </Button>
                </Link>
                <Link
                  href={user.role.includes("ADMIN") ? "/admin/settings" : "/volunteer/profile"}
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-xs text-[#6B7280] px-3 py-1 hover:underline"
                >
                  Signed in as {user.email}
                </Link>
                <Button
                  variant="outline"
                  className="w-full justify-center text-[#DC2626]"
                  onClick={() => {
                    setMobileMenuOpen(false);
                    logout();
                  }}
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="outline" className="w-full">
                    Login
                  </Button>
                </Link>
                <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
                  <Button variant="primary" className="w-full">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
