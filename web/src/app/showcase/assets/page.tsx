"use client";

import React, { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { ArrowLeft, Sparkles, Layers, Image as ImageIcon, Award, Shield, Palette } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SegmentedTabs } from "@/components/ui/tabs";
import { SectionHeader } from "@/components/ui/section-header";

interface AssetCardProps {
  title: string;
  category: string;
  path: string;
  format: string;
  dimensions: string;
  description: string;
  usage: string;
  isVector?: boolean;
}

function AssetPreviewCard({
  title,
  category,
  path,
  format,
  dimensions,
  description,
  usage,
  isVector = true,
}: AssetCardProps) {
  return (
    <Card className="flex flex-col overflow-hidden border-[#EFECE6] hover:border-[#F5B817]/60 transition-all group">
      {/* Visual Canvas Container */}
      <div className="relative w-full h-48 bg-[#FAF8F5] border-b border-[#EFECE6] flex items-center justify-center p-4 overflow-hidden">
        {/* Subtle checkered pattern to demonstrate transparency */}
        <div
          className="absolute inset-0 opacity-15"
          style={{
            backgroundImage:
              "radial-gradient(#CBD5E1 1px, transparent 1px), radial-gradient(#CBD5E1 1px, #FAF8F5 1px)",
            backgroundSize: "16px 16px",
            backgroundPosition: "0 0, 8px 8px",
          }}
        />
        {/* Actual Rendered Asset */}
        <div className="relative z-10 max-h-40 max-w-full flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
          <img
            src={path}
            alt={title}
            className="max-h-36 max-w-full object-contain"
          />
        </div>
        <div className="absolute top-2.5 right-2.5 z-20">
          <Badge variant="neutral" size="sm">
            {format.toUpperCase()}
          </Badge>
        </div>
      </div>

      {/* Asset Metadata */}
      <div className="p-4 flex flex-col flex-1 justify-between space-y-3 bg-white">
        <div>
          <div className="flex items-center justify-between gap-2">
            <h4 className="text-sm font-bold text-[#1F2421] truncate" title={title}>
              {title}
            </h4>
            <span className="text-[10px] font-semibold text-[#946C00] bg-[#FFF8E7] px-2 py-0.5 rounded-full border border-[#F5B817]/30 flex-shrink-0">
              {dimensions}
            </span>
          </div>
          <p className="text-xs text-[#4B5563] mt-1 line-clamp-2 leading-relaxed">
            {description}
          </p>
        </div>

        <div className="pt-2 border-t border-[#EFECE6] flex items-center justify-between text-[11px]">
          <span className="text-[#6B7280]">Target Usage:</span>
          <span className="font-semibold text-[#1F2421] truncate max-w-[160px] text-right" title={usage}>
            {usage}
          </span>
        </div>
      </div>
    </Card>
  );
}

export default function AssetGalleryShowcasePage() {
  const [activeTab, setActiveTab] = useState("all");

  const ILLUSTRATIONS: AssetCardProps[] = [
    {
      title: "Hero Volunteers Landscape",
      category: "illustrations",
      path: "/assets/maatram/illustrations/hero-volunteering-banner.svg",
      format: "svg",
      dimensions: "960 × 300 px",
      description: "Panoramic scenic landscape with volunteers in black Maatram t-shirts under golden sun and lush shade tree.",
      usage: "Volunteer Dashboard Welcome Banner",
    },
    {
      title: "Together Hand-Heart",
      category: "illustrations",
      path: "/assets/maatram/illustrations/together-heart.svg",
      format: "svg",
      dimensions: "400 × 400 px",
      description: "Two cupping hands holding a glowing golden heart with radiating sunburst rays and official slogan.",
      usage: "Dashboard Guide & Sidebar Feature",
    },
    {
      title: "Desk Calendar Empty State",
      category: "illustrations",
      path: "/assets/maatram/illustrations/empty-calendar-event.svg",
      format: "svg",
      dimensions: "400 × 300 px",
      description: "3D desk flip-calendar showing Maatram brand leaf and radial golden aura for upcoming participation empty states.",
      usage: "Dashboard Upcoming Events Card",
    },
    {
      title: "Activity Clock & Calendar",
      category: "illustrations",
      path: "/assets/maatram/illustrations/empty-activity-clock.svg",
      format: "svg",
      dimensions: "450 × 320 px",
      description: "3D desk calendar alongside a floating analogue clock with golden botanical leaves framing the scene.",
      usage: "My Activity Empty State",
    },
    {
      title: "Community Mentorship",
      category: "illustrations",
      path: "/assets/maatram/illustrations/community-mentorship.svg",
      format: "svg",
      dimensions: "500 × 400 px",
      description: "Warm illustration of volunteer mentor guiding a first-generation scholar with an open book and mortarboard.",
      usage: "Impact Reports & Onboarding",
    },
    {
      title: "School Visit Guidance",
      category: "illustrations",
      path: "/assets/maatram/illustrations/school-guidance.svg",
      format: "svg",
      dimensions: "500 × 400 px",
      description: "Government High School building with flag, classroom windows, and rural school signpost.",
      usage: "School Visit Event Discovery",
    },
  ];

  const GAMIFICATION: AssetCardProps[] = [
    {
      title: "Podium Rank 1 (Gold)",
      category: "gamification",
      path: "/assets/maatram/gamification/podium-rank-1-gold.svg",
      format: "svg",
      dimensions: "240 × 320 px",
      description: "3D-styled physical golden podium pedestal (tallest, center) with golden crown, Roman numeral 1, and laurel wreath.",
      usage: "Leaderboard Top 3 Podium",
    },
    {
      title: "Podium Rank 2 (Silver)",
      category: "gamification",
      path: "/assets/maatram/gamification/podium-rank-2-silver.svg",
      format: "svg",
      dimensions: "220 × 270 px",
      description: "Polished silver metallic pedestal (mid-height, left) with silver crown and Roman numeral 2.",
      usage: "Leaderboard Top 3 Podium",
    },
    {
      title: "Podium Rank 3 (Bronze)",
      category: "gamification",
      path: "/assets/maatram/gamification/podium-rank-3-bronze.svg",
      format: "svg",
      dimensions: "220 × 240 px",
      description: "Warm copper-bronze metallic pedestal (lowest, right) with bronze crown and Roman numeral 3.",
      usage: "Leaderboard Top 3 Podium",
    },
    {
      title: "Grand Champion Trophy",
      category: "gamification",
      path: "/assets/maatram/gamification/trophy-grand.svg",
      format: "svg",
      dimensions: "360 × 400 px",
      description: "Master golden champion trophy with star medallion, dual ornate handles, and silhouetted cheering crowd accent.",
      usage: "Leaderboard Hero Banner",
    },
    {
      title: "Crown #1 (Gold)",
      category: "gamification",
      path: "/assets/maatram/gamification/crown-gold.svg",
      format: "svg",
      dimensions: "120 × 80 px",
      description: "5-point golden crown with ruby and sapphire gemstones for 1st place avatar badge overlay.",
      usage: "Podium & Profile Ranking",
    },
    {
      title: "Crown #2 (Silver)",
      category: "gamification",
      path: "/assets/maatram/gamification/crown-silver.svg",
      format: "svg",
      dimensions: "120 × 80 px",
      description: "5-point silver crown with sapphire jewels for 2nd place avatar badge overlay.",
      usage: "Podium & Profile Ranking",
    },
    {
      title: "Crown #3 (Bronze)",
      category: "gamification",
      path: "/assets/maatram/gamification/crown-bronze.svg",
      format: "svg",
      dimensions: "120 × 80 px",
      description: "5-point warm bronze crown with amber jewels for 3rd place avatar badge overlay.",
      usage: "Podium & Profile Ranking",
    },
    {
      title: "Circular Laurel Wreath",
      category: "gamification",
      path: "/assets/maatram/gamification/laurel-wreath.svg",
      format: "svg",
      dimensions: "200 × 200 px",
      description: "Symmetrical circular olive branches in canonical gold framing rank 1 portrait photo.",
      usage: "Leaderboard 1st Place Avatar",
    },
    {
      title: "Medal: First Step",
      category: "gamification",
      path: "/assets/maatram/gamification/badge-first-step.svg",
      format: "svg",
      dimensions: "140 × 140 px",
      description: "Compass star medal with emerald ribbons marking volunteer's first event registration.",
      usage: "Volunteer Profile Achievements",
    },
    {
      title: "Medal: Star Mentor",
      category: "gamification",
      path: "/assets/maatram/gamification/badge-mentor-star.svg",
      format: "svg",
      dimensions: "140 × 140 px",
      description: "Radiant multi-point star medal with sapphire ribbons awarded for exemplary mentorship.",
      usage: "Volunteer Profile Achievements",
    },
    {
      title: "Medal: Century Club",
      category: "gamification",
      path: "/assets/maatram/gamification/badge-century-club.svg",
      format: "svg",
      dimensions: "140 × 140 px",
      description: "Shield medal with purple ribbons celebrating 100+ points accumulated.",
      usage: "Volunteer Profile Achievements",
    },
    {
      title: "Medal: Super Volunteer",
      category: "gamification",
      path: "/assets/maatram/gamification/badge-super-volunteer.svg",
      format: "svg",
      dimensions: "140 × 140 px",
      description: "Winged crown medal with crimson ribbons recognizing top community contributors.",
      usage: "Volunteer Profile Achievements",
    },
  ];

  const DECORATIONS: AssetCardProps[] = [
    {
      title: "Flock of Birds in Flight",
      category: "decorations",
      path: "/assets/maatram/decorations/birds-flock.svg",
      format: "svg",
      dimensions: "240 × 120 px",
      description: "Silhouetted flock of 7 birds rising gracefully toward the sun.",
      usage: "Hero Banner & Header Accents",
    },
    {
      title: "Shade Tree Silhouette",
      category: "decorations",
      path: "/assets/maatram/decorations/tree-silhouette.svg",
      format: "svg",
      dimensions: "320 × 320 px",
      description: "Organic banyan/shade tree silhouette framing natural landscapes.",
      usage: "Hero Landscape Compositions",
    },
    {
      title: "Wheat Stalks Watermark",
      category: "decorations",
      path: "/assets/maatram/decorations/wheat-stalks.svg",
      format: "svg",
      dimensions: "120 × 240 px",
      description: "Delicate golden botanical wheat stalks and arching leaves for background watermarks.",
      usage: "Sidebar Canvas & Card Corners",
    },
    {
      title: "Radial Golden Sunburst",
      category: "decorations",
      path: "/assets/maatram/decorations/golden-sunburst.svg",
      format: "svg",
      dimensions: "400 × 400 px",
      description: "Warm radiating sunburst beams in canonical gold with soft center glow.",
      usage: "Celebratory Cards & Milestones",
    },
    {
      title: "Warm Wave Accent",
      category: "decorations",
      path: "/assets/maatram/decorations/warm-wave-accent.svg",
      format: "svg",
      dimensions: "800 × 160 px",
      description: "Organic flowing wave ribbon divider in warm gold and cream.",
      usage: "Card Headers & Section Dividers",
    },
    {
      title: "Celebratory Confetti",
      category: "decorations",
      path: "/assets/maatram/decorations/celebratory-confetti.svg",
      format: "svg",
      dimensions: "600 × 400 px",
      description: "Burst of golden starbursts, ribbons, and geometric confetti particles.",
      usage: "Leaderboard & Milestone Moments",
    },
  ];

  const ICONS: AssetCardProps[] = [
    {
      title: "Nav: Dashboard",
      category: "icons",
      path: "/assets/maatram/icons/nav-dashboard.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Warm hearth home icon with canonical gold hearth accent.",
      usage: "Left Navigation Rail",
    },
    {
      title: "Nav: Discover Events",
      category: "icons",
      path: "/assets/maatram/icons/nav-discover.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Compass with golden directional needle.",
      usage: "Left Navigation Rail",
    },
    {
      title: "Nav: My Activity",
      category: "icons",
      path: "/assets/maatram/icons/nav-activity.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Calendar with completed tick.",
      usage: "Left Navigation Rail",
    },
    {
      title: "Nav: Leaderboard",
      category: "icons",
      path: "/assets/maatram/icons/nav-leaderboard.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Trophy cup with golden plinth.",
      usage: "Left Navigation Rail",
    },
    {
      title: "Nav: My Profile",
      category: "icons",
      path: "/assets/maatram/icons/nav-profile.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "User silhouette with warm aura.",
      usage: "Left Navigation Rail",
    },
    {
      title: "Nav: Notifications",
      category: "icons",
      path: "/assets/maatram/icons/nav-notifications.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Bell with unread indicator badge dot.",
      usage: "Header & Navigation Rail",
    },
    {
      title: "Category: School Visit",
      category: "icons",
      path: "/assets/maatram/icons/cat-school-visit.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Schoolhouse with flag and graduation cap.",
      usage: "Event Filter & Category Pills",
    },
    {
      title: "Category: Mock Interview",
      category: "icons",
      path: "/assets/maatram/icons/cat-mock-interview.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Dual interview speech bubbles.",
      usage: "Event Filter & Category Pills",
    },
    {
      title: "Category: BGV Support",
      category: "icons",
      path: "/assets/maatram/icons/cat-bgv-support.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Document clipboard with shield checkmark.",
      usage: "Event Filter & Category Pills",
    },
    {
      title: "Category: Admissions",
      category: "icons",
      path: "/assets/maatram/icons/cat-admissions.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Mortarboard with golden tassel.",
      usage: "Event Filter & Category Pills",
    },
    {
      title: "Category: Panel Interview",
      category: "icons",
      path: "/assets/maatram/icons/cat-panel-interview.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Three mentor panelists at conference table.",
      usage: "Event Filter & Category Pills",
    },
    {
      title: "Mode: Onsite",
      category: "icons",
      path: "/assets/maatram/icons/mode-onsite.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Location map pin with solid green center.",
      usage: "Event Delivery Mode Tag",
    },
    {
      title: "Mode: Online",
      category: "icons",
      path: "/assets/maatram/icons/mode-online.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Laptop screen with video signal indicator.",
      usage: "Event Delivery Mode Tag",
    },
    {
      title: "Metric: Points Star",
      category: "icons",
      path: "/assets/maatram/icons/metric-points.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Gleaming 5-point star in golden circle.",
      usage: "KPI Cards & Points Ledger",
    },
    {
      title: "Metric: Hours Clock",
      category: "icons",
      path: "/assets/maatram/icons/metric-hours.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Clock with verified service checkmark.",
      usage: "KPI Cards & Attendance",
    },
    {
      title: "Metric: Events Calendar",
      category: "icons",
      path: "/assets/maatram/icons/metric-events.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Calendar with completed event drive indicators.",
      usage: "KPI Cards & Dashboard",
    },
    {
      title: "Metric: Rank Podium",
      category: "icons",
      path: "/assets/maatram/icons/metric-rank.svg",
      format: "svg",
      dimensions: "24 × 24 px",
      description: "Step-podium with #1 leader star.",
      usage: "KPI Cards & Leaderboard",
    },
  ];

  const PHOTOGRAPHY: AssetCardProps[] = [
    {
      title: "Hero Classroom Mentoring",
      category: "photography",
      path: "/assets/maatram/photography/hero-volunteering.jpg",
      format: "jpeg",
      dimensions: "1200 × 800 px",
      description: "Authentic classroom mentorship session with engaged rural scholars.",
      usage: "Public Landing Hero",
      isVector: false,
    },
    {
      title: "School Visit Classroom",
      category: "photography",
      path: "/assets/maatram/photography/school-visit.jpg",
      format: "jpeg",
      dimensions: "800 × 498 px",
      description: "Authentic Government High School classroom interaction and guidance drive.",
      usage: "Event Cards & Dashboard",
      isVector: false,
    },
    {
      title: "Mock Interview Mentorship",
      category: "photography",
      path: "/assets/maatram/photography/mock-interview.jpg",
      format: "jpeg",
      dimensions: "800 × 533 px",
      description: "Authentic 1-on-1 career interview practice and resume guidance session.",
      usage: "Event Cards & Dashboard",
      isVector: false,
    },
    {
      title: "BGV Field Verification",
      category: "photography",
      path: "/assets/maatram/photography/bgv-support.jpg",
      format: "jpeg",
      dimensions: "800 × 533 px",
      description: "Authentic background verification document review and scholarship eligibility support.",
      usage: "Event Cards & Dashboard",
      isVector: false,
    },
    {
      title: "Admissions Guidance Celebration",
      category: "photography",
      path: "/assets/maatram/photography/admissions-guidance.jpg",
      format: "jpeg",
      dimensions: "800 × 533 px",
      description: "Authentic first-generation college scholars and volunteer mentors celebrating university admissions letters.",
      usage: "Discover Events Category Thumbnail",
      isVector: false,
    },
    {
      title: "Panel Interview Mentorship",
      category: "photography",
      path: "/assets/maatram/photography/panel-interview.jpg",
      format: "jpeg",
      dimensions: "800 × 533 px",
      description: "Authentic volunteer mentors conducting an encouraging practice interview panel with a young student scholar.",
      usage: "Discover Events Category Thumbnail",
      isVector: false,
    },
    {
      title: "Community Outreach Initiative",
      category: "photography",
      path: "/assets/maatram/photography/community-engagement.jpg",
      format: "jpeg",
      dimensions: "800 × 533 px",
      description: "Authentic volunteers gathered outdoors with village youth discussing student mentorship and higher education access.",
      usage: "Community Drives & Public Impact",
      isVector: false,
    },
  ];

  const ALL_ASSETS = [
    ...ILLUSTRATIONS,
    ...GAMIFICATION,
    ...DECORATIONS,
    ...ICONS,
    ...PHOTOGRAPHY,
  ];

  const filteredAssets =
    activeTab === "all"
      ? ALL_ASSETS
      : ALL_ASSETS.filter((a) => a.category === activeTab);

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-[#1F2421]">
      {/* Top Header */}
      <header className="bg-white border-b border-[#EFECE6] px-4 py-3 sticky top-0 z-50 shadow-xs">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/showcase"
              className="p-1.5 rounded-lg text-[#4B5563] hover:text-[#1F2421] hover:bg-[#FAF8F5] transition-colors"
              title="Back to Component Showcase"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-[#946C00] bg-[#FFF8E7] px-2.5 py-0.5 rounded-full border border-[#F5B817]/40">
                  Internal QA Utility
                </span>
                <h1 className="text-sm font-extrabold text-[#1F2421]">
                  Maatram Visual Asset Library
                </h1>
              </div>
            </div>
          </div>

          <div className="text-xs text-[#4B5563] font-medium hidden sm:block">
            Total Curated Assets: <span className="font-bold text-[#F5B817]">{ALL_ASSETS.length}</span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto p-4 md:p-8 space-y-8">
        {/* Intro Banner */}
        <div className="bg-gradient-to-r from-[#FFF8E7] via-[#FFFDF5] to-[#FAF8F5] p-6 rounded-3xl border border-[#F5B817]/30 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white text-[#946C00] text-xs font-bold border border-[#F5B817]/30">
              <Shield className="w-3.5 h-3.5 text-[#F5B817]" />
              <span>Internal Review Only — Development QA Utility</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-[#1F2421]">
              Illustrations, Photography, Symbols & Gamification
            </h2>
            <p className="text-sm text-[#4B5563] leading-relaxed">
              Every asset in this library is crafted to embody Maatram's warm, human-centered brand identity.
              Calibrated strictly to the canonical brand gold (<code className="font-bold text-[#946C00]">#F5B817</code>),
              warm ivory (<code className="font-bold text-[#946C00]">#FAF8F5</code>), and mentor reference designs.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 flex-shrink-0">
            <div className="p-3 rounded-2xl bg-white border border-[#EFECE6] text-center shadow-xs">
              <span className="block text-2xl font-black text-[#1F2421]">{ILLUSTRATIONS.length}</span>
              <span className="text-[11px] text-[#6B7280] font-semibold">Illustrations</span>
            </div>
            <div className="p-3 rounded-2xl bg-white border border-[#EFECE6] text-center shadow-xs">
              <span className="block text-2xl font-black text-[#1F2421]">{GAMIFICATION.length}</span>
              <span className="text-[11px] text-[#6B7280] font-semibold">Gamification</span>
            </div>
            <div className="p-3 rounded-2xl bg-white border border-[#EFECE6] text-center shadow-xs">
              <span className="block text-2xl font-black text-[#1F2421]">{ICONS.length}</span>
              <span className="text-[11px] text-[#6B7280] font-semibold">Custom Icons</span>
            </div>
            <div className="p-3 rounded-2xl bg-white border border-[#EFECE6] text-center shadow-xs">
              <span className="block text-2xl font-black text-[#1F2421]">{DECORATIONS.length}</span>
              <span className="text-[11px] text-[#6B7280] font-semibold">Decorations</span>
            </div>
          </div>
        </div>

        {/* Category Tabs Filter */}
        <div className="flex items-center justify-between flex-wrap gap-4 pt-2">
          <SegmentedTabs
            tabs={[
              { id: "all", label: "All Assets", badge: ALL_ASSETS.length },
              { id: "illustrations", label: "Illustrations", badge: ILLUSTRATIONS.length },
              { id: "gamification", label: "Gamification", badge: GAMIFICATION.length },
              { id: "decorations", label: "Decorations", badge: DECORATIONS.length },
              { id: "icons", label: "Icons", badge: ICONS.length },
              { id: "photography", label: "Photography", badge: PHOTOGRAPHY.length },
            ]}
            activeTab={activeTab}
            onChange={setActiveTab}
          />
        </div>

        {/* Asset Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {filteredAssets.map((asset) => (
            <AssetPreviewCard key={asset.path} {...asset} />
          ))}
        </div>

        {/* Section: Example Combinations / How Assets Work Together */}
        <section className="space-y-6 pt-8 border-t border-[#EFECE6]">
          <SectionHeader
            title="Visual Composition Harmony Test"
            description="Demonstrating how illustrations, photography, decorations, and gamification artwork work together on authentic Maatram card surfaces."
          />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Sample 1: Leaderboard Podium Celebration Composition */}
            <Card className="relative overflow-hidden p-6 space-y-6 bg-gradient-to-b from-[#FFFDF5] to-[#FAF8F5] border-[#EFECE6]">
              <div className="absolute top-0 right-0 w-64 h-64 pointer-events-none opacity-40">
                <img src="/assets/maatram/decorations/celebratory-confetti.svg" alt="" className="w-full h-full object-contain" />
              </div>

              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#946C00] bg-[#FFF8E7] px-3 py-1 rounded-full border border-[#F5B817]/30 inline-block mb-2">
                  Composition 1: Leaderboard Top 3 Podium
                </span>
                <h3 className="text-xl font-bold text-[#1F2421]">
                  Physical 3-Step Podium with Crowning & Laurels
                </h3>
              </div>

              {/* Podium Visual Layout */}
              <div className="flex items-end justify-center gap-3 pt-8 pb-4 relative z-10">
                {/* 2nd Place (Silver) */}
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full bg-white border-3 border-[#CBD5E1] shadow-md flex items-center justify-center font-bold text-sm text-[#475569] mb-[-12px] z-20">
                    BK
                  </div>
                  <img
                    src="/assets/maatram/gamification/podium-rank-2-silver.svg"
                    alt="Rank 2 Silver"
                    className="w-28 h-auto"
                  />
                  <span className="text-xs font-bold text-[#1F2421] mt-2">Bala K.</span>
                  <span className="text-[11px] font-semibold text-[#64748B]">520 pts</span>
                </div>

                {/* 1st Place (Gold - Tallest & Laureled) */}
                <div className="flex flex-col items-center z-10">
                  <div className="relative mb-[-16px] z-20">
                    <img
                      src="/assets/maatram/gamification/laurel-wreath.svg"
                      alt="Laurel"
                      className="absolute inset-0 w-24 h-24 -top-3 -left-3 scale-110 pointer-events-none"
                    />
                    <div className="w-20 h-20 rounded-full bg-white border-3 border-[#F5B817] shadow-lg flex items-center justify-center font-extrabold text-base text-[#1F2421]">
                      AM
                    </div>
                  </div>
                  <img
                    src="/assets/maatram/gamification/podium-rank-1-gold.svg"
                    alt="Rank 1 Gold"
                    className="w-36 h-auto"
                  />
                  <span className="text-xs font-extrabold text-[#1F2421] mt-2">Anand M.</span>
                  <span className="text-xs font-black text-[#946C00]">580 pts</span>
                </div>

                {/* 3rd Place (Bronze) */}
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full bg-white border-3 border-[#FDBA74] shadow-md flex items-center justify-center font-bold text-sm text-[#9A3412] mb-[-12px] z-20">
                    DS
                  </div>
                  <img
                    src="/assets/maatram/gamification/podium-rank-3-bronze.svg"
                    alt="Rank 3 Bronze"
                    className="w-28 h-auto"
                  />
                  <span className="text-xs font-bold text-[#1F2421] mt-2">Divya S.</span>
                  <span className="text-[11px] font-semibold text-[#C2410C]">460 pts</span>
                </div>
              </div>
            </Card>

            {/* Sample 2: Panoramic Hero Banner Integration */}
            <Card className="relative overflow-hidden p-6 space-y-4 bg-white border-[#EFECE6] flex flex-col justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#946C00] bg-[#FFF8E7] px-3 py-1 rounded-full border border-[#F5B817]/30 inline-block mb-2">
                  Composition 2: Welcome Banner Integration
                </span>
                <h3 className="text-xl font-bold text-[#1F2421]">
                  Layered Panoramic Welcome Hero
                </h3>
              </div>

              <div className="rounded-2xl overflow-hidden border border-[#EFECE6] shadow-xs">
                <img
                  src="/assets/maatram/illustrations/hero-volunteering-banner.svg"
                  alt="Panoramic Hero Banner"
                  className="w-full h-auto object-cover"
                />
              </div>

              <div className="flex items-center justify-between text-xs text-[#6B7280] pt-2">
                <span>Features: Sunburst, Birds, Tree, Volunteers, Curved Golden Ribbon</span>
                <span className="font-bold text-[#F5B817]">Matches Reference 2</span>
              </div>
            </Card>
          </div>
        </section>
      </main>
    </div>
  );
}
