import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/models/notification_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/layout/organic_background.dart';

class NotificationDetailsScreen extends StatelessWidget {
  final String notificationId;
  final NotificationModel? notification;

  const NotificationDetailsScreen({
    super.key,
    required this.notificationId,
    this.notification,
  });

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
            'Notification',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
        ),
        body: ListView(
          padding: const EdgeInsets.all(MaatramSpacing.md),
          children: [
            Container(
              padding: const EdgeInsets.all(MaatramSpacing.lg),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color:
                              MaatramColors.primaryGold.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          notification?.type ?? 'ALERT',
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: MaatramColors.deepNavy,
                          ),
                        ),
                      ),
                      Flexible(
                        child: Text(
                          notification?.fullDate ?? '—',
                          style: MaatramTypography.bodySmall
                              .copyWith(color: MaatramColors.secondaryText),
                          textAlign: TextAlign.end,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    notification?.title ?? 'Notification Update',
                    style: MaatramTypography.titleLarge.copyWith(
                      fontFamily: 'Georgia',
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Divider(color: MaatramColors.warmBorder),
                  const SizedBox(height: 12),
                  Text(
                    notification?.message ??
                        'Thank you for being an active part of the Maatram volunteer movement. Stay tuned for further updates.',
                    style: MaatramTypography.bodyMedium.copyWith(
                      color: MaatramColors.deepNavy,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.xl),
            if (notification?.actionUrl != null &&
                notification!.actionUrl!.isNotEmpty) ...[
              MaatramButton(
                label: 'View Related Event',
                onPressed: () {
                  context.push(notification!.actionUrl!);
                },
              ),
              const SizedBox(height: 12),
            ],
            OutlinedButton(
              onPressed: () => context.pop(),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size.fromHeight(48),
                side: const BorderSide(color: MaatramColors.warmBorder),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16)),
              ),
              child: Text(
                'Back to Notifications',
                style: MaatramTypography.labelLarge
                    .copyWith(color: MaatramColors.deepNavy),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
