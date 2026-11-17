import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/models/gamification_summary_model.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/shadows.dart';
import '../../../../core/theme/spacing.dart';

/// Section 6: Volunteer Progress Card.
/// Shows circular progress ring (events toward 10-event milestone),
/// motivational text, and ascending bar chart — matching the reference design.
class YourProgressSection extends StatelessWidget {
  final GamificationSummaryModel? summary;
  final bool isLoading;

  const YourProgressSection({
    super.key,
    this.summary,
    this.isLoading = false,
  });

  /// Progress toward the next milestone (10 completed events = 100%).
  double _progressFraction() {
    final completed = summary?.completedEventsCount ?? 0;
    const milestone = 10;
    return (completed / milestone).clamp(0.0, 1.0);
  }

  String _progressLabel() {
    final pct = (_progressFraction() * 100).round();
    return '$pct%';
  }

  @override
  Widget build(BuildContext context) {
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

        // 2. Progress Card
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
                // 1. Circular progress ring
                _CircularProgressRing(
                  fraction: _progressFraction(),
                  label: _progressLabel(),
                ),
                const SizedBox(width: MaatramSpacing.md),

                // 2. Motivational text
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text(
                        'Keep going!',
                        style: TextStyle(
                          fontFamily: 'Roboto',
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                          color: MaatramColors.deepNavy,
                        ),
                      ),
                      const SizedBox(height: 3),
                      const Text(
                        "You're doing great. Complete more events to earn more points.",
                        style: TextStyle(
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

                // 3. Ascending Gold Bar Chart
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

/// Circular progress ring with percentage label in the center.
class _CircularProgressRing extends StatelessWidget {
  final double fraction;
  final String label;

  const _CircularProgressRing({
    required this.fraction,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 64,
      height: 64,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background track ring
          CustomPaint(
            size: const Size(64, 64),
            painter: _RingPainter(
              fraction: 1.0,
              color: const Color(0xFFE5E0D5),
              strokeWidth: 7.0,
            ),
          ),
          // Foreground progress ring
          CustomPaint(
            size: const Size(64, 64),
            painter: _RingPainter(
              fraction: fraction,
              color: const Color(0xFFD97706),
              strokeWidth: 7.0,
            ),
          ),
          // Percentage label
          Text(
            label,
            style: const TextStyle(
              fontFamily: 'Roboto',
              fontSize: 13,
              fontWeight: FontWeight.w800,
              color: Color(0xFFB45309),
            ),
          ),
        ],
      ),
    );
  }
}

/// Paints a circular arc ring from the top (-π/2).
class _RingPainter extends CustomPainter {
  final double fraction;
  final Color color;
  final double strokeWidth;

  const _RingPainter({
    required this.fraction,
    required this.color,
    required this.strokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    final rect = Rect.fromLTWH(
      strokeWidth / 2,
      strokeWidth / 2,
      size.width - strokeWidth,
      size.height - strokeWidth,
    );

    canvas.drawArc(
      rect,
      -math.pi / 2,              // start at top
      2 * math.pi * fraction,    // sweep clockwise
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant _RingPainter old) =>
      old.fraction != fraction || old.color != color;
}

/// Custom painter rendering stylized ascending bar chart with upward trend arrow.
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
