"use client";

import React, { useEffect, useState } from "react";
import {
  BarChart3,
  Download,
  Users,
  CheckCircle2,
  Clock,
  XCircle,
  GraduationCap,
  Briefcase,
  Building2,
  Calendar,
  ChevronDown,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import {
  AdminDashboardResponse,
  StudentContributionReportResponse,
  AlumniContributionReportResponse,
  OrganisationContributionReportResponse,
  InterviewAvailabilityReportResponse,
  InactiveVolunteerReportResponse,
} from "@/types";

type ReportTab =
  | "overview"
  | "students"
  | "alumni"
  | "organisations"
  | "interviews"
  | "inactive";

export default function AdminReportsPage() {
  const currentYear = new Date().getFullYear();
  const [activeTab, setActiveTab] = useState<ReportTab>("overview");
  const [selectedYear, setSelectedYear] = useState<number>(currentYear);

  const [dashboardData, setDashboardData] = useState<AdminDashboardResponse | null>(null);
  const [studentReport, setStudentReport] = useState<StudentContributionReportResponse | null>(null);
  const [alumniReport, setAlumniReport] = useState<AlumniContributionReportResponse | null>(null);
  const [orgReport, setOrgReport] = useState<OrganisationContributionReportResponse | null>(null);
  const [interviewReport, setInterviewReport] = useState<InterviewAvailabilityReportResponse | null>(null);
  const [inactiveReport, setInactiveReport] = useState<InactiveVolunteerReportResponse | null>(null);

  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load Overview Data on Mount
  useEffect(() => {
    const fetchOverview = async () => {
      try {
        setLoading(true);
        const res = await apiClient.get<AdminDashboardResponse>("/admin/dashboard");
        setDashboardData(res.data);
      } catch (err: unknown) {
        const e = err as { message?: string };
        setError(e.message || "Failed to load dashboard metrics.");
      } finally {
        setLoading(false);
      }
    };
    fetchOverview();
  }, [selectedYear]);

  // Load Tab-specific Data
  useEffect(() => {
    const fetchTabData = async () => {
      try {
        if (activeTab === "students" && !studentReport) {
          const res = await apiClient.get<StudentContributionReportResponse>(
            "/admin/reports/student-contributions?limit=50"
          );
          setStudentReport(res.data);
        } else if (activeTab === "alumni" && !alumniReport) {
          const res = await apiClient.get<AlumniContributionReportResponse>(
            "/admin/reports/alumni-contributions?limit=50"
          );
          setAlumniReport(res.data);
        } else if (activeTab === "organisations" && !orgReport) {
          const res = await apiClient.get<OrganisationContributionReportResponse>(
            "/admin/reports/organisation-contributions?limit=50"
          );
          setOrgReport(res.data);
        } else if (activeTab === "interviews" && !interviewReport) {
          const res = await apiClient.get<InterviewAvailabilityReportResponse>(
            "/admin/reports/interview-availability?limit=50"
          );
          setInterviewReport(res.data);
        } else if (activeTab === "inactive" && !inactiveReport) {
          const res = await apiClient.get<InactiveVolunteerReportResponse>(
            "/admin/reports/inactive-volunteers?limit=50"
          );
          setInactiveReport(res.data);
        }
      } catch {
        // Tab-specific fetch handled
      }
    };
    fetchTabData();
  }, [activeTab]);

  const handleExport = async (type: string) => {
    try {
      setExporting(true);
      const res = await apiClient.download(`/admin/reports/${type}/export`);
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Maatram_${type}_report_${selectedYear}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("Failed to export Excel report. Please ensure report records are present.");
    } finally {
      setExporting(false);
    }
  };

  const studentCount = dashboardData?.volunteers.by_category?.STUDENT ?? 0;
  const alumniCount = dashboardData?.volunteers.by_category?.ALUMNI ?? 0;
  const corporateCount = dashboardData?.volunteers.by_category?.CORPORATE ?? 0;
  const totalVolunteers =
    dashboardData?.volunteers.total_volunteers ??
    (studentCount + alumniCount + corporateCount);

  const studentPct = totalVolunteers > 0 ? Math.round((studentCount / totalVolunteers) * 100) : 0;
  const alumniPct = totalVolunteers > 0 ? Math.round((alumniCount / totalVolunteers) * 100) : 0;
  const corporatePct = totalVolunteers > 0 ? Math.round((corporateCount / totalVolunteers) * 100) : 0;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header Matching Screen 9 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight flex items-center gap-2.5">
            <BarChart3 className="w-7 h-7 text-[#F5B817]" />
            Reports & Analytics
          </h1>
          <p className="text-sm text-charcoal-500 mt-1">
            Canonical data reporting across student cohorts, alumni consistency, and partner organisations.
          </p>
        </div>

        {/* Year Dropdown & Export */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-lg border border-stone-200 text-xs font-semibold text-charcoal-700 shadow-xs">
            <span>Year:</span>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="bg-transparent font-bold text-charcoal-900 focus:outline-hidden cursor-pointer"
            >
              {[currentYear - 1, currentYear, currentYear + 1].map((yr) => (
                <option key={yr} value={yr}>
                  {yr}
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            disabled={exporting}
            onClick={() => handleExport(activeTab === "overview" ? "student-contributions" : activeTab === "students" ? "student-contributions" : activeTab === "alumni" ? "alumni-contributions" : activeTab === "organisations" ? "organisation-contributions" : "interview-availability")}
            className="px-4 py-2 bg-charcoal-900 hover:bg-charcoal-800 text-white rounded-lg text-xs font-bold transition flex items-center gap-2 shadow-xs"
          >
            <Download className="w-3.5 h-3.5 text-[#F5B817]" />
            {exporting ? "Generating..." : "Export Excel (.xlsx)"}
          </button>
        </div>
      </div>

      {/* Screen 9 Tabs */}
      <div className="border-b border-stone-200 flex items-center gap-6 text-xs font-bold text-charcoal-500 overflow-x-auto scrollbar-none">
        <button
          type="button"
          onClick={() => setActiveTab("overview")}
          className={`pb-3 transition whitespace-nowrap ${
            activeTab === "overview"
              ? "text-charcoal-900 border-b-2 border-[#F5B817] font-extrabold"
              : "hover:text-charcoal-800"
          }`}
        >
          Volunteer Overview
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("students")}
          className={`pb-3 transition whitespace-nowrap ${
            activeTab === "students"
              ? "text-charcoal-900 border-b-2 border-[#F5B817] font-extrabold"
              : "hover:text-charcoal-800"
          }`}
        >
          Student Contributions
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("alumni")}
          className={`pb-3 transition whitespace-nowrap ${
            activeTab === "alumni"
              ? "text-charcoal-900 border-b-2 border-[#F5B817] font-extrabold"
              : "hover:text-charcoal-800"
          }`}
        >
          Alumni Contributions
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("organisations")}
          className={`pb-3 transition whitespace-nowrap ${
            activeTab === "organisations"
              ? "text-charcoal-900 border-b-2 border-[#F5B817] font-extrabold"
              : "hover:text-charcoal-800"
          }`}
        >
          Employer / Organisations
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("interviews")}
          className={`pb-3 transition whitespace-nowrap ${
            activeTab === "interviews"
              ? "text-charcoal-900 border-b-2 border-[#F5B817] font-extrabold"
              : "hover:text-charcoal-800"
          }`}
        >
          Interview Availability
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("inactive")}
          className={`pb-3 transition whitespace-nowrap ${
            activeTab === "inactive"
              ? "text-charcoal-900 border-b-2 border-[#F5B817] font-extrabold"
              : "hover:text-charcoal-800"
          }`}
        >
          Inactive Volunteers
        </button>
      </div>

      {/* TAB 1: OVERVIEW MATCHING SCREEN 9 */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* 4 Metric Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
                <Users className="w-6 h-6" />
              </div>
              <div>
                <div className="text-2xl font-black text-charcoal-900 tracking-tight">
                  {dashboardData?.volunteers.total_volunteers ?? 0}
                </div>
                <div className="text-xs font-semibold text-charcoal-500 mt-0.5">Total Volunteers</div>
              </div>
            </div>

            <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <div className="text-2xl font-black text-charcoal-900 tracking-tight">
                  {dashboardData?.volunteers.active_volunteers ?? 0}
                </div>
                <div className="text-xs font-semibold text-charcoal-500 mt-0.5">Approved & Active</div>
              </div>
            </div>

            <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center shrink-0">
                <Clock className="w-6 h-6" />
              </div>
              <div>
                <div className="text-2xl font-black text-charcoal-900 tracking-tight">
                  {dashboardData?.applications.pending ?? 0}
                </div>
                <div className="text-xs font-semibold text-charcoal-500 mt-0.5">Pending Review</div>
              </div>
            </div>

            <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-red-50 text-red-600 flex items-center justify-center shrink-0">
                <XCircle className="w-6 h-6" />
              </div>
              <div>
                <div className="text-2xl font-black text-charcoal-900 tracking-tight">
                  {dashboardData?.applications.rejected ?? 0}
                </div>
                <div className="text-xs font-semibold text-charcoal-500 mt-0.5">Rejected</div>
              </div>
            </div>
          </div>

          {/* Dual Charts from Screen 9 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Verified Engagement Summary */}
            <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-charcoal-900 tracking-tight">
                  Verified Engagement Metrics
                </h3>
                <p className="text-xs text-charcoal-400 mt-0.5">
                  Canonical aggregated data from PostgreSQL attendance & gamification ledgers
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-stone-100 grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200/60">
                  <span className="text-[11px] font-bold text-amber-800 uppercase tracking-wider block">
                    Verified Service Hours
                  </span>
                  <div className="text-2xl font-black text-charcoal-900 mt-1">
                    {dashboardData?.engagement.total_hours_credited ?? "0.00"} hrs
                  </div>
                  <span className="text-[10px] text-charcoal-500 mt-0.5 block">
                    Approved attendance hours
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-200/60">
                  <span className="text-[11px] font-bold text-emerald-800 uppercase tracking-wider block">
                    Points Allocated
                  </span>
                  <div className="text-2xl font-black text-charcoal-900 mt-1">
                    {dashboardData?.engagement.total_points_allocated ?? "0.00"} pts
                  </div>
                  <span className="text-[10px] text-charcoal-500 mt-0.5 block">
                    Canonical ledger balance
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-stone-50 border border-stone-200">
                  <span className="text-[11px] font-bold text-charcoal-600 uppercase tracking-wider block">
                    Total Registrations
                  </span>
                  <div className="text-2xl font-black text-charcoal-900 mt-1">
                    {dashboardData?.engagement.total_registrations ?? 0}
                  </div>
                  <span className="text-[10px] text-charcoal-500 mt-0.5 block">
                    Volunteer drive signups
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-stone-50 border border-stone-200">
                  <span className="text-[11px] font-bold text-charcoal-600 uppercase tracking-wider block">
                    Completed Events
                  </span>
                  <div className="text-2xl font-black text-charcoal-900 mt-1">
                    {dashboardData?.events.completed_events ?? 0}
                  </div>
                  <span className="text-[10px] text-charcoal-500 mt-0.5 block">
                    Closed & points distributed
                  </span>
                </div>
              </div>
            </div>

            {/* Right: Volunteers by Category Donut Chart */}
            <div className="bg-white border border-stone-200 rounded-xl p-6 shadow-xs flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-charcoal-900 tracking-tight">
                  Volunteers by Category
                </h3>
                <p className="text-xs text-charcoal-400 mt-0.5">
                  Composition breakdown across cohorts
                </p>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-around gap-6 my-auto pt-6">
                {/* Donut graphic */}
                <div className="relative w-40 h-40 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    {/* Background Circle */}
                    <circle
                      cx="18"
                      cy="18"
                      r="14"
                      fill="none"
                      stroke="#E5E7EB"
                      strokeWidth="4"
                    />
                    {/* Students */}
                    <circle
                      cx="18"
                      cy="18"
                      r="14"
                      fill="none"
                      stroke="#10B981"
                      strokeWidth="4"
                      strokeDasharray={`${studentPct * 0.88} 100`}
                      strokeDashoffset="0"
                    />
                    {/* Alumni */}
                    <circle
                      cx="18"
                      cy="18"
                      r="14"
                      fill="none"
                      stroke="#F59E0B"
                      strokeWidth="4"
                      strokeDasharray={`${alumniPct * 0.88} 100`}
                      strokeDashoffset={`-${studentPct * 0.88}`}
                    />
                    {/* Corporate */}
                    <circle
                      cx="18"
                      cy="18"
                      r="14"
                      fill="none"
                      stroke="#3B82F6"
                      strokeWidth="4"
                      strokeDasharray={`${corporatePct * 0.88} 100`}
                      strokeDashoffset={`-${(studentPct + alumniPct) * 0.88}`}
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-xl font-black text-charcoal-900">
                      {totalVolunteers}
                    </span>
                    <span className="text-[10px] text-charcoal-400 font-semibold uppercase">Total</span>
                  </div>
                </div>

                {/* Legend */}
                <div className="space-y-3 text-xs min-w-[130px]">
                  <div className="flex items-center gap-3">
                    <span className="w-3 h-3 rounded-full bg-emerald-500 shrink-0" />
                    <span className="text-charcoal-700 font-medium">Students</span>
                    <span className="font-bold text-charcoal-900 ml-auto">{studentPct}%</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="w-3 h-3 rounded-full bg-[#F5B817] shrink-0" />
                    <span className="text-charcoal-700 font-medium">Alumni</span>
                    <span className="font-bold text-charcoal-900 ml-auto">{alumniPct}%</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="w-3 h-3 rounded-full bg-blue-500 shrink-0" />
                    <span className="text-charcoal-700 font-medium">Corporate</span>
                    <span className="font-bold text-charcoal-900 ml-auto">{corporatePct}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: STUDENTS REPORT */}
      {activeTab === "students" && (
        <div className="bg-white border border-stone-200 rounded-xl shadow-xs overflow-hidden">
          <div className="p-4 border-b border-stone-200 bg-stone-50 flex items-center justify-between">
            <h3 className="text-sm font-bold text-charcoal-900">Student Volunteer Contributions</h3>
            <span className="text-xs text-charcoal-500 font-medium">
              Total Records: {studentReport?.total ?? 0}
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase">
                  <th className="py-3 px-4">Student</th>
                  <th className="py-3 px-4">College / University</th>
                  <th className="py-3 px-4">Department</th>
                  <th className="py-3 px-4">Events</th>
                  <th className="py-3 px-4">Hours Credited</th>
                  <th className="py-3 px-4">Points</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {studentReport?.items && studentReport.items.length > 0 ? (
                  studentReport.items.map((item, idx) => (
                    <tr key={idx} className="hover:bg-amber-50/20">
                      <td className="py-3 px-4 font-bold text-charcoal-900">{item.volunteer_name}</td>
                      <td className="py-3 px-4 text-charcoal-700">{item.college_name || "N/A"}</td>
                      <td className="py-3 px-4 text-charcoal-600">{item.department || "N/A"}</td>
                      <td className="py-3 px-4 font-semibold">{item.events_attended}</td>
                      <td className="py-3 px-4 font-bold text-amber-700">{item.hours_credited} hrs</td>
                      <td className="py-3 px-4 font-black text-charcoal-900">{item.points_earned} pts</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-charcoal-400 italic">
                      No student contribution records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: ALUMNI REPORT */}
      {activeTab === "alumni" && (
        <div className="bg-white border border-stone-200 rounded-xl shadow-xs overflow-hidden">
          <div className="p-4 border-b border-stone-200 bg-stone-50 flex items-center justify-between">
            <h3 className="text-sm font-bold text-charcoal-900">Alumni Volunteer Contributions</h3>
            <span className="text-xs text-charcoal-500 font-medium">
              Total Records: {alumniReport?.total ?? 0}
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase">
                  <th className="py-3 px-4">Alumni Volunteer</th>
                  <th className="py-3 px-4">Employer / Company</th>
                  <th className="py-3 px-4">Graduation Batch</th>
                  <th className="py-3 px-4">Events</th>
                  <th className="py-3 px-4">Hours</th>
                  <th className="py-3 px-4">Points</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {alumniReport?.items && alumniReport.items.length > 0 ? (
                  alumniReport.items.map((item, idx) => (
                    <tr key={idx} className="hover:bg-amber-50/20">
                      <td className="py-3 px-4 font-bold text-charcoal-900">{item.volunteer_name}</td>
                      <td className="py-3 px-4 text-charcoal-700">{item.employer_name || "N/A"}</td>
                      <td className="py-3 px-4 text-charcoal-600">{item.graduation_year || "N/A"}</td>
                      <td className="py-3 px-4 font-semibold">{item.events_attended}</td>
                      <td className="py-3 px-4 font-bold text-amber-700">{item.hours_credited} hrs</td>
                      <td className="py-3 px-4 font-black text-charcoal-900">{item.points_earned} pts</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-charcoal-400 italic">
                      No alumni contribution records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: ORGANISATIONS REPORT */}
      {activeTab === "organisations" && (
        <div className="bg-white border border-stone-200 rounded-xl shadow-xs overflow-hidden">
          <div className="p-4 border-b border-stone-200 bg-stone-50 flex items-center justify-between">
            <h3 className="text-sm font-bold text-charcoal-900">Employer & Partner Organisation Impact</h3>
            <span className="text-xs text-charcoal-500 font-medium">
              Total Organisations: {orgReport?.total ?? 0}
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase">
                  <th className="py-3 px-4">Organisation Name</th>
                  <th className="py-3 px-4">Volunteers</th>
                  <th className="py-3 px-4">Total Events Attended</th>
                  <th className="py-3 px-4">Verified Hours</th>
                  <th className="py-3 px-4">Points Earned</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {orgReport?.items && orgReport.items.length > 0 ? (
                  orgReport.items.map((item, idx) => (
                    <tr key={idx} className="hover:bg-amber-50/20">
                      <td className="py-3 px-4 font-bold text-charcoal-900">
                        {item.organisation_name}
                      </td>
                      <td className="py-3 px-4 font-semibold">{item.volunteer_count}</td>
                      <td className="py-3 px-4">{item.total_events_attended}</td>
                      <td className="py-3 px-4 font-bold text-amber-700">{item.total_hours_credited} hrs</td>
                      <td className="py-3 px-4 font-black text-charcoal-900">{item.total_points_earned} pts</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-charcoal-400 italic">
                      No partner organisation records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 5: INTERVIEW AVAILABILITY */}
      {activeTab === "interviews" && (
        <div className="bg-white border border-stone-200 rounded-xl shadow-xs overflow-hidden">
          <div className="p-4 border-b border-stone-200 bg-stone-50 flex items-center justify-between">
            <h3 className="text-sm font-bold text-charcoal-900">
              Mock Interview Availability (Privacy Masked)
            </h3>
            <span className="text-xs text-charcoal-500 font-medium">
              Available Volunteers: {interviewReport?.total ?? 0}
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase">
                  <th className="py-3 px-4">Volunteer</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Organisation</th>
                  <th className="py-3 px-4">Contact (Consent Governed)</th>
                  <th className="py-3 px-4">Skills</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {interviewReport?.items && interviewReport.items.length > 0 ? (
                  interviewReport.items.map((item, idx) => (
                    <tr key={idx} className="hover:bg-amber-50/20">
                      <td className="py-3 px-4 font-bold text-charcoal-900">{item.volunteer_name}</td>
                      <td className="py-3 px-4 font-semibold">{item.category}</td>
                      <td className="py-3 px-4 text-charcoal-700">{item.organisation || "Independent"}</td>
                      <td className="py-3 px-4 font-mono text-stone-600">{item.contact_number}</td>
                      <td className="py-3 px-4 text-charcoal-600">{item.skills?.join(", ") || "General"}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-charcoal-400 italic">
                      No interview availability records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 6: INACTIVE VOLUNTEERS */}
      {activeTab === "inactive" && (
        <div className="bg-white border border-stone-200 rounded-xl shadow-xs overflow-hidden">
          <div className="p-4 border-b border-stone-200 bg-stone-50 flex items-center justify-between">
            <h3 className="text-sm font-bold text-charcoal-900">
              Inactive Volunteers (No Participation in 90+ Days)
            </h3>
            <span className="text-xs text-charcoal-500 font-medium">
              Total Inactive: {inactiveReport?.total ?? 0}
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase">
                  <th className="py-3 px-4">Volunteer</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Last Attended Event</th>
                  <th className="py-3 px-4">Days Since Activity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {inactiveReport?.items && inactiveReport.items.length > 0 ? (
                  inactiveReport.items.map((item, idx) => (
                    <tr key={idx} className="hover:bg-amber-50/20">
                      <td className="py-3 px-4 font-bold text-charcoal-900">{item.volunteer_name}</td>
                      <td className="py-3 px-4 font-semibold">{item.category}</td>
                      <td className="py-3 px-4 text-charcoal-600">
                        {item.last_event_title || "None recorded"}
                      </td>
                      <td className="py-3 px-4 font-bold text-red-600">{item.days_inactive} days</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="py-12 text-center text-charcoal-400 italic">
                      No inactive volunteer records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

