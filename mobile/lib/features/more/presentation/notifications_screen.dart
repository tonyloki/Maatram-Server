import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/models/notification_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/feedback/empty_state.dart';
import '../../../core/widgets/feedback/skeleton_loader.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../data/more_repository.dart';

class NotificationsScreen extends ConsumerStatefulWidget {
  const NotificationsScreen({super.key});

  @override
  ConsumerState<NotificationsScreen> createState() =>
      _NotificationsScreenState();
}

class _NotificationsScreenState extends ConsumerState<NotificationsScreen> {
  NotificationListModel? _notifications;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadNotifications();
  }

  Future<void> _loadNotifications() async {
    final repo = ref.read(moreRepositoryProvider);
    final data = await repo.getNotifications();
    if (mounted) {
      setState(() {
        _notifications = data;
        _isLoading = false;
      });
    }
  }

  Future<void> _markAllAsRead() async {
    final repo = ref.read(moreRepositoryProvider);
    await repo.markAllNotificationsAsRead();
    _loadNotifications();
  }

  @override
  Widget build(BuildContext context) {
    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_rounded,
                color: MaatramColors.deepNavy),
            onPressed: () => context.pop(),
          ),
          title: Text(
            'Notifications',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
          actions: [
            if (_notifications != null && _notifications!.unreadCount > 0)
              TextButton(
                onPressed: _markAllAsRead,
                child: Text(
                  'Mark all read',
                  style: MaatramTypography.labelSmall.copyWith(
                    fontWeight: FontWeight.bold,
                    color: MaatramColors.deepNavy,
                  ),
                ),
              ),
          ],
        ),
        body: _isLoading
            ? const Padding(
                padding: EdgeInsets.all(MaatramSpacing.md),
                child: Column(
                  children: [
                    MaatramSkeletonBox(
                        width: double.infinity,
                        height: 72,
                        borderRadius: BorderRadius.all(Radius.circular(16))),
                    SizedBox(height: 10),
                    MaatramSkeletonBox(
                        width: double.infinity,
                        height: 72,
                        borderRadius: BorderRadius.all(Radius.circular(16))),
                    SizedBox(height: 10),
                    MaatramSkeletonBox(
                        width: double.infinity,
                        height: 72,
                        borderRadius: BorderRadius.all(Radius.circular(16))),
                  ],
                ),
              )
            : _notifications == null || _notifications!.items.isEmpty
                ? const Center(
                    child: MaatramEmptyState(
                      title: 'All Caught Up!',
                      description:
                          'You have no new notifications right now. Check back later for updates.',
                      icon: Icons.notifications_none_rounded,
                    ),
                  )
                : ListView.separated(
                    padding: const EdgeInsets.all(MaatramSpacing.md),
                    itemCount: _notifications!.items.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 10),
                    itemBuilder: (context, index) {
                      final item = _notifications!.items[index];
                      return InkWell(
                        onTap: () {
                          // Mark as read and open detail screen
                          ref
                              .read(moreRepositoryProvider)
                              .markNotificationAsRead(item.id);
                          context.push(
                            RouteNames.notificationDetailsPath
                                .replaceAll(':id', item.id),
                            extra: item,
                          );
                        },
                        borderRadius: BorderRadius.circular(20),
                        child: Container(
                          padding: const EdgeInsets.all(MaatramSpacing.md),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: MaatramRadii.cardRadius,
                            border: Border.all(
                              color: item.isRead
                                  ? MaatramColors.warmBorder
                                  : MaatramColors.primaryGold
                                      .withValues(alpha: 0.5),
                              width: item.isRead ? 1.0 : 1.5,
                            ),
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                width: 40,
                                height: 40,
                                decoration: BoxDecoration(
                                  color: item.isRead
                                      ? const Color(0xFFF3F4F6)
                                      : MaatramColors.primaryGold
                                          .withValues(alpha: 0.2),
                                  shape: BoxShape.circle,
                                ),
                                child: Icon(
                                  _getIconForType(item.type),
                                  color: item.isRead
                                      ? MaatramColors.secondaryText
                                      : MaatramColors.deepNavy,
                                  size: 20,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.spaceBetween,
                                      children: [
                                        Expanded(
                                          child: Text(
                                            item.title,
                                            style: MaatramTypography.titleSmall
                                                .copyWith(
                                              fontWeight: item.isRead
                                                  ? FontWeight.w600
                                                  : FontWeight.bold,
                                              color: MaatramColors.deepNavy,
                                            ),
                                          ),
                                        ),
                                        if (!item.isRead)
                                          Container(
                                            width: 8,
                                            height: 8,
                                            decoration: const BoxDecoration(
                                              color: MaatramColors.primaryGold,
                                              shape: BoxShape.circle,
                                            ),
                                          ),
                                      ],
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      item.message,
                                      style:
                                          MaatramTypography.bodySmall.copyWith(
                                        color: MaatramColors.secondaryText,
                                      ),
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    const SizedBox(height: 6),
                                    Text(
                                      item.formattedTimeAgo,
                                      style: TextStyle(
                                        fontSize: 11,
                                        color: MaatramColors.secondaryText
                                            .withValues(alpha: 0.8),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
      ),
    );
  }

  IconData _getIconForType(String type) {
    switch (type.toUpperCase()) {
      case 'EVENT_REGISTRATION':
      case 'EVENT_SELECTION':
        return Icons.event_available_rounded;
      case 'GAMIFICATION_POINTS':
      case 'ACHIEVEMENT':
        return Icons.stars_rounded;
      case 'BROADCAST':
        return Icons.campaign_rounded;
      default:
        return Icons.notifications_active_rounded;
    }
  }
}
