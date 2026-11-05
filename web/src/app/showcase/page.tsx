"use client";

import React, { useState } from "react";
import Link from "next/link";
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
  Search,
  ArrowRight,
  Mail,
  Shield,
  HelpCircle,
  Flame,
  Award,
  Palette,
} from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, KpiCard } from "@/components/ui/card";
import { Input, Textarea, Select } from "@/components/ui/input";
import { Switch, ConsentSwitch } from "@/components/ui/switch";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, ConfirmDialog } from "@/components/ui/dialog";
import { SegmentedTabs, UnderlineTabs } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";
import { Avatar } from "@/components/ui/avatar";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { PublicHeader } from "@/components/navigation/public-header";
import { VolunteerSidebar } from "@/components/navigation/volunteer-sidebar";
import { AdminSidebar } from "@/components/navigation/admin-sidebar";

export default function DesignSystemShowcasePage() {
  const [buttonLoading, setButtonLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [navPreview, setNavPreview] = useState<"public" | "volunteer" | "admin">("public");

  // Tab State
  const [activeSegmentedTab, setActiveSegmentedTab] = useState("upcoming");
  const [activeUnderlineTab, setActiveUnderlineTab] = useState("personal");

  // Input states
  const [bioText, setBioText] = useState("Passionate about volunteering and mentoring scholars in rural schools.");
  const [singleSwitch, setSingleSwitch] = useState(true);
  const [singleCheckbox, setSingleCheckbox] = useState(true);

  // All 6 Canonical Affirmative Consent Preferences State
  const [consents, setConsents] = useState({
    leaderboard_visible: true,
    name_visible: false,
    thank_you_emails: true,
    linkedin_content: false,
    contact_available: false,
    media_usage: true,
  });

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-[#1F2421]">
      {/* 1. Interactive Navigation Foundation Preview Bar */}
      <div className="bg-white border-b border-[#EFECE6] px-4 py-3 sticky top-0 z-50 shadow-xs">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="text-xs font-bold uppercase tracking-wider text-[#946C00] bg-[#FFF8E7] px-3 py-1 rounded-full border border-[#F5B817]/40">
              Milestone 6.1 Showcase
            </span>
            <span className="text-xs text-[#4B5563] hidden sm:inline">
              Maatram Canonical Tokens & Reusable Component Library
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/showcase/assets"
              className="text-xs px-3 py-1.5 rounded-xl font-bold bg-[#F5B817] text-[#1F2421] hover:bg-[#E5A800] transition-all shadow-xs inline-flex items-center gap-1.5"
            >
              <Palette className="w-3.5 h-3.5" />
              <span>Asset Library (M6.1A)</span>
            </Link>

            <div className="flex items-center gap-1.5 bg-[#FAF8F5] p-1 rounded-xl border border-[#EFECE6]">
              <span className="text-xs font-semibold text-[#4B5563] px-2">Navigation Mode:</span>
            <button
              onClick={() => setNavPreview("public")}
              className={`text-xs px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                navPreview === "public" ? "bg-white text-[#1F2421] shadow-xs" : "text-[#4B5563] hover:text-[#1F2421]"
              }`}
            >
              Public
            </button>
            <button
              onClick={() => setNavPreview("volunteer")}
              className={`text-xs px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                navPreview === "volunteer" ? "bg-white text-[#1F2421] shadow-xs" : "text-[#4B5563] hover:text-[#1F2421]"
              }`}
            >
              Volunteer
            </button>
            <button
              onClick={() => setNavPreview("admin")}
              className={`text-xs px-3 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                navPreview === "admin" ? "bg-[#16171A] text-white shadow-xs" : "text-[#4B5563] hover:text-[#1F2421]"
              }`}
            >
              Admin
            </button>
          </div>
        </div>
      </div>
    </div>

      {/* Render Dynamic Navigation Preview */}
      {navPreview === "public" && <PublicHeader />}

      <div className="flex min-w-0">
        {navPreview === "volunteer" && (
          <div className="hidden md:block w-64 flex-shrink-0">
            <VolunteerSidebar className="sticky top-14 h-[calc(100vh-3.5rem)]" />
          </div>
        )}
        {navPreview === "admin" && (
          <div className="hidden md:block w-64 flex-shrink-0">
            <AdminSidebar adminName="Ramesh N." adminRole="Admin" className="sticky top-14 h-[calc(100vh-3.5rem)]" />
          </div>
        )}

        {/* Main Showcase Body */}
        <main className="flex-1 min-w-0 max-w-6xl mx-auto p-4 md:p-8 space-y-12">
          {/* Section: Introduction */}
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FFF8E7] text-[#946C00] text-xs font-bold mb-3 border border-[#F5B817]/40">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Design System Foundations</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-[#1F2421]">
              Maatram Component Library
            </h1>
            <p className="text-sm md:text-base text-[#4B5563] mt-2 max-w-2xl leading-relaxed">
              Shared visual foundations, design tokens, accessible components, and motion conventions calibrated to match the mentor reference designs.
            </p>
          </div>

          {/* Section 1: Color Tokens & Brand Resolution */}
          <section className="space-y-4">
            <SectionHeader
              title="1. Color Tokens & Brand Resolution"
              description="Canonical primary brand gold (#F5B817) with WCAG AA compliant supporting shades."
            />
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              <div className="p-4 rounded-2xl bg-[#F5B817] text-[#1F2421] shadow-xs">
                <span className="block text-xs font-bold uppercase tracking-wider">Primary Gold</span>
                <span className="block text-sm font-extrabold mt-1">#F5B817</span>
                <span className="block text-[10px] opacity-80 mt-2">Canonical Brand Token</span>
              </div>
              <div className="p-4 rounded-2xl bg-[#E5A800] text-[#1F2421] shadow-xs">
                <span className="block text-xs font-bold uppercase tracking-wider">Hover Gold</span>
                <span className="block text-sm font-extrabold mt-1">#E5A800</span>
                <span className="block text-[10px] opacity-80 mt-2">Interactive Hover</span>
              </div>
              <div className="p-4 rounded-2xl bg-[#FFF8E7] text-[#946C00] border border-[#F5B817]/40 shadow-xs">
                <span className="block text-xs font-bold uppercase tracking-wider">Surface Subtle</span>
                <span className="block text-sm font-extrabold mt-1">#FFF8E7</span>
                <span className="block text-[10px] text-[#946C00] mt-2">Active Rail & Fills</span>
              </div>
              <div className="p-4 rounded-2xl bg-[#FAF8F5] text-[#1F2421] border border-[#EFECE6] shadow-xs">
                <span className="block text-xs font-bold uppercase tracking-wider">Warm Canvas</span>
                <span className="block text-sm font-extrabold mt-1">#FAF8F5</span>
                <span className="block text-[10px] text-[#4B5563] mt-2">Global Page Canvas</span>
              </div>
              <div className="p-4 rounded-2xl bg-white text-[#1F2421] border border-[#EFECE6] shadow-xs">
                <span className="block text-xs font-bold uppercase tracking-wider">Card Surface</span>
                <span className="block text-sm font-extrabold mt-1">#FFFFFF</span>
                <span className="block text-[10px] text-[#4B5563] mt-2">Floating White Cards</span>
              </div>
              <div className="p-4 rounded-2xl bg-[#1F2421] text-white shadow-xs">
                <span className="block text-xs font-bold uppercase tracking-wider">Primary Text</span>
                <span className="block text-sm font-extrabold mt-1">#1F2421</span>
                <span className="block text-[10px] opacity-80 mt-2">High Contrast Charcoal</span>
              </div>
            </div>
          </section>

          {/* Section 2: Typography Scale */}
          <section className="space-y-4">
            <SectionHeader
              title="2. Typography Hierarchy"
              description="Rhythmic type scale adhering to 8pt spatial grid."
            />
            <Card className="space-y-4 divide-y divide-[#EFECE6]">
              <div className="pb-3">
                <span className="text-[11px] font-bold uppercase text-[#946C00] tracking-wider block mb-1">Display Title (Hero) — 32px Bold</span>
                <p className="text-2xl md:text-3xl font-bold tracking-tight text-[#1F2421]">
                  Transform Education Through Meaningful Mentorship
                </p>
              </div>
              <div className="pt-3 pb-3">
                <span className="text-[11px] font-bold uppercase text-[#946C00] tracking-wider block mb-1">Section Header (H2) — 22px Bold</span>
                <p className="text-lg md:text-xl font-bold tracking-tight text-[#1F2421]">
                  Your Contribution at a Glance
                </p>
              </div>
              <div className="pt-3 pb-3">
                <span className="text-[11px] font-bold uppercase text-[#946C00] tracking-wider block mb-1">Card Title (H3) — 18px Bold</span>
                <p className="text-base md:text-lg font-bold text-[#1F2421]">
                  School Visit – Government High School
                </p>
              </div>
              <div className="pt-3">
                <span className="text-[11px] font-bold uppercase text-[#946C00] tracking-wider block mb-1">Body Text — 15px Regular</span>
                <p className="text-sm md:text-base text-[#4B5563] leading-relaxed">
                  Join a passionate community of students, alumni, and industry professionals guiding first-generation scholars across rural and underserved schools to achieve higher education and career success.
                </p>
              </div>
            </Card>
          </section>

          {/* Section 3: Buttons & Interactive Feedback */}
          <section className="space-y-4">
            <SectionHeader
              title="3. Buttons & Action Primitives"
              description="Tactile buttons with hover lift, active scale, and loading states."
            />
            <Card className="space-y-6">
              <div className="flex flex-wrap items-center gap-3">
                <Button variant="primary" rightIcon={<ArrowRight className="w-4 h-4" />}>
                  Primary Button
                </Button>
                <Button variant="secondary">
                  Secondary Pill
                </Button>
                <Button variant="outline">
                  Outline Button
                </Button>
                <Button variant="ghost">
                  Ghost Link
                </Button>
                <Button variant="destructive">
                  Destructive Action
                </Button>
                <Button
                  variant="primary"
                  isLoading={buttonLoading}
                  onClick={() => {
                    setButtonLoading(true);
                    setTimeout(() => setButtonLoading(false), 1500);
                  }}
                >
                  {buttonLoading ? "Saving..." : "Click to Test Loading"}
                </Button>
              </div>

              <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-[#EFECE6]">
                <span className="text-xs font-semibold text-[#4B5563] mr-2">Sizes:</span>
                <Button size="sm" variant="primary">Small (sm)</Button>
                <Button size="md" variant="primary">Medium (md)</Button>
                <Button size="lg" variant="primary">Large (lg)</Button>
                <Button size="md" rounded="xl" variant="outline">Rounded-XL Variant</Button>
                <Button size="md" variant="primary" disabled>Disabled State</Button>
              </div>
            </Card>
          </section>

          {/* Section 4: Badges & Category Delivery Tags */}
          <section className="space-y-4">
            <SectionHeader
              title="4. Badges & Delivery Format Tags"
              description="Tailored pastel pills directly sampled from mentor references."
            />
            <Card className="space-y-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#4B5563] block mb-2.5">
                  Semantic Status Badges:
                </span>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="success" dot>Approved</Badge>
                  <Badge variant="warning" dot>Pending Review</Badge>
                  <Badge variant="error" dot>Suspended</Badge>
                  <Badge variant="attention" dot>Attention</Badge>
                  <Badge variant="neutral">Draft</Badge>
                  <Badge variant="brand">Student Volunteer</Badge>
                </div>
              </div>

              <div className="pt-3 border-t border-[#EFECE6]">
                <span className="text-xs font-bold uppercase tracking-wider text-[#4B5563] block mb-2.5">
                  Delivery Mode & Event Category Tags (from Mentor References):
                </span>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="onsite">Onsite</Badge>
                  <Badge variant="online">Online</Badge>
                  <Badge variant="school-visit">School Visit</Badge>
                  <Badge variant="mock-interview">Mock Interview</Badge>
                  <Badge variant="bgv">BGV Support</Badge>
                  <Badge variant="admissions">Admissions</Badge>
                  <Badge variant="panel">Panel Interview</Badge>
                </div>
              </div>
            </Card>
          </section>

          {/* Section 5: Cards & KPI Metric Primitives */}
          <section className="space-y-4">
            <SectionHeader
              title="5. Cards & KPI Metrics"
              description="Floating white containers with subtle borders and ambient elevation."
            />
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <KpiCard
                title="Volunteering Points"
                value="580"
                subtitle="Events × 10 + Hours × 2"
                icon={<Trophy className="w-5 h-5" />}
              />
              <KpiCard
                title="Approved Hours"
                value="48.0"
                subtitle="Verified service"
                trend="+4.5 hrs"
                trendPositive={true}
                icon={<Clock className="w-5 h-5" />}
              />
              <KpiCard
                title="Events Attended"
                value="8"
                subtitle="Completed drives"
                icon={<Calendar className="w-5 h-5" />}
              />
              <KpiCard
                title="Current Rank"
                value="#1"
                subtitle="Top 1% Mentor"
                trend="Promoted"
                trendPositive={true}
                icon={<Award className="w-5 h-5" />}
              />
            </div>
          </section>

          {/* Section 6: Tabs & Navigation Controls */}
          <section className="space-y-4">
            <SectionHeader
              title="6. Segmented & Underline Tabs"
              description="Replicating the My Activity, Leaderboard, and Profile tab mechanics."
            />
            <Card className="space-y-6">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#4B5563] block mb-2.5">
                  Segmented Pill Tabs (Reference 4 & 5 style):
                </span>
                <SegmentedTabs
                  tabs={[
                    { id: "upcoming", label: "Upcoming", badge: 0 },
                    { id: "ongoing", label: "Ongoing", badge: 0 },
                    { id: "past", label: "Past", badge: 8 },
                    { id: "ledger", label: "Points Ledger" },
                  ]}
                  activeTab={activeSegmentedTab}
                  onChange={setActiveSegmentedTab}
                />
              </div>

              <div className="pt-3 border-t border-[#EFECE6]">
                <span className="text-xs font-bold uppercase tracking-wider text-[#4B5563] block mb-2.5">
                  Underline Tabs (Reference 6 style):
                </span>
                <UnderlineTabs
                  tabs={[
                    { id: "personal", label: "Personal Information" },
                    { id: "preferences", label: "Volunteer Preferences" },
                    { id: "consents", label: "Consents & Privacy" },
                    { id: "achievements", label: "Achievements" },
                  ]}
                  activeTab={activeUnderlineTab}
                  onChange={setActiveUnderlineTab}
                />
              </div>
            </Card>
          </section>

          {/* Section 7: Form Controls & Inputs */}
          <section className="space-y-4">
            <SectionHeader
              title="7. Form Controls & Inputs"
              description="Accessible form fields with error and helper text handling."
            />
            <Card className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Search Events"
                placeholder="Search by topic, school, or location..."
                leftIcon={<Search className="w-4 h-4" />}
              />
              <Select
                label="Delivery Mode"
                options={[
                  { label: "All Formats", value: "" },
                  { label: "Onsite Workshops", value: "onsite" },
                  { label: "Online Sessions", value: "online" },
                ]}
              />
              <Input
                label="First Name"
                defaultValue="Anand"
                required
              />
              <Input
                label="Email Address"
                defaultValue="anand.k@example.com"
                helperText="Read only identity identifier"
                disabled
              />
              <div className="md:col-span-2">
                <Textarea
                  label="Short Bio"
                  value={bioText}
                  onChange={(e) => setBioText(e.target.value)}
                  maxLength={200}
                  currentLength={bioText.length}
                />
              </div>
              <div className="flex items-center gap-6 pt-2">
                <div className="flex items-center gap-2.5">
                  <Switch checked={singleSwitch} onChange={setSingleSwitch} />
                  <span className="text-sm font-semibold text-[#1F2421]">Standalone Switch</span>
                </div>
                <Checkbox
                  id="demo-checkbox"
                  checked={singleCheckbox}
                  onChange={(e) => setSingleCheckbox(e.target.checked)}
                  label="I agree to portal terms"
                />
              </div>
            </Card>
          </section>

          {/* Section 8: All Six Affirmative Consent Switches */}
          <section className="space-y-4">
            <SectionHeader
              title="8. Affirmative Consent Switches (All 6 Dimensions)"
              description="Strict affirmative privacy controls bound to the canonical backend ConsentRecord model."
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <ConsentSwitch
                checked={consents.leaderboard_visible}
                onChange={(c) => setConsents({ ...consents, leaderboard_visible: c })}
                title="Leaderboard Visibility"
                description="Allow your participation and points to be visible on the public community leaderboard."
              />
              <ConsentSwitch
                checked={consents.name_visible}
                onChange={(c) => setConsents({ ...consents, name_visible: c })}
                title="Name Display on Leaderboard"
                description="Display your real name on rankings. If disabled, you will appear as 'Anonymous Volunteer'."
              />
              <ConsentSwitch
                checked={consents.thank_you_emails}
                onChange={(c) => setConsents({ ...consents, thank_you_emails: c })}
                title="Thank You & Milestone Emails"
                description="Receive celebration emails upon event completion and milestone achievements."
              />
              <ConsentSwitch
                checked={consents.linkedin_content}
                onChange={(c) => setConsents({ ...consents, linkedin_content: c })}
                title="LinkedIn Appreciation Mentions"
                description="Permit Maatram to prepare celebration draft posts highlighting your volunteering impact."
              />
              <ConsentSwitch
                checked={consents.contact_available}
                onChange={(c) => setConsents({ ...consents, contact_available: c })}
                title="Coordinator Contact Sharing"
                description="Share your email and phone number with verified Maatram event coordinators for logistics."
              />
              <ConsentSwitch
                checked={consents.media_usage}
                onChange={(c) => setConsents({ ...consents, media_usage: c })}
                title="Media & Photography Usage"
                description="Permit photographs and videos taken during volunteering drives in official annual reports."
              />
            </div>
          </section>

          {/* Section 9: Empty States & Loading Skeletons */}
          <section className="space-y-4">
            <SectionHeader
              title="9. Empty States & Skeletons"
              description="Comforting empty states and warm shimmer loading placeholders."
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="flex items-center justify-center">
                <EmptyState
                  icon={<Calendar className="w-8 h-8" />}
                  title="No upcoming activities"
                  description="You haven't registered for any upcoming events yet. Discover events and start volunteering today!"
                  action={
                    <Button variant="primary" rightIcon={<ArrowRight className="w-4 h-4" />}>
                      Discover Events
                    </Button>
                  }
                />
              </Card>

              <Card className="p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <Skeleton variant="circular" className="w-12 h-12" />
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
                <Skeleton className="h-24 w-full" />
                <div className="flex justify-end gap-2 pt-2">
                  <Skeleton className="h-8 w-20" />
                  <Skeleton className="h-8 w-24" />
                </div>
              </Card>
            </div>
          </section>

          {/* Section 10: Avatars & Identity Treatments */}
          <section className="space-y-4">
            <SectionHeader
              title="10. Avatars & Identity Treatments"
              description="Warm initials fallbacks and status indicator dots."
            />
            <Card className="flex flex-wrap items-center gap-6">
              <div className="flex items-center gap-2">
                <Avatar fallback="AK" size="sm" />
                <span className="text-xs text-[#4B5563]">Small (sm)</span>
              </div>
              <div className="flex items-center gap-2">
                <Avatar fallback="Anand K" size="md" status="online" />
                <span className="text-xs text-[#4B5563]">Medium (md)</span>
              </div>
              <div className="flex items-center gap-2">
                <Avatar fallback="Bala M" size="lg" status="verified" />
                <span className="text-xs text-[#4B5563]">Large (lg)</span>
              </div>
              <div className="flex items-center gap-2">
                <Avatar fallback="Divya S" size="xl" status="verified" />
                <span className="text-xs text-[#4B5563]">Extra Large (xl)</span>
              </div>
            </Card>
          </section>

          {/* Section 11: Dialog & Confirmation Modals */}
          <section className="space-y-4">
            <SectionHeader
              title="11. Modals & Dialogs"
              description="Accessible dialogs with smooth spring transitions and backdrop blur."
            />
            <Card className="flex flex-wrap items-center gap-3">
              <Button variant="outline" onClick={() => setDialogOpen(true)}>
                Open Standard Dialog
              </Button>
              <Button variant="destructive" onClick={() => setConfirmDialogOpen(true)}>
                Open Confirmation Dialog
              </Button>

              <Dialog
                open={dialogOpen}
                onClose={() => setDialogOpen(false)}
                title="Volunteer Participation Guidelines"
                description="Please review our mentorship principles before confirming your attendance."
                footer={
                  <Button variant="primary" size="sm" onClick={() => setDialogOpen(false)}>
                    Understood & Continue
                  </Button>
                }
              >
                <p className="text-xs text-[#4B5563] leading-relaxed">
                  As a Maatram volunteer mentor, you represent the highest standard of empathy, punctuality, and commitment to rural first-generation scholars.
                </p>
              </Dialog>

              <ConfirmDialog
                open={confirmDialogOpen}
                onClose={() => setConfirmDialogOpen(false)}
                onConfirm={() => setConfirmDialogOpen(false)}
                title="Withdraw from Event?"
                description="Are you sure you want to withdraw your registration? This opens up your seat for waitlisted volunteers."
                confirmText="Yes, Withdraw"
                variant="destructive"
              />
            </Card>
          </section>

          {/* Section 12: Table Primitives (Ranking Table Sample) */}
          <section className="space-y-4">
            <SectionHeader
              title="12. Data Table Primitives"
              description="Clean responsive table matching Mentor Reference 5 Leaderboard rows."
            />
            <Card className="p-0 overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">#</TableHead>
                    <TableHead>Volunteer</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Points</TableHead>
                    <TableHead className="text-right">Hours</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow highlight={true}>
                    <TableCell className="font-bold">
                      <span className="w-6 h-6 rounded-full bg-[#F5B817] text-[#1F2421] text-xs flex items-center justify-center font-bold">
                        1
                      </span>
                    </TableCell>
                    <TableCell className="font-semibold flex items-center gap-2">
                      <Avatar fallback="AK" size="sm" />
                      <span>Anand K.</span>
                      <Badge variant="brand" size="sm">You</Badge>
                    </TableCell>
                    <TableCell><Badge variant="neutral">STUDENT</Badge></TableCell>
                    <TableCell className="text-right font-bold text-[#1F2421]">580 pts</TableCell>
                    <TableCell className="text-right font-medium text-[#4B5563]">48 hrs</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-bold text-[#4B5563]">2</TableCell>
                    <TableCell className="font-semibold flex items-center gap-2">
                      <Avatar fallback="BM" size="sm" />
                      <span>Bala M.</span>
                    </TableCell>
                    <TableCell><Badge variant="neutral">STUDENT</Badge></TableCell>
                    <TableCell className="text-right font-bold text-[#1F2421]">520 pts</TableCell>
                    <TableCell className="text-right font-medium text-[#4B5563]">46 hrs</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-bold text-[#4B5563]">3</TableCell>
                    <TableCell className="font-semibold flex items-center gap-2">
                      <Avatar fallback="DS" size="sm" />
                      <span>Divya S.</span>
                    </TableCell>
                    <TableCell><Badge variant="neutral">STUDENT</Badge></TableCell>
                    <TableCell className="text-right font-bold text-[#1F2421]">460 pts</TableCell>
                    <TableCell className="text-right font-medium text-[#4B5563]">40 hrs</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </Card>
          </section>
        </main>
      </div>
    </div>
  );
}
