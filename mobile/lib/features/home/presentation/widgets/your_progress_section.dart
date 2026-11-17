import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/models/gamification_summary_model.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/shadows.dart';
import '../../../../core/theme/spacing.dart';

/// Section 6: Non-numeric Volunteer Progress & Community Contribution Card.
/// Displays genuine milestone recognition and encouragement without fabricated
/// percentages or arbitrary progress targets.
class YourProgressSection extends StatelessWidget {
  final GamificationSummaryModel? summary;
  final bool isLoading;

  const YourProgressSection({
    super.key,
    this.summary,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final badgesCount = summary?.badgesEarnedCount ?? 0;
    final hasBadges = badgesCount > 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        // 1. Header
        const Padding(
          padding: EdgeInsets.fromLTRB(
            MaatramSpacing.md,
            MaatramSpacing.md,
            MaatramSpacing.md,
            MaatramSpacing.xs,
          ),
          child: Text(
            'Your Progress',
            style: TextStyle(
              fontFamily: 'Georgia',
              fontSize: 19,
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
        ),

        // 2. Contribution Card (Non-numeric milestone recognition)
        MaatramFadeSlideIn(
          direction: SlideDirection.fromBottom,
          delay: const Duration(milliseconds: 200),
          child: Container(
            margin: const EdgeInsets.symmetric(
              horizontal: MaatramSpacing.md,
              vertical: MaatramSpacing.xs,
            ),
            padding: const EdgeInsets.all(MaatramSpacing.md),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [
                  Color(0xFFFFFDF8),
                  Color(0xFFFFF8E7),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: MaatramRadii.cardRadius,
              border: Border.all(color: const Color(0xFFFDE68A)),
              boxShadow: MaatramShadows.card,
            ),
            child: Row(
              children: [
                // 1. Genuine Milestone Emblem (Badges Earned or Active Volunteer Star)
                Container(
                  width: 54,
                  height: 54,
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFF3D6),
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: const Color(0xFFFDE68A),
                      width: 1.5,
                    ),
                  ),
                  child: Center(
                    child: hasBadges
                        ? Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(
                                Icons.workspace_premium_rounded,
                                color: Color(0xFFD97706),
                                size: 20,
                              ),
                              Text(
                                '$badgesCount',
                                style: const TextStyle(
                                  fontFamily: 'Roboto',
                                  fontSize: 12,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFFB45309),
                                  height: 1.0,
                                ),
                              ),
                            ],
                          )
                        : const Icon(
                            Icons.stars_rounded,
                            color: Color(0xFFD97706),
                            size: 28,
                          ),
                  ),
                ),
                const SizedBox(width: MaatramSpacing.md),

                // 2. Inspiring Non-Numeric Message Grounded in Mission
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        hasBadges ? 'Keep going!' : 'Every Contribution Counts',
                        style: const TextStyle(
                          fontFamily: 'Roboto',
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                          color: MaatramColors.deepNavy,
                        ),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        hasBadges
                            ? "You're doing great! Complete more events to earn more points and badges."
                            : 'Join upcoming volunteer drives to earn points, unlock badges, and make a difference.',
                        style: const TextStyle(
                          fontFamily: 'Roboto',
                          fontSize: 12,
                          color: Color(0xFF6B655B),
                          height: 1.3,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: MaatramSpacing.sm),

                // 3. Ascending Gold Bar Chart Graphic
                CustomPaint(
                  size: const Size(36, 32),
                  painter: _GrowthBarsPainter(),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

/// Custom painter rendering stylized ascending bar chart with upward trend arrow
class _GrowthBarsPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final barPaint = Paint()
      ..color = const Color(0xFFF5B817)
      ..style = PaintingStyle.fill;

    final arrowPaint = Paint()
      ..color = const Color(0xFFD97706)
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    final barWidth = size.width * 0.22;
    final radius = Radius.circular(barWidth * 0.3);

    // Bar 1 (Short)
    final r1 = RRect.fromRectAndRadius(
      Rect.fromLTWH(0, size.height * 0.55, barWidth, size.height * 0.45),
      radius,
    );
    canvas.drawRRect(r1, barPaint);

    // Bar 2 (Medium)
    final r2 = RRect.fromRectAndRadius(
      Rect.fromLTWH(
          barWidth * 1.4, size.height * 0.3, barWidth, size.height * 0.7),
      radius,
    );
    canvas.drawRRect(r2, barPaint);

    // Bar 3 (Tall)
    final r3 = RRect.fromRectAndRadius(
      Rect.fromLTWH(
          barWidth * 2.8, size.height * 0.05, barWidth, size.height * 0.95),
      radius,
    );
    canvas.drawRRect(r3, barPaint);

    // Upward trend arrow above bars
    final arrowPath = Path();
    arrowPath.moveTo(size.width * 0.1, size.height * 0.35);
    arrowPath.quadraticBezierTo(
        size.width * 0.5, size.height * 0.15, size.width * 0.95, 0);

    canvas.drawPath(arrowPath, arrowPaint);

    // Arrowhead
    final head = Path();
    head.moveTo(size.width * 0.75, 0);
    head.lineTo(size.width * 0.95, 0);
    head.lineTo(size.width * 0.95, size.height * 0.15);
    canvas.drawPath(head, arrowPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
