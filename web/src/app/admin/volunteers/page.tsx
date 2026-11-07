"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  Search,
  ChevronLeft,
  ChevronRight,
  GraduationCap,
  Briefcase,
  Eye,
  ShieldCheck,
  Calendar,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { VolunteerListResponse, VolunteerListItem, VolunteerCategory } from "@/types";

export default function AdminVolunteersPage() {
  const [volunteers, setVolunteers] = useState<VolunteerListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [category, setCategory] = useState<string>("ALL");
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");

  const fetchVolunteers = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams();
      if (category !== "ALL") params.append("category", category);
      if (search.trim()) params.append("search", search.trim());
      params.append("page", page.toString());
      params.append("page_size", "15");

      const res = await apiClient.get<VolunteerListResponse>(`/volunteers?${params.toString()}`);
      setVolunteers(res.data.items || []);
      setTotal(res.data.total || 0);
      setTotalPages(res.data.total_pages || 1);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setError(e.message || "Failed to load volunteers directory.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVolunteers();
  }, [category, search, page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setSearch(searchInput);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight flex items-center gap-2.5">
            <Users className="w-7 h-7 text-[#F5B817]" />
            Volunteer Directory
          </h1>
          <p className="text-sm text-charcoal-500 mt-1">
            Search, inspect, and manage canonical volunteer profiles across all chapters.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-charcoal-600 bg-stone-200/60 px-3 py-1.5 rounded-lg">
            Total Roster: <strong className="text-charcoal-900">{total}</strong>
          </span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-stone-200 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0 scrollbar-none">
          {(["ALL", "STUDENT", "ALUMNI", "CORPORATE"] as const).map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => {
                setCategory(cat);
                setPage(1);
              }}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition whitespace-nowrap ${
                category === cat
                  ? "bg-[#F5B817] text-[#1F2421] shadow-xs"
                  : "bg-stone-100 text-charcoal-600 hover:bg-stone-200/70"
              }`}
            >
              {cat === "ALL" ? "All Volunteers" : cat.charAt(0) + cat.slice(1).toLowerCase() + "s"}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-72">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search by name, email, or college..."
            className="w-full text-xs pl-9 pr-3 py-2 bg-stone-50 border border-stone-300 rounded-lg text-charcoal-900 focus:outline-hidden focus:ring-2 focus:ring-[#F5B817]"
          />
          <Search className="w-4 h-4 text-stone-400 absolute left-2.5 top-2.5 pointer-events-none" />
        </form>
      </div>

      {/* Directory Table */}
      <div className="bg-white border border-stone-200 rounded-xl shadow-xs overflow-hidden">
        {loading ? (
          <div className="py-20 text-center">
            <div className="w-8 h-8 border-3 border-[#F5B817] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-xs text-charcoal-500 font-medium">Loading volunteer records...</p>
          </div>
        ) : error ? (
          <div className="py-16 text-center text-red-600">
            <p className="text-sm font-semibold">{error}</p>
          </div>
        ) : volunteers.length === 0 ? (
          <div className="py-20 text-center">
            <Users className="w-10 h-10 text-stone-300 mx-auto mb-3" />
            <p className="text-sm font-bold text-charcoal-700">No volunteers found</p>
            <p className="text-xs text-charcoal-500 mt-1">Try adjusting your category filter or search keywords.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase tracking-wider">
                  <th scope="col" className="py-3.5 px-4">Volunteer</th>
                  <th scope="col" className="py-3.5 px-4">Category</th>
                  <th scope="col" className="py-3.5 px-4">Affiliation / Organisation</th>
                  <th scope="col" className="py-3.5 px-4">Skills & Interests</th>
                  <th scope="col" className="py-3.5 px-4">Safeguarding</th>
                  <th scope="col" className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100 text-xs">
                {volunteers.map((vol) => (
                  <tr key={vol.id} className="hover:bg-amber-50/30 transition">
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-amber-100 text-amber-900 font-bold flex items-center justify-center shrink-0 text-xs border border-amber-200">
                          {vol.first_name?.[0]}
                          {vol.last_name?.[0]}
                        </div>
                        <div>
                          <div className="font-bold text-charcoal-900 text-sm">
                            {vol.first_name} {vol.last_name}
                          </div>
                          <div className="text-[11px] text-charcoal-500">{vol.mobile_number || "Contact hidden"}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wider ${
                          vol.category === "STUDENT"
                            ? "bg-blue-50 text-blue-800 border border-blue-200"
                            : vol.category === "ALUMNI"
                            ? "bg-purple-50 text-purple-800 border border-purple-200"
                            : "bg-emerald-50 text-emerald-800 border border-emerald-200"
                        }`}
                      >
                        {vol.category === "STUDENT" ? (
                          <GraduationCap className="w-3 h-3" />
                        ) : (
                          <Briefcase className="w-3 h-3" />
                        )}
                        {vol.category}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-medium text-charcoal-800">
                        {vol.college_name || vol.employer_name || "Independent"}
                      </div>
                      <div className="text-[11px] text-charcoal-500">
                        {vol.department || vol.job_title || "General"}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {vol.skills && vol.skills.length > 0 ? (
                          vol.skills.slice(0, 3).map((s: string, idx: number) => (
                            <span key={idx} className="px-2 py-0.5 bg-stone-100 text-charcoal-700 rounded text-[10px]">
                              {s}
                            </span>
                          ))
                        ) : (
                          <span className="text-charcoal-400 italic text-[11px]">None listed</span>
                        )}
                        {vol.skills && vol.skills.length > 3 && (
                          <span className="text-[10px] text-charcoal-500">+{vol.skills.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      {vol.is_minor ? (
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                            vol.parental_consent_status === "VERIFIED"
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-amber-100 text-amber-900"
                          }`}
                        >
                          <ShieldCheck className="w-3 h-3" />
                          Minor ({vol.parental_consent_status || "Needed"})
                        </span>
                      ) : (
                        <span className="text-stone-400 text-[11px]">Adult (18+)</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <Link
                        href={`/admin/volunteers/${vol.id}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-stone-100 hover:bg-[#F5B817] hover:text-[#1F2421] text-charcoal-700 font-semibold rounded-lg text-xs transition"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        View Dossier
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        {!loading && totalPages > 1 && (
          <div className="px-4 py-3 bg-stone-50 border-t border-stone-200 flex items-center justify-between text-xs text-charcoal-600">
            <div>
              Showing page <strong>{page}</strong> of <strong>{totalPages}</strong> ({total} records)
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                className="p-1.5 rounded border border-stone-300 disabled:opacity-40 hover:bg-stone-100"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                type="button"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                className="p-1.5 rounded border border-stone-300 disabled:opacity-40 hover:bg-stone-100"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

