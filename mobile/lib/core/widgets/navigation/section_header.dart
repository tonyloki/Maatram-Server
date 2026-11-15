import 'package:flutter/material.dart';
import '../../animations/pressable.dart';
import '../../theme/colors.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';

/// Editorial section header displaying section title, subtitle, and action link.
class MaatramSectionHeader extends StatelessWidget {
  final String title;
  final String? subtitle;
  final String? actionLabel;
  final VoidCallback? onAction;

  const MaatramSectionHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.actionLabel,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: MaatramSpacing.sm),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  title,
                  style: MaatramTypography.headlineMedium,
                ),
                if (subtitle != null) ...[
                  const SizedBox(height: MaatramSpacing.xxs),
                  Text(
                    subtitle!,
                    style: MaatramTypography.bodySmall,
                  ),
                ],
              ],
            ),
          ),
          if (actionLabel != null && onAction != null)
            MaatramPressable(
              onTap: onAction,
              child: Padding(
                padding: const EdgeInsets.only(bottom: 2.0),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      actionLabel!,
                      style: MaatramTypography.labelSmall.copyWith(
                        color: MaatramColors.goldDark,
                      ),
                    ),
                    const SizedBox(width: 2),
                    const Icon(
                      Icons.chevron_right_rounded,
                      size: 16,
                      color: MaatramColors.goldDark,
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

