import 'package:intl/intl.dart';
import 'package:meta/meta.dart';

/// Models an in-app notification from `GET /api/v1/notifications/me`.
@immutable
class NotificationModel {
  final String id;
  final String userId;
  final String title;
  final String message;
  final String type;
  final String? actionUrl;
  final bool isRead;
  final DateTime? readAt;
  final DateTime createdAt;

  const NotificationModel({
    required this.id,
    required this.userId,
    required this.title,
    required this.message,
    required this.type,
    this.actionUrl,
    required this.isRead,
    this.readAt,
    required this.createdAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id']?.toString() ?? '',
      userId: json['user_id']?.toString() ?? '',
      title: json['title']?.toString() ?? 'Notification',
      message: json['message']?.toString() ?? (json['body']?.toString() ?? ''),
      type: json['type']?.toString() ??
          (json['notification_type']?.toString() ?? 'SYSTEM'),
      actionUrl: json['action_url']?.toString(),
      isRead: json['is_read'] as bool? ?? false,
      readAt: json['read_at'] != null
          ? DateTime.tryParse(json['read_at'] as String)
          : null,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  String get formattedTimeAgo {
    final difference = DateTime.now().difference(createdAt);
    if (difference.inMinutes < 1) return 'Just now';
    if (difference.inMinutes < 60) return '${difference.inMinutes}m ago';
    if (difference.inHours < 24) return '${difference.inHours}h ago';
    if (difference.inDays < 7) return '${difference.inDays}d ago';
    return DateFormat('d MMM').format(createdAt.toLocal());
  }

  String get fullDate =>
      DateFormat('d MMM yyyy, h:mm a').format(createdAt.toLocal());
}

/// Paginated list response for notifications
@immutable
class NotificationListModel {
  final List<NotificationModel> items;
  final int total;
  final int page;
  final int limit;
  final int totalPages;
  final int unreadCount;

  const NotificationListModel({
    required this.items,
    required this.total,
    required this.page,
    required this.limit,
    required this.totalPages,
    required this.unreadCount,
  });

  factory NotificationListModel.fromJson(Map<String, dynamic> json) {
    final list = (json['items'] as List<dynamic>?) ?? [];
    return NotificationListModel(
      items: list
          .map((i) => NotificationModel.fromJson(i as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num?)?.toInt() ?? 0,
      page: (json['page'] as num?)?.toInt() ?? 1,
      limit: (json['limit'] as num?)?.toInt() ?? 20,
      totalPages: (json['total_pages'] as num?)?.toInt() ?? 1,
      unreadCount: (json['unread_count'] as num?)?.toInt() ?? 0,
    );
  }
}
