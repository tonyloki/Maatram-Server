import 'package:flutter/material.dart';
import '../../../core/models/achievement_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/buttons/maatram_button.dart';

class AchievementDetailsModal extends StatelessWidget {
  final AchievementModel achievement;

  const AchievementDetailsModal({super.key, required this.achievement});

  @override
  Widget build(BuildContext context) {
    final isEarned = achievement.isEarned;

    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      padding: const EdgeInsets.all(MaatramSpacing.lg),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Drag handle
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: MaatramColors.warmBorder,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: MaatramSpacing.lg),

            // Large Badge Icon
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: isEarned
                    ? const Color(0xFFFEF3C7)
                    : const Color(0xFFF3F4F6),
                shape: BoxShape.circle,
                border: Border.all(
                  color: isEarned
                      ? MaatramColors.primaryGold
                      : MaatramColors.warmBorder,
                  width: 2,
                ),
              ),
              child: Icon(
                isEarned
                    ? Icons.military_tech_rounded
                    : Icons.lock_outline_rounded,
                color: isEarned
                    ? const Color(0xFFB45309)
                    : MaatramColors.secondaryText,
                size: 44,
              ),
            ),
            const SizedBox(height: MaatramSpacing.md),

            // Title
            Text(
              achievement.title,
              style: MaatramTypography.headlineSmall.copyWith(
                fontFamily: 'Georgia',
                fontWeight: FontWeight.bold,
                color: MaatramColors.deepNavy,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 6),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: isEarned
                    ? const Color(0xFFECFDF5)
                    : const Color(0xFFF3F4F6),
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(
                isEarned ? 'Unlocked' : 'Locked Milestone',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: isEarned
                      ? MaatramColors.success
                      : MaatramColors.secondaryText,
                ),
              ),
            ),
            const SizedBox(height: MaatramSpacing.md),

            // Description
            Text(
              achievement.description,
              style: MaatramTypography.bodyMedium.copyWith(
                color: MaatramColors.deepNavy,
                height: 1.4,
              ),
              textAlign: TextAlign.center,
            ),
            if (isEarned && achievement.awardedAt != null) ...[
              const SizedBox(height: 12),
              Text(
                'Awarded on ${achievement.formattedAwardedDate}',
                style: MaatramTypography.bodySmall.copyWith(
                  color: MaatramColors.secondaryText,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
            const SizedBox(height: MaatramSpacing.xl),

            MaatramButton(
              label: isEarned ? 'Share Achievement' : 'Got It',
              leadingIcon:
                  isEarned ? const Icon(Icons.share_rounded, size: 18) : null,
              onPressed: () {
                Navigator.of(context).pop();
                if (isEarned) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                        content: Text(
                            'Sharing "${achievement.title}" achievement!')),
                  );
                }
              },
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}
