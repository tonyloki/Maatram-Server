"use client";

import React, { useEffect, useState } from "react";
import {
  Activity,
  RefreshCw,
  Mail,
  Bell,
  AlertOctagon,
  CheckCircle2,
  Clock,
  RotateCcw,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { OutboxJobResponse, OutboxJobListResponse, OutboxRetryResponse } from "@/types";

export default function AdminOperationsPage() {
  const [jobs, setJobs] = useState<OutboxJobResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [channelFilter, setChannelFilter] = useState<string>("ALL");
  const [retryingId, setRetryingId] = useState<string | null>(null);
  const [retryMessage, setRetryMessage] = useState<string | null>(null);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams();
      if (statusFilter !== "ALL") params.append("status", statusFilter);
      if (channelFilter !== "ALL") params.append("channel", channelFilter);
      params.append("page", page.toString());
      params.append("limit", "20");

      const res = await apiClient.get<OutboxJobListResponse>(`/admin/outbox/jobs?${params.toString()}`);
      setJobs(res.data.items || []);
      setTotal(res.data.total || 0);
      setTotalPages(res.data.total_pages || 1);
    } catch (err: unknown) {
      const e = err as { message?: string };
      setError(e.message || "Failed to load outbox jobs.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [statusFilter, channelFilter, page]);

  const handleRetryJob = async (jobId: string) => {
    try {
      setRetryingId(jobId);
      setRetryMessage(null);
      const res = await apiClient.post<OutboxRetryResponse>(`/admin/outbox/jobs/${jobId}/retry`);
      setRetryMessage(`Job ${jobId.slice(0, 8)} successfully reset to PENDING.`);
      await fetchJobs();
    } catch (err: unknown) {
      const e = err as { message?: string };
      alert(e.message || "Failed to retry outbox job.");
    } finally {
      setRetryingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-charcoal-900 tracking-tight flex items-center gap-2.5">
            <Activity className="w-7 h-7 text-[#F5B817]" />
            Transactional Outbox & Dispatch Operations
          </h1>
          <p className="text-sm text-charcoal-500 mt-1">
            Real-time queue monitoring, email and push notifications dispatching, and Dead Letter Queue (DLQ) recovery.
          </p>
        </div>

        <button
          type="button"
          onClick={fetchJobs}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-stone-200 hover:bg-stone-50 text-charcoal-700 font-semibold rounded-lg text-xs shadow-xs transition"
        >
          <RefreshCw className="w-3.5 h-3.5 text-stone-500" />
          Refresh Queue
        </button>
      </div>

      {retryMessage && (
        <div className="p-3 bg-emerald-50 text-emerald-800 text-xs rounded-xl border border-emerald-200 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          {retryMessage}
        </div>
      )}

      {/* Filters Bar */}
      <div className="bg-white p-4 rounded-xl border border-stone-200 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Status Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto scrollbar-none pb-1 md:pb-0">
          {(["ALL", "PENDING", "PROCESSING", "SENT", "FAILED", "DEAD_LETTER"] as const).map((st) => (
            <button
              key={st}
              type="button"
              onClick={() => {
                setStatusFilter(st);
                setPage(1);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition whitespace-nowrap ${
                statusFilter === st
                  ? "bg-[#F5B817] text-[#1F2421] shadow-xs"
                  : "bg-stone-100 text-charcoal-600 hover:bg-stone-200/70"
              }`}
            >
              {st === "ALL" ? "All Statuses" : st.replace("_", " ")}
            </button>
          ))}
        </div>

        {/* Channel Filters */}
        <div className="flex items-center gap-2 text-xs">
          <span className="font-semibold text-charcoal-500">Channel:</span>
          {(["ALL", "EMAIL", "PUSH"] as const).map((ch) => (
            <button
              key={ch}
              type="button"
              onClick={() => {
                setChannelFilter(ch);
                setPage(1);
              }}
              className={`px-2.5 py-1 rounded text-[11px] font-semibold transition ${
                channelFilter === ch
                  ? "bg-charcoal-900 text-white"
                  : "bg-stone-100 text-charcoal-600 hover:bg-stone-200"
              }`}
            >
              {ch}
            </button>
          ))}
        </div>
      </div>

      {/* Outbox Table */}
      <div className="bg-white border border-stone-200 rounded-xl shadow-xs overflow-hidden">
        {loading ? (
          <div className="py-20 text-center">
            <div className="w-8 h-8 border-3 border-[#F5B817] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-xs text-charcoal-500">Inspecting transactional outbox...</p>
          </div>
        ) : error ? (
          <div className="py-16 text-center text-red-600 text-xs font-semibold">
            {error}
          </div>
        ) : jobs.length === 0 ? (
          <div className="py-20 text-center text-xs text-charcoal-500">
            <Activity className="w-10 h-10 text-stone-300 mx-auto mb-3" />
            No outbox communication jobs found for this filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200 text-[11px] font-bold text-charcoal-500 uppercase tracking-wider">
                  <th scope="col" className="py-3 px-4">Job ID & Channel</th>
                  <th scope="col" className="py-3 px-4">Recipient</th>
                  <th scope="col" className="py-3 px-4">Template / Payload</th>
                  <th scope="col" className="py-3 px-4">Status</th>
                  <th scope="col" className="py-3 px-4">Attempts</th>
                  <th scope="col" className="py-3 px-4">Created / Scheduled</th>
                  <th scope="col" className="py-3 px-4 text-right">Recovery Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-100">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-amber-50/20 transition">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        {job.channel === "EMAIL" ? (
                          <Mail className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                        ) : (
                          <Bell className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                        )}
                        <span className="font-mono text-[11px] font-bold text-charcoal-900">
                          {job.id.slice(0, 8)}...
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-medium text-charcoal-800">
                      {job.recipient}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-charcoal-700 bg-stone-100 px-2 py-0.5 rounded text-[11px]">
                        {job.template_name}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold tracking-wider ${
                          job.status === "SENT"
                            ? "bg-emerald-100 text-emerald-800"
                            : job.status === "PENDING"
                            ? "bg-stone-100 text-charcoal-700"
                            : job.status === "PROCESSING"
                            ? "bg-blue-100 text-blue-800"
                            : job.status === "FAILED"
                            ? "bg-amber-100 text-amber-900"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {job.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-charcoal-600 font-mono">
                      {job.attempts} / {job.max_retries}
                    </td>
                    <td className="py-3 px-4 text-charcoal-500 text-[11px]">
                      {new Date(job.created_at).toLocaleTimeString("en-IN", {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                      })}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {(job.status === "FAILED" || job.status === "DEAD_LETTER") ? (
                        <button
                          type="button"
                          disabled={retryingId === job.id}
                          onClick={() => handleRetryJob(job.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#F5B817] hover:bg-[#E5A800] text-[#1F2421] font-bold rounded text-[11px] shadow-xs transition"
                        >
                          <RotateCcw className="w-3 h-3" />
                          {retryingId === job.id ? "Retrying..." : "Retry Job"}
                        </button>
                      ) : (
                        <span className="text-stone-400 text-[11px]">—</span>
                      )}
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
              Showing page <strong>{page}</strong> of <strong>{totalPages}</strong> ({total} jobs)
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

