import 'package:flutter/material.dart';
import '../../animations/animated_counter.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';
import 'maatram_card.dart';

/// Statistical summary card displaying an icon, count, and metric label.
class MaatramStatCard extends StatelessWidget {
  final String label;
  final num value;
  final IconData icon;
  final Color iconColor;
  final Color iconBackgroundColor;
  final String? prefix;
  final String? suffix;
  final String? subtitle;
  final VoidCallback? onTap;

  const MaatramStatCard({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
    this.iconColor = MaatramColors.primaryGold,
    this.iconBackgroundColor = MaatramColors.goldSurface,
    this.prefix,
    this.suffix,
    this.subtitle,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MaatramCard(
      onTap: onTap,
      padding: MaatramSpacing.compactCardPadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: iconBackgroundColor,
                  borderRadius: MaatramRadii.radiusLg,
                ),
                child: Icon(icon, size: 20, color: iconColor),
              ),
              if (subtitle != null)
                Text(
                  subtitle!,
                  style: MaatramTypography.bodySmall.copyWith(
                    fontWeight: FontWeight.w600,
                    color: MaatramColors.secondaryText,
                  ),
                ),
            ],
          ),
          const SizedBox(height: MaatramSpacing.md),
          MaatramAnimatedCounter(
            value: value,
            prefix: prefix,
            suffix: suffix,
            style: MaatramTypography.statNumberLarge,
          ),
          const SizedBox(height: MaatramSpacing.xxs),
          Text(
            label,
            style: MaatramTypography.bodySmall.copyWith(
              fontWeight: FontWeight.w600,
              color: MaatramColors.charcoal700,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
