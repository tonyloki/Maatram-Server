"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Trophy,
  Users,
  Calendar,
  Clock,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Sliders,
  Layers,
} from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, KpiCard } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/input";
import { ConsentSwitch } from "@/components/ui/switch";
import { Dialog } from "@/components/ui/dialog";
import { PublicHeader } from "@/components/navigation/public-header";
import { VolunteerSidebar } from "@/components/navigation/volunteer-sidebar";
import { AdminSidebar } from "@/components/navigation/admin-sidebar";
import {
  staggerContainer,
  staggerItem,
  podiumVariants,
  crownBounceVariants,
} from "@/lib/animations";

export default function DesignSystemShowcasePage() {
  const [buttonLoading, setButtonLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [navPreview, setNavPreview] = useState<"public" | "volunteer" | "admin">("public");

  // Consent Switches State
  const [consents, setConsents] = useState({
    leaderboard_visible: true,
    name_visible: false,
    thank_you_emails: true,
    linkedin_content: false,
    contact_available: false,
    media_usage: true,
  });

  return (
    <div className="min-h-screen bg-[#FAF8F3] text-[#1F2421]">
      {/* 1. Interactive Navigation Foundation Preview */}
      <div className="bg-white border-b border-[#EBE6DD] px-4 py-3 sticky top-0 z-50 shadow-xs">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-[#946C00] bg-[#FFF8E7] px-2.5 py-1 rounded-full border border-[#F5B817]/40">
              Milestone 1 Showcase
            </span>
            <span className="text-xs text-[#6B7280] hidden sm:inline">
              Maatram Design Tokens & Component Library
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-[#FAF8F3] p-1 rounded-xl border border-[#EBE6DD]">
            <span className="text-xs font-medium text-[#6B7280] px-2">Navigation Mode:</span>
            <button
              onClick={() => setNavPreview("public")}
              className={`text-xs px-3 py-1 rounded-lg font-medium transition-all ${
                navPreview === "public" ? "bg-white text-[#1F2421] shadow-xs" : "text-[#6B7280]"
              }`}
            >
              Public
            </button>
            <button
              onClick={() => setNavPreview("volunteer")}
              className={`text-xs px-3 py-1 rounded-lg font-medium transition-all ${
                navPreview === "volunteer" ? "bg-white text-[#1F2421] shadow-xs" : "text-[#6B7280]"
              }`}
            >
              Volunteer
            </button>
            <button
              onClick={() => setNavPreview("admin")}
              className={`text-xs px-3 py-1 rounded-lg font-medium transition-all ${
                navPreview === "admin" ? "bg-[#16171A] text-white shadow-xs" : "text-[#6B7280]"
              }`}
            >
              Admin
            </button>
          </div>
        </div>
      </div>

      {/* Render Dynamic Navigation Preview */}
      {navPreview === "public" && <PublicHeader />}
      
      <div className="flex">
        {navPreview === "volunteer" && <VolunteerSidebar className="hidden md:flex" />}
        {navPreview === "admin" && <AdminSidebar className="hidden md:flex" adminName="Ramesh N." adminRole="Admin" />}

        {/* Main Showcase Body */}
        <main className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
          {/* Section: Typography & Official Branding */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#6B7280]">
              <Layers className="w-4 h-4 text-[#F5B817]" />
              <span>Section 1: Official Brand Identity & Typography Hierarchy</span>
            </div>

            <div className="bg-white rounded-2xl border border-[#EBE6DD] p-6 sm:p-8 flex flex-col md:flex-row items-center gap-8">
              <div className="flex-shrink-0 text-center p-4 bg-[#FAF8F3] rounded-xl border border-[#EBE6DD]">
                <Logo width={160} height={80} priority />
                <p className="text-[11px] text-[#6B7280] mt-2 font-mono">2.014:1 Preserved Ratio</p>
              </div>

              <div className="space-y-2 flex-1">
                <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-[#1F2421]">
                  Volunteer for a Better Tomorrow
                </h1>
                <p className="text-base text-[#6B7280] leading-relaxed">
                  Join Maatram Foundation&apos;s community of students, alumni, and professionals to create
                  meaningful educational opportunities across government schools.
                </p>
                <div className="pt-2 flex flex-wrap gap-2">
                  <Badge variant="brand">Inter Typeface</Badge>
                  <Badge variant="neutral">WCAG 2.1 AA Compliant</Badge>
                  <Badge variant="success">Ivory Canvas (#FAF8F3)</Badge>
                </div>
              </div>
            </div>
          </section>

          {/* Section: Buttons & Micro-Interactions */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#6B7280]">
                <Sparkles className="w-4 h-4 text-[#F5B817]" />
                <span>Section 2: Reusable Button Primitives & Interactive States</span>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setButtonLoading(!buttonLoading)}
              >
                {buttonLoading ? "Stop Spinner" : "Toggle Loading Spinner"}
              </Button>
            </div>

            <div className="bg-white rounded-2xl border border-[#EBE6DD] p-6 space-y-6">
              <div className="flex flex-wrap items-center gap-4">
                <Button variant="primary" isLoading={buttonLoading}>
                  Primary Action (Gold Pill)
                </Button>
                <Button variant="outline" isLoading={buttonLoading}>
                  Outline Button
                </Button>
                <Button variant="ghost" isLoading={buttonLoading}>
                  Ghost Button
                </Button>
                <Button variant="destructive" isLoading={buttonLoading}>
                  Decline / Withdraw
                </Button>
              </div>

              <div className="flex flex-wrap items-center gap-4 pt-4 border-t border-[#EBE6DD]">
                <span className="text-xs font-medium text-[#6B7280] mr-2">Button Sizes:</span>
                <Button size="sm" variant="primary">Small (32px)</Button>
                <Button size="md" variant="primary">Medium Default (40px)</Button>
                <Button size="lg" variant="primary">Large Hero CTA (48px)</Button>
              </div>
            </div>
          </section>

          {/* Section: Status Tokens & Badges */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#6B7280]">
              <CheckCircle2 className="w-4 h-4 text-[#03543F]" />
              <span>Section 3: Semantic Status Badge Matrix</span>
            </div>

            <div className="bg-white rounded-2xl border border-[#EBE6DD] p-6 flex flex-wrap gap-3">
              <Badge variant="success">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Approved / Selected
              </Badge>
              <Badge variant="warning">
                <AlertTriangle className="w-3.5 h-3.5 mr-1" /> Waitlisted / Pending Review
              </Badge>
              <Badge variant="error">
                <XCircle className="w-3.5 h-3.5 mr-1" /> Rejected / Cancelled
              </Badge>
              <Badge variant="attention">
                <Clock className="w-3.5 h-3.5 mr-1" /> Incomplete Check-Out
              </Badge>
              <Badge variant="neutral">
                Draft / Archived
              </Badge>
              <Badge variant="brand">
                <Trophy className="w-3.5 h-3.5 mr-1 text-[#946C00]" /> Gold Contributor
              </Badge>
            </div>
          </section>

          {/* Section: Metric Cards & Grids */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#6B7280]">
              <Users className="w-4 h-4 text-[#F5B817]" />
              <span>Section 4: Responsive KPI & Content Cards (Staggered Entrance)</span>
            </div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              animate="show"
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
            >
              <motion.div variants={staggerItem}>
                <KpiCard
                  title="Total Volunteers"
                  value="1,248"
                  icon={<Users className="w-5 h-5" />}
                  subtitle="Active in program"
                  trend="+12% this cycle"
                  trendPositive
                />
              </motion.div>
              <motion.div variants={staggerItem}>
                <KpiCard
                  title="Pending Approvals"
                  value="42"
                  icon={<Clock className="w-5 h-5" />}
                  subtitle="Applications in queue"
                  trend="Requires action"
                  trendPositive={false}
                />
              </motion.div>
              <motion.div variants={staggerItem}>
                <KpiCard
                  title="Total Events"
                  value="18"
                  icon={<Calendar className="w-5 h-5" />}
                  subtitle="This academic year"
                />
              </motion.div>
              <motion.div variants={staggerItem}>
                <KpiCard
                  title="Verified Hours"
                  value="4,820"
                  icon={<Trophy className="w-5 h-5" />}
                  subtitle="Community impact"
                  trend="Canonical ledger"
                  trendPositive
                />
              </motion.div>
            </motion.div>
          </section>

          {/* Section: Form Inputs & Affirmative Consent Switches */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#6B7280]">
              <Sliders className="w-4 h-4 text-[#F5B817]" />
              <span>Section 5: Forms & Affirmative Privacy Switches (Module 4)</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left Column: Form Controls */}
              <Card className="space-y-4">
                <CardHeader>
                  <CardTitle>Standard Input Elements</CardTitle>
                  <CardDescription>Strict validation matching Pydantic schemas.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Input
                    label="Full Name"
                    placeholder="e.g. Priya Sundaram"
                    defaultValue="Priya S."
                    required
                  />
                  <Input
                    label="Mobile Number (E.164 Format)"
                    placeholder="+919876543210"
                    defaultValue="+919876543210"
                    helperText="International format with country code"
                    required
                  />
                  <Select label="Volunteer Category" defaultValue="STUDENT">
                    <option value="STUDENT">Student (College / Beneficiary)</option>
                    <option value="ALUMNI">Alumni (Working Professional)</option>
                    <option value="CORPORATE">Corporate Panelist</option>
                  </Select>
                </CardContent>
                <CardFooter>
                  <Button variant="primary" onClick={() => setDialogOpen(true)}>
                    Open Confirmation Dialog
                  </Button>
                </CardFooter>
              </Card>

              {/* Right Column: 6 Affirmative Consent Switches */}
              <Card className="space-y-4">
                <CardHeader>
                  <CardTitle>Affirmative Consent Controls</CardTitle>
                  <CardDescription>
                    All 6 dimensions default to false. Every switch produces an immutable audit record.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2.5">
                  <ConsentSwitch
                    id="consent-leaderboard"
                    title="1. Show Ranking on Community Leaderboard"
                    description="Display your points score on public leaderboards."
                    checked={consents.leaderboard_visible}
                    onChange={(val) => setConsents({ ...consents, leaderboard_visible: val })}
                  />
                  <ConsentSwitch
                    id="consent-name"
                    title="2. Display Full Name on Leaderboard"
                    description="If off, you will appear masked as 'Anonymous Volunteer'."
                    checked={consents.name_visible}
                    onChange={(val) => setConsents({ ...consents, name_visible: val })}
                  />
                  <ConsentSwitch
                    id="consent-email"
                    title="3. Receive Event Thank-You Emails"
                    description="Receive milestone recognition and completion messages."
                    checked={consents.thank_you_emails}
                    onChange={(val) => setConsents({ ...consents, thank_you_emails: val })}
                  />
                  <ConsentSwitch
                    id="consent-linkedin"
                    title="4. Allow LinkedIn Appreciation Mentions"
                    description="Include your name in drafted celebration posts."
                    checked={consents.linkedin_content}
                    onChange={(val) => setConsents({ ...consents, linkedin_content: val })}
                  />
                </CardContent>
              </Card>
            </div>
          </section>

          {/* Section: Motion Effects & Top 3 Podium Simulation */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#6B7280]">
              <Trophy className="w-4 h-4 text-[#F5B817]" />
              <span>Section 6: Framer Motion Top 3 Podium Simulation (Screen 5)</span>
            </div>

            <Card className="p-8">
              <div className="flex items-end justify-center gap-4 max-w-md mx-auto pt-8 pb-4">
                {/* Rank 2: Silver */}
                <div className="flex flex-col items-center flex-1">
                  <div className="w-12 h-12 rounded-full border-2 border-slate-300 bg-white flex items-center justify-center font-bold text-sm shadow-sm mb-2">
                    AK
                  </div>
                  <span className="text-xs font-bold text-[#1F2421]">Arun K.</span>
                  <span className="text-[11px] text-[#6B7280]">480 pts</span>
                  <motion.div
                    custom={0.1}
                    variants={podiumVariants}
                    initial="hidden"
                    animate="visible"
                    className="w-full h-24 bg-gradient-to-t from-slate-200 to-slate-100 rounded-t-xl flex items-center justify-center font-bold text-slate-500 mt-2 border border-slate-300 shadow-sm"
                  >
                    #2
                  </motion.div>
                </div>

                {/* Rank 1: Gold Center */}
                <div className="flex flex-col items-center flex-1">
                  <motion.div
                    variants={crownBounceVariants}
                    initial="hidden"
                    animate="visible"
                    className="text-[#F5B817] mb-1"
                  >
                    👑
                  </motion.div>
                  <div className="w-14 h-14 rounded-full border-2 border-[#F5B817] bg-[#FFF8E7] flex items-center justify-center font-bold text-sm shadow-md mb-2">
                    PS
                  </div>
                  <span className="text-xs font-bold text-[#1F2421]">Priya S.</span>
                  <span className="text-[11px] text-[#946C00] font-semibold">520 pts</span>
                  <motion.div
                    custom={0}
                    variants={podiumVariants}
                    initial="hidden"
                    animate="visible"
                    className="w-full h-32 bg-gradient-to-t from-[#F5B817] to-[#FED667] rounded-t-xl flex items-center justify-center font-bold text-[#1F2421] mt-2 border border-[#E5A800] shadow-md"
                  >
                    #1
                  </motion.div>
                </div>

                {/* Rank 3: Bronze */}
                <div className="flex flex-col items-center flex-1">
                  <div className="w-12 h-12 rounded-full border-2 border-amber-600/40 bg-white flex items-center justify-center font-bold text-sm shadow-sm mb-2">
                    SR
                  </div>
                  <span className="text-xs font-bold text-[#1F2421]">Sneha R.</span>
                  <span className="text-[11px] text-[#6B7280]">460 pts</span>
                  <motion.div
                    custom={0.2}
                    variants={podiumVariants}
                    initial="hidden"
                    animate="visible"
                    className="w-full h-16 bg-gradient-to-t from-amber-100 to-amber-50 rounded-t-xl flex items-center justify-center font-bold text-amber-800 mt-2 border border-amber-200 shadow-sm"
                  >
                    #3
                  </motion.div>
                </div>
              </div>
            </Card>
          </section>
        </main>
      </div>

      {/* Interactive Modal Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        title="Confirm Event Registration"
        description="Review event details before confirming participation."
        footer={
          <>
            <Button variant="ghost" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                alert("Action completed cleanly!");
                setDialogOpen(false);
              }}
            >
              Confirm Registration
            </Button>
          </>
        }
      >
        <p className="text-sm text-[#6B7280] leading-relaxed">
          You are registering for the <strong className="text-[#1F2421]">Government High School Visit</strong>.
          Attendance will be verified on site by the coordinator.
        </p>
      </Dialog>
    </div>
  );
}
