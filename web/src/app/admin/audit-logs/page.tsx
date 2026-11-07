"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  FileText,
  Search,
  Filter,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  Calendar,
  Eye,
  X,
  Code,
  User,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { AuditLogResponse, AuditLogListResponse } from "@/types";
import { useAuth } from "@/lib/auth-context";

export default function AdminAuditLogsPage() {
  const { user } = useAuth();
  const [logs, setLogs] = useState<AuditLogResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSuperAdmin, setIsSuperAdmin] = useState(true);

  // Filters
  const [actionFilter, setActionFilter] = useState("");
  const [resourceFilter, setResourceFilter] = useState("ALL");
  const [selectedLog, setSelectedLog] = useState<AuditLogResponse | null>(null);

  const fetchLogs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      params.append("page", page.toString());
      params.append("limit", limit.toString());
      if (actionFilter.trim()) params.append("action", actionFilter.trim());
      if (resourceFilter !== "ALL") params.append("resource_type", resourceFilter);

      const res = await apiClient.get<AuditLogListResponse>(
        `/admin/audit-logs?${params.toString()}`
      );
      setLogs(res.data.items || []);
      setTotal(res.data.total || 0);
      setTotalPages(res.data.total_pages || 1);
      setIsSuperAdmin(true);
    } catch (err: unknown) {
      const e = err as { status?: number; message?: string };
      if (e.status === 403) {
        setIsSuperAdmin(false);
        setError("Super Administrator privileges are required to inspect system audit logs.");
      } else {
        setError(e.message || "Failed to retrieve audit trail entries.");
      }
    } finally {
      setLoading(false);
    }
  }, [page, limit, actionFilter, resourceFilter]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
  };

  const getActionBadge = (action: string) => {
    const act = action.toUpperCase();
    if (act.includes("CREATE") || act.includes("APPROVE") || act.includes("AWARD")) {
      return "bg-emerald-50 text-emerald-800 border-emerald-200";
    }
    if (act.includes("REJECT") || act.includes("DELETE") || act.includes("SUSPEND")) {
      return "bg-rose-50 text-rose-800 border-rose-200";
    }
    if (act.includes("UPDATE") || act.includes("EDIT") || act.includes("MODIFY")) {
      return "bg-amber-50 text-amber-800 border-amber-200";
    }
    return "bg-charcoal-100 text-charcoal-700 border-charcoal-200";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-charcoal-900 tracking-tight">
              System Audit Logs
            </h1>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-charcoal-900 text-[#F5B817] border border-charcoal-700 uppercase tracking-wider">
              Immutable
            </span>
          </div>
          <p className="text-xs text-charcoal-500 mt-1">
            Complete cryptographic audit trail of state transitions, user access, and administrative decisions.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3 py-2 text-xs font-bold rounded-xl border border-charcoal-200 text-charcoal-700 hover:bg-charcoal-50 transition-all self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Permission Blocked State */}
      {!isSuperAdmin && (
        <div className="p-8 bg-white border border-rose-200 rounded-3xl shadow-sm text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h3 className="text-base font-bold text-charcoal-900">Restricted Access</h3>
            <p className="text-xs text-charcoal-600">
              Your account ({user?.role || "ADMIN"}) does not possess the <code className="font-mono bg-charcoal-100 px-1 py-0.5 rounded">SUPER_ADMIN</code> role required to view security audit logs.
            </p>
          </div>
        </div>
      )}

      {isSuperAdmin && (
        <>
          {/* Filter Bar */}
          <form
            onSubmit={handleFilterSubmit}
            className="p-4 bg-white border border-charcoal-200 rounded-2xl shadow-xs flex flex-wrap items-center gap-3"
          >
            <div className="relative flex-1 min-w-[200px]">
              <Search className="w-4 h-4 text-charcoal-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search by action (e.g., USER_APPROVED, EVENT_CREATED)..."
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
                className="w-full text-xs pl-9 pr-3 py-2 bg-[#FAF8F3] border border-charcoal-200 rounded-xl text-charcoal-800 placeholder-charcoal-400 focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:bg-white"
              />
            </div>

            <div className="flex items-center gap-2 min-w-[170px]">
              <Filter className="w-4 h-4 text-charcoal-400 shrink-0" />
              <select
                value={resourceFilter}
                onChange={(e) => {
                  setResourceFilter(e.target.value);
                  setPage(1);
                }}
                className="w-full text-xs px-3 py-2 bg-[#FAF8F3] border border-charcoal-200 rounded-xl text-charcoal-800 focus:outline-none focus:ring-2 focus:ring-[#F5B817] focus:bg-white"
              >
                <option value="ALL">All Resource Types</option>
                <option value="USER">USER</option>
                <option value="EVENT">EVENT</option>
                <option value="REGISTRATION">REGISTRATION</option>
                <option value="ATTENDANCE">ATTENDANCE</option>
                <option value="VOLUNTEER_APPLICATION">VOLUNTEER_APPLICATION</option>
                <option value="GAMIFICATION">GAMIFICATION</option>
                <option value="AUTH">AUTH</option>
              </select>
            </div>

            <button
              type="submit"
              className="px-4 py-2 bg-[#F5B817] text-charcoal-950 font-bold text-xs rounded-xl hover:bg-[#E5AA10] transition-colors"
            >
              Filter
            </button>
          </form>

          {/* Error Banner */}
          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between">
              <span>{error}</span>
              <button
                onClick={fetchLogs}
                className="font-bold underline ml-3 shrink-0"
              >
                Retry
              </button>
            </div>
          )}

          {/* Logs Table */}
          <div className="bg-white border border-charcoal-200 rounded-2xl shadow-xs overflow-hidden">
            {loading ? (
              <div className="p-12 text-center space-y-3">
                <div className="w-8 h-8 border-3 border-charcoal-900 border-t-[#F5B817] rounded-full animate-spin mx-auto" />
                <p className="text-xs text-charcoal-500 font-medium">
                  Loading audit logs...
                </p>
              </div>
            ) : logs.length === 0 ? (
              <div className="p-12 text-center space-y-2">
                <FileText className="w-10 h-10 text-charcoal-300 mx-auto" />
                <h3 className="text-sm font-bold text-charcoal-900">
                  No Audit Logs Found
                </h3>
                <p className="text-xs text-charcoal-500 max-w-sm mx-auto">
                  No audit log records matched your query filters or none have been logged yet.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-charcoal-700">
                  <thead className="bg-[#FAF8F3] text-charcoal-600 font-bold uppercase tracking-wider text-[10px] border-b border-charcoal-200">
                    <tr>
                      <th className="px-4 py-3">Timestamp (UTC)</th>
                      <th className="px-4 py-3">Actor</th>
                      <th className="px-4 py-3">Action</th>
                      <th className="px-4 py-3">Resource</th>
                      <th className="px-4 py-3">Reason</th>
                      <th className="px-4 py-3 text-right">Payload</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-charcoal-100">
                    {logs.map((log) => (
                      <tr
                        key={log.id}
                        className="hover:bg-charcoal-50/60 transition-colors"
                      >
                        <td className="px-4 py-3 font-mono text-[11px] text-charcoal-500 whitespace-nowrap">
                          {new Date(log.created_at).toISOString().replace("T", " ").slice(0, 19)}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1.5">
                            <User className="w-3.5 h-3.5 text-charcoal-400 shrink-0" />
                            <span className="font-semibold text-charcoal-900 truncate max-w-[180px]">
                              {log.actor_email || log.actor_user_id || "System"}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-block px-2 py-0.5 rounded-md font-mono text-[10px] font-bold border ${getActionBadge(
                              log.action
                            )}`}
                          >
                            {log.action}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-medium text-charcoal-900">
                            {log.resource_type}
                          </div>
                          <div className="font-mono text-[10px] text-charcoal-400 truncate max-w-[120px]">
                            {log.resource_id}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-charcoal-600 max-w-[200px] truncate">
                          {log.reason || "—"}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => setSelectedLog(log)}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-charcoal-200 text-charcoal-700 hover:bg-white hover:text-charcoal-900 text-[11px] font-bold transition-all"
                          >
                            <Eye className="w-3 h-3" />
                            Diff
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Pagination Controls */}
            {total > 0 && (
              <div className="p-4 border-t border-charcoal-200 bg-[#FAF8F3] flex items-center justify-between text-xs text-charcoal-600">
                <span>
                  Showing {logs.length} of {total} entries (Page {page} of {totalPages})
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page <= 1 || loading}
                    className="p-1.5 rounded-lg border border-charcoal-200 hover:bg-white disabled:opacity-40 transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page >= totalPages || loading}
                    className="p-1.5 rounded-lg border border-charcoal-200 hover:bg-white disabled:opacity-40 transition-colors"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* State Diff Inspector Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-charcoal-200 overflow-hidden">
            <div className="p-5 border-b border-charcoal-200 flex items-center justify-between bg-[#FAF8F3]">
              <div>
                <h3 className="text-sm font-black text-charcoal-900 flex items-center gap-2">
                  <Code className="w-4 h-4 text-[#F5B817]" />
                  Audit State Diff — {selectedLog.action}
                </h3>
                <p className="text-[11px] text-charcoal-500 font-mono mt-0.5">
                  ID: {selectedLog.id} • {selectedLog.resource_type}:{selectedLog.resource_id}
                </p>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="p-1.5 rounded-xl text-charcoal-400 hover:text-charcoal-700 hover:bg-charcoal-200 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs font-mono">
              {selectedLog.reason && (
                <div className="p-3 rounded-xl bg-charcoal-50 border border-charcoal-200 text-charcoal-800">
                  <span className="font-bold text-[10px] text-charcoal-500 uppercase tracking-wider block font-sans mb-1">
                    Administrative Reason:
                  </span>
                  {selectedLog.reason}
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="font-bold text-[10px] text-charcoal-500 uppercase tracking-wider block font-sans mb-1.5">
                    Previous State (old_state)
                  </span>
                  <pre className="p-3 bg-charcoal-900 text-charcoal-100 rounded-xl text-[11px] overflow-x-auto max-h-64">
                    {selectedLog.old_state
                      ? JSON.stringify(selectedLog.old_state, null, 2)
                      : "null"}
                  </pre>
                </div>

                <div>
                  <span className="font-bold text-[10px] text-emerald-700 uppercase tracking-wider block font-sans mb-1.5">
                    New State (new_state)
                  </span>
                  <pre className="p-3 bg-charcoal-900 text-emerald-400 rounded-xl text-[11px] overflow-x-auto max-h-64">
                    {selectedLog.new_state
                      ? JSON.stringify(selectedLog.new_state, null, 2)
                      : "null"}
                  </pre>
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-charcoal-200 bg-[#FAF8F3] flex justify-end">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 bg-charcoal-900 text-white rounded-xl text-xs font-bold hover:bg-charcoal-800 transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

