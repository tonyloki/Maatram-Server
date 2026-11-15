import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';
import '../buttons/maatram_button.dart';

/// Reusable empty state display for empty rosters, event queries, or notifications.
class MaatramEmptyState extends StatelessWidget {
  final String title;
  final String description;
  final IconData icon;
  final String? actionLabel;
  final VoidCallback? onAction;

  const MaatramEmptyState({
    super.key,
    required this.title,
    required this.description,
    this.icon = Icons.spa_outlined,
    this.actionLabel,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: MaatramSpacing.xxl,
        vertical: MaatramSpacing.xxxl,
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: MaatramColors.goldSurface,
                shape: BoxShape.circle,
                border: Border.all(
                  color: MaatramColors.primaryGold.withOpacity(0.3),
                  width: 1.5,
                ),
              ),
              child: Icon(icon, size: 36, color: MaatramColors.goldDark),
            ),
            const SizedBox(height: MaatramSpacing.lg),
            Text(
              title,
              textAlign: TextAlign.center,
              style: MaatramTypography.titleLarge,
            ),
            const SizedBox(height: MaatramSpacing.sm),
            Text(
              description,
              textAlign: TextAlign.center,
              style: MaatramTypography.bodyMedium.copyWith(
                color: MaatramColors.secondaryText,
              ),
            ),
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: MaatramSpacing.xl),
              MaatramButton(
                label: actionLabel!,
                onPressed: onAction,
                size: MaatramButtonSize.sm,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

