import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/spacing.dart';

/// Section 7: Warm Inspiration Banner closing the Home Screen.
/// Displays "Together for a Better Tomorrow" with golden celebration motifs.
class InspirationBanner extends StatelessWidget {
  const InspirationBanner({super.key});

  @override
  Widget build(BuildContext context) {
    return MaatramFadeSlideIn(
      direction: SlideDirection.fromBottom,
      delay: const Duration(milliseconds: 250),
      child: Container(
        margin: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.md,
          vertical: MaatramSpacing.sm,
        ),
        padding: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.md,
          vertical: MaatramSpacing.md,
        ),
        decoration: BoxDecoration(
          borderRadius: MaatramRadii.cardRadius,
          gradient: const LinearGradient(
            colors: [
              Color(0xFFFFF9E6),
              Color(0xFFFEE8A2),
              Color(0xFFFDD976),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          border: Border.all(
            color: const Color(0xFFFBE094),
            width: 1.0,
          ),
          boxShadow: [
            BoxShadow(
              color: MaatramColors.primaryGold.withValues(alpha: 0.1),
              blurRadius: 12,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        child: Row(
          children: [
            // 1. Golden Trophy Icon Container with Laurel Leaves
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.85),
                shape: BoxShape.circle,
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x10000000),
                    blurRadius: 6,
                    offset: Offset(0, 2),
                  ),
                ],
              ),
              child: const Icon(
                Icons.emoji_events_rounded,
                size: 32,
                color: Color(0xFFD97706),
              ),
            ),
            const SizedBox(width: MaatramSpacing.md),

            // 2. Inspiring Motto
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Together\nfor a Better Tomorrow',
                    style: TextStyle(
                      fontFamily: 'Georgia',
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                      height: 1.25,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    width: 50,
                    height: 2.5,
                    decoration: BoxDecoration(
                      color: const Color(0xFFD97706),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: MaatramSpacing.sm),

            // 3. Subtle Leaf Flourish on the Right
            const Opacity(
              opacity: 0.7,
              child: Icon(
                Icons.spa_rounded,
                size: 28,
                color: Color(0xFFD97706),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
