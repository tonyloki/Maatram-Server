"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bell,
  CheckCircle2,
  Calendar,
  Award,
  AlertCircle,
  Loader2,
  ArrowRight,
  CheckCheck,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { NotificationItem, NotificationListResponse } from "@/types";
import { fadeInUp, staggerContainer } from "@/lib/animations";

export default function VolunteerNotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadNotifications = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiClient<NotificationListResponse>("/notifications/me", {
        params: { page: 1, limit: 50 },
      });
      setNotifications(res.items || []);
      setUnreadCount(res.unread_count || 0);
    } catch (err: unknown) {
      console.error("Failed to load notifications", err);
      setError("Unable to load notifications at this time.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);

  const handleMarkAsRead = async (id: string) => {
    // Optimistic update
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n))
    );
    setUnreadCount((c) => Math.max(0, c - 1));

    try {
      await apiClient(`/notifications/${id}/read`, { method: "PATCH" });
    } catch (err: unknown) {
      console.warn("Failed to mark notification as read", err);
    }
  };

  const handleMarkAllAsRead = async () => {
    setNotifications((prev) =>
      prev.map((n) => ({ ...n, is_read: true, read_at: new Date().toISOString() }))
    );
    setUnreadCount(0);

    try {
      await apiClient("/notifications/read-all", { method: "POST" });
    } catch (err: unknown) {
      console.warn("Failed to mark all notifications as read", err);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "EVENT":
      case "EVENT_REGISTRATION":
      case "EVENT_REMINDER":
        return <Calendar className="w-5 h-5 text-sky-600" />;
      case "GAMIFICATION":
      case "BADGE_EARNED":
      case "POINTS_AWARDED":
        return <Award className="w-5 h-5 text-amber-500" />;
      case "APPLICATION_APPROVED":
      case "ATTENDANCE_VERIFIED":
        return <CheckCircle2 className="w-5 h-5 text-emerald-600" />;
      default:
        return <Bell className="w-5 h-5 text-primary-600" />;
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-16">
      {/* Page Title & Mark All Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-charcoal-900 tracking-tight font-serif">
            Notifications
          </h1>
          <p className="text-sm text-charcoal-500 mt-1">
            Stay informed about your registrations, attendance approvals, and badge achievements.
          </p>
        </div>

        {unreadCount > 0 && (
          <button
            type="button"
            onClick={handleMarkAllAsRead}
            className="self-start sm:self-auto inline-flex items-center gap-1.5 px-4 py-2 rounded-xl border border-charcoal-200/80 hover:border-charcoal-400 bg-white text-xs md:text-sm font-semibold text-charcoal-800 shadow-xs hover:bg-charcoal-50 transition-colors"
          >
            <CheckCheck className="w-4 h-4 text-primary-600" /> Mark all as read
          </button>
        )}
      </div>

      {/* Notifications List */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-charcoal-200/80">
          <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
          <p className="text-sm font-medium text-charcoal-500 mt-3">Loading notifications...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center text-red-700">
          <AlertCircle className="w-8 h-8 mx-auto text-red-500 mb-2" />
          <p className="font-semibold">{error}</p>
          <button
            onClick={loadNotifications}
            className="mt-3 px-4 py-1.5 bg-red-600 text-white rounded-xl text-sm font-medium hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      ) : notifications.length === 0 ? (
        <div className="bg-white rounded-3xl border border-charcoal-200/80 p-12 text-center">
          <div className="w-12 h-12 bg-charcoal-100 rounded-full flex items-center justify-center mx-auto text-charcoal-400 mb-3">
            <Bell className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-charcoal-900">You are all caught up!</h3>
          <p className="text-sm text-charcoal-500 mt-1 max-w-sm mx-auto">
            No unread alerts or notifications at this time.
          </p>
        </div>
      ) : (
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="space-y-3"
        >
          {notifications.map((n) => (
            <motion.div
              key={n.id}
              variants={fadeInUp}
              className={`p-4 md:p-5 rounded-2xl border transition-all flex items-start gap-4 ${
                n.is_read
                  ? "bg-white border-charcoal-200/70 opacity-80"
                  : "bg-primary-50/40 border-primary-200/90 shadow-xs"
              }`}
            >
              <div className="w-10 h-10 rounded-xl bg-white border border-charcoal-200/80 flex items-center justify-center flex-shrink-0 shadow-2xs">
                {getNotificationIcon(n.type)}
              </div>

              <div className="flex-1 min-w-0 space-y-1">
                <div className="flex items-center justify-between gap-2">
                  <h4 className="text-sm md:text-base font-bold text-charcoal-900 truncate">{n.title}</h4>
                  <span className="text-[11px] text-charcoal-400 whitespace-nowrap">
                    {new Date(n.created_at).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "short",
                      hour: "numeric",
                      minute: "2-digit",
                      hour12: true,
                    })}
                  </span>
                </div>
                <p className="text-xs md:text-sm text-charcoal-600 leading-relaxed">{n.message}</p>

                {/* Optional action or mark read link */}
                <div className="flex items-center gap-4 pt-1.5">
                  {n.action_url && (
                    <Link
                      href={n.action_url}
                      className="inline-flex items-center gap-1 text-xs font-bold text-primary-800 hover:text-primary-950 hover:underline"
                    >
                      View Details <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  )}
                  {!n.is_read && (
                    <button
                      type="button"
                      onClick={() => handleMarkAsRead(n.id)}
                      className="text-xs font-semibold text-charcoal-500 hover:text-charcoal-800 transition-colors"
                    >
                      Mark as read
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}

