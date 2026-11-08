"use client";

import React from "react";
import {
  Settings,
  Shield,
  Clock,
  Sparkles,
  Database,
  CheckCircle2,
} from "lucide-react";

export default function AdminSettingsPage() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-16">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight flex items-center gap-2.5">
          <Settings className="w-7 h-7 text-[#F5B817]" />
          Governance & System Directives
        </h1>
        <p className="text-sm text-charcoal-500 mt-1">
          Locked architectural parameters, gamification policies, and data protection guidelines.
        </p>
      </div>

      {/* Governance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Gamification Policies */}
        <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-stone-100 pb-3">
            <Sparkles className="w-5 h-5 text-[#F5B817]" />
            <h3 className="text-base font-bold text-charcoal-900">Gamification Ledger Directives</h3>
          </div>
          <div className="space-y-3 text-xs text-charcoal-700">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <strong>Point Calculation Formula:</strong>
                <p className="text-charcoal-500 mt-0.5">
                  Points awarded are exactly computed as{" "}
                  <code className="bg-stone-100 px-1 py-0.5 rounded text-[#92400E] font-mono">
                    (10 × Event) + (2 × Verified Hours)
                  </code>
                  .
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <strong>Append-Only Ledger:</strong>
                <p className="text-charcoal-500 mt-0.5">
                  Point balances are strictly computed from canonical, immutable point transaction rows. Point
                  adjustments use compensating credit/debit entries with mandatory audit logs.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <strong>Calendar Cycle:</strong>
                <p className="text-charcoal-500 mt-0.5">
                  Active cycle runs from January 1 through December 31. Leaderboard rankings reset yearly while
                  lifetime stats are preserved.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Safeguarding & Compliance */}
        <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-stone-100 pb-3">
            <Shield className="w-5 h-5 text-[#F5B817]" />
            <h3 className="text-base font-bold text-charcoal-900">Safeguarding & Data Protection</h3>
          </div>
          <div className="space-y-3 text-xs text-charcoal-700">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <strong>Minor Protection Rule (Age &lt; 18):</strong>
                <p className="text-charcoal-500 mt-0.5">
                  Under Maatram Safeguarding Directives, any applicant born after the 18-year threshold requires
                  formal documentary parental consent verification before event participation.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <strong>Granular Consent Gates:</strong>
                <p className="text-charcoal-500 mt-0.5">
                  Volunteer preferences (Leaderboard display, Photo media, Contact sharing, LinkedIn attribution)
                  are tracked with explicit IP and timestamp audit trails.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <strong>Contact Privacy Masking:</strong>
                <p className="text-charcoal-500 mt-0.5">
                  Public and peer endpoints never expose phone numbers or sensitive addresses. Contact details are
                  only visible to authorized administrators.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Event Operations & Attendance */}
        <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-stone-100 pb-3">
            <Clock className="w-5 h-5 text-[#F5B817]" />
            <h3 className="text-base font-bold text-charcoal-900">Event Execution Directives</h3>
          </div>
          <div className="space-y-3 text-xs text-charcoal-700">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <strong>Withdrawal Policy:</strong>
                <p className="text-charcoal-500 mt-0.5">
                  Volunteers may withdraw without penalty up to 24 hours prior to scheduled start time. Late
                  withdrawals trigger attendance status updates.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <strong>Decimal Precision & Rounding:</strong>
                <p className="text-charcoal-500 mt-0.5">
                  Volunteering hours are recorded with half-hour granularity using arithmetic{" "}
                  <code className="bg-stone-100 px-1 py-0.5 rounded text-[#92400E] font-mono">ROUND_HALF_UP</code>.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* System Architecture */}
        <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-stone-100 pb-3">
            <Database className="w-5 h-5 text-[#F5B817]" />
            <h3 className="text-base font-bold text-charcoal-900">Infrastructure & Single Backend</h3>
          </div>
          <div className="space-y-3 text-xs text-charcoal-700">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <strong>Single Modular Monolith Backend:</strong>
                <p className="text-charcoal-500 mt-0.5">
                  All web and mobile clients communicate exclusively with the unified FastAPI backend. No direct
                  database access is permitted from clients.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
              <div>
                <strong>Zero Client Fabrication:</strong>
                <p className="text-charcoal-500 mt-0.5">
                  Every statistic, point ledger, and audit record is computed on-demand from canonical PostgreSQL
                  tables.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

