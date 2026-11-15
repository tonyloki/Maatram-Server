import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';

/// Gamification points pill showing a golden star and numerical points reward.
class MaatramPointsBadge extends StatelessWidget {
  final num points;
  final bool isLarge;

  const MaatramPointsBadge({
    super.key,
    required this.points,
    this.isLarge = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isLarge ? MaatramSpacing.md : MaatramSpacing.sm,
        vertical: isLarge ? MaatramSpacing.xs : 3,
      ),
      decoration: BoxDecoration(
        color: MaatramColors.goldSurface,
        borderRadius: MaatramRadii.radiusPill,
        border: Border.all(color: MaatramColors.primaryGold.withOpacity(0.5), width: 1.0),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.stars_rounded,
            size: isLarge ? 16 : 13,
            color: MaatramColors.goldDark,
          ),
          const SizedBox(width: 4),
          Text(
            '+$points pts',
            style: (isLarge ? MaatramTypography.labelMedium : MaatramTypography.labelSmall).copyWith(
              color: MaatramColors.goldDark,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}

