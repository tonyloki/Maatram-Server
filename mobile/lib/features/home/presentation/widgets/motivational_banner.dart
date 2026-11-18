import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/spacing.dart';

/// Section 7: Warm Motivational Banner closing the Volunteer Home Screen.
/// Displays golden trophy illustration + laurels + "Together for a Better Tomorrow"
/// matching the approved design reference.
class MotivationalBanner extends StatelessWidget {
  const MotivationalBanner({super.key});

  @override
  Widget build(BuildContext context) {
    return MaatramFadeSlideIn(
      direction: SlideDirection.fromBottom,
      delay: const Duration(milliseconds: 250),
      child: Container(
        margin: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.md,
          vertical: 10,
        ),
        decoration: BoxDecoration(
          borderRadius: MaatramRadii.cardRadius,
          gradient: const LinearGradient(
            colors: [
              Color(0xFFFFF3B0),
              Color(0xFFFEE060),
              Color(0xFFF5B817),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          border: Border.all(
            color: const Color(0xFFFBBF24),
            width: 1.0,
          ),
          boxShadow: [
            BoxShadow(
              color: MaatramColors.primaryGold.withValues(alpha: 0.15),
              blurRadius: 14,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Stack(
          children: [
            // Subtle crowd silhouette background
            Positioned.fill(
              child: ClipRRect(
                borderRadius: MaatramRadii.cardRadius,
                child: Opacity(
                  opacity: 0.12,
                  child: CustomPaint(
                    painter: _CrowdBackgroundPainter(),
                  ),
                ),
              ),
            ),

            // Foreground row
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: MaatramSpacing.md,
                vertical: 16,
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // Large golden trophy illustration
                  const SizedBox(
                    width: 68,
                    height: 68,
                    child: CustomPaint(
                      painter: _TrophyPainter(),
                    ),
                  ),
                  const SizedBox(width: MaatramSpacing.md),

                  // Motto text in Georgia
                  const Expanded(
                    child: Text(
                      'Together\nfor a Better Tomorrow',
                      style: TextStyle(
                        fontFamily: 'Georgia',
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF7C4A00),
                        height: 1.25,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Paints a golden trophy cup with laurel leaves.
class _TrophyPainter extends CustomPainter {
  const _TrophyPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    final goldMid = Paint()
      ..color = const Color(0xFFD97706)
      ..style = PaintingStyle.fill;

    final goldLight = Paint()
      ..color = const Color(0xFFFBBF24)
      ..style = PaintingStyle.fill;

    // Cup body
    final cupPath = Path();
    cupPath.moveTo(w * 0.20, h * 0.18);
    cupPath.lineTo(w * 0.80, h * 0.18);
    cupPath.cubicTo(
      w * 0.90, h * 0.30,
      w * 0.80, h * 0.52,
      w * 0.60, h * 0.56,
    );
    cupPath.lineTo(w * 0.60, h * 0.65);
    cupPath.lineTo(w * 0.70, h * 0.65);
    cupPath.lineTo(w * 0.70, h * 0.72);
    cupPath.lineTo(w * 0.30, h * 0.72);
    cupPath.lineTo(w * 0.30, h * 0.65);
    cupPath.lineTo(w * 0.40, h * 0.65);
    cupPath.lineTo(w * 0.40, h * 0.56);
    cupPath.cubicTo(
      w * 0.20, h * 0.52,
      w * 0.10, h * 0.30,
      w * 0.20, h * 0.18,
    );
    cupPath.close();
    canvas.drawPath(cupPath, goldMid);

    // Highlight stripe on cup
    final highlightPath = Path();
    highlightPath.moveTo(w * 0.30, h * 0.20);
    highlightPath.cubicTo(
      w * 0.28, h * 0.32,
      w * 0.26, h * 0.44,
      w * 0.35, h * 0.52,
    );
    highlightPath.lineTo(w * 0.42, h * 0.52);
    highlightPath.cubicTo(
      w * 0.30, h * 0.42,
      w * 0.33, h * 0.28,
      w * 0.38, h * 0.20,
    );
    highlightPath.close();
    canvas.drawPath(highlightPath, goldLight);

    // Cup rim
    final rimPaint = Paint()
      ..color = const Color(0xFFFBBF24)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(
      Offset(w * 0.20, h * 0.18),
      Offset(w * 0.80, h * 0.18),
      rimPaint,
    );

    // Base plate
    final basePaint = Paint()
      ..color = const Color(0xFFB45309)
      ..style = PaintingStyle.fill;
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(w * 0.18, h * 0.72, w * 0.64, h * 0.10),
        const Radius.circular(4),
      ),
      basePaint,
    );

    // Handles
    final handlePaint = Paint()
      ..color = const Color(0xFFD97706)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.5
      ..strokeCap = StrokeCap.round;

    // Left handle
    canvas.drawArc(
      Rect.fromCircle(center: Offset(w * 0.17, h * 0.33), radius: w * 0.14),
      0.9,
      2.8,
      false,
      handlePaint,
    );

    // Right handle
    canvas.drawArc(
      Rect.fromCircle(center: Offset(w * 0.83, h * 0.33), radius: w * 0.14),
      -0.5,
      2.8,
      false,
      handlePaint,
    );

    // Star badge on trophy face
    final starPaint = Paint()
      ..color = const Color(0xFFFFF9E6)
      ..style = PaintingStyle.fill;
    _drawStar(canvas, Offset(w * 0.50, h * 0.36), w * 0.09, starPaint);
  }

  void _drawStar(Canvas canvas, Offset center, double radius, Paint paint) {
    const points = 5;
    final path = Path();
    final innerRadius = radius * 0.42;

    for (var i = 0; i < points * 2; i++) {
      final r = i.isEven ? radius : innerRadius;
      final angle = (i * math.pi / points) - (math.pi / 2);
      final x = center.dx + r * math.cos(angle);
      final y = center.dy + r * math.sin(angle);
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _CrowdBackgroundPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF92400E)
      ..style = PaintingStyle.fill;

    final w = size.width;
    final h = size.height;

    for (var i = 0; i < 7; i++) {
      final cx = w * (0.05 + i * 0.15);
      final headR = 10.0 + (i % 3) * 2;
      canvas.drawCircle(Offset(cx, h * 0.65), headR, paint);
      canvas.drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTWH(cx - headR * 1.2, h * 0.72, headR * 2.4, h * 0.28),
          const Radius.circular(6),
        ),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
