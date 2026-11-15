import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';
import '../badges/category_badge.dart';
import '../badges/points_badge.dart';
import '../badges/status_badge.dart';
import 'maatram_card.dart';

/// Reusable event card primitive showing event meta, dates, location, and points reward.
class MaatramEventCard extends StatelessWidget {
  final String title;
  final VolunteerCategory category;
  final String dateText;
  final String timeText;
  final String locationText;
  final num points;
  final MaatramStatus? status;
  final bool isOnline;
  final VoidCallback? onTap;

  const MaatramEventCard({
    super.key,
    required this.title,
    required this.category,
    required this.dateText,
    required this.timeText,
    required this.locationText,
    this.points = 10,
    this.status,
    this.isOnline = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MaatramCard(
      onTap: onTap,
      padding: MaatramSpacing.cardPadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top row: Category Badge + Status / Points
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              MaatramCategoryBadge(category: category, isCompact: true),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (status != null) ...[
                    MaatramStatusBadge(status: status!),
                    const SizedBox(width: MaatramSpacing.xs),
                  ],
                  MaatramPointsBadge(points: points),
                ],
              ),
            ],
          ),
          const SizedBox(height: MaatramSpacing.md),

          // Event Title
          Text(
            title,
            style: MaatramTypography.titleLarge,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: MaatramSpacing.md),

          // Details row: Date, Time & Location
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: MaatramSpacing.md,
              vertical: MaatramSpacing.sm,
            ),
            decoration: BoxDecoration(
              color: MaatramColors.background,
              borderRadius: MaatramRadii.radiusMd,
              border: Border.all(color: MaatramColors.warmBorder, width: 1.0),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.calendar_today_outlined,
                  size: 14,
                  color: MaatramColors.charcoal600,
                ),
                const SizedBox(width: 6),
                Text(
                  '$dateText • $timeText',
                  style: MaatramTypography.bodySmall.copyWith(
                    fontWeight: FontWeight.w600,
                    color: MaatramColors.charcoal800,
                  ),
                ),
                const Spacer(),
                Icon(
                  isOnline ? Icons.videocam_outlined : Icons.location_on_outlined,
                  size: 14,
                  color: isOnline ? MaatramColors.infoDark : MaatramColors.charcoal600,
                ),
                const SizedBox(width: 4),
                Text(
                  locationText,
                  style: MaatramTypography.bodySmall.copyWith(
                    color: isOnline ? MaatramColors.infoDark : MaatramColors.charcoal700,
                    fontWeight: FontWeight.w500,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

