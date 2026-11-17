import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/spacing.dart';

/// Section 7: Warm Inspiration Banner closing the Home Screen.
/// Shows golden trophy illustration + laurel leaves + "Together for a Better Tomorrow"
/// matching the reference design precisely.
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
                vertical: MaatramSpacing.md,
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // Large trophy illustration
                  SizedBox(
                    width: 72,
                    height: 72,
                    child: CustomPaint(
                      painter: _TrophyPainter(),
                    ),
                  ),
                  const SizedBox(width: MaatramSpacing.md),

                  // Motto text
                  const Expanded(
                    child: Text(
                      'Together\nfor a Better Tomorrow',
                      style: TextStyle(
                        fontFamily: 'Georgia',
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF7C4A00),
                        height: 1.3,
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
  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    final goldDark = Paint()
      ..color = const Color(0xFFB45309)
      ..style = PaintingStyle.fill;

    final goldMid = Paint()
      ..color = const Color(0xFFD97706)
      ..style = PaintingStyle.fill;

    final goldLight = Paint()
      ..color = const Color(0xFFFBBF24)
      ..style = PaintingStyle.fill;

    // ── Cup body ──────────────────────────────────────────────────────
    final cupPath = Path();
    // Top opening rim
    cupPath.moveTo(w * 0.20, h * 0.18);
    cupPath.lineTo(w * 0.80, h * 0.18);
    // Right side curving inward to base
    cupPath.cubicTo(
      w * 0.90, h * 0.30,
      w * 0.80, h * 0.52,
      w * 0.60, h * 0.56,
    );
    // Base stem
    cupPath.lineTo(w * 0.60, h * 0.65);
    cupPath.lineTo(w * 0.70, h * 0.65);
    cupPath.lineTo(w * 0.70, h * 0.72);
    cupPath.lineTo(w * 0.30, h * 0.72);
    cupPath.lineTo(w * 0.30, h * 0.65);
    cupPath.lineTo(w * 0.40, h * 0.65);
    cupPath.lineTo(w * 0.40, h * 0.56);
    // Left side
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

    // ── Handles ───────────────────────────────────────────────────────
    final handlePaint = Paint()
      ..color = const Color(0xFFD97706)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.5
      ..strokeCap = StrokeCap.round;

    // Left handle
    canvas.drawArc(
      Rect.fromLTWH(w * 0.02, h * 0.20, w * 0.22, h * 0.26),
      math.pi * 0.4,
      -math.pi * 0.9,
      false,
      handlePaint,
    );
    // Right handle
    canvas.drawArc(
      Rect.fromLTWH(w * 0.76, h * 0.20, w * 0.22, h * 0.26),
      math.pi * 1.6,
      -math.pi * 0.9,
      false,
      handlePaint,
    );

    // ── Star on cup ──────────────────────────────────────────────────
    _drawStar(canvas, goldLight, Offset(w * 0.50, h * 0.36), h * 0.09);

    // ── Laurel leaves ─────────────────────────────────────────────────
    _drawLaurelLeaves(canvas, goldDark, size);
  }

  void _drawStar(Canvas canvas, Paint paint, Offset center, double r) {
    final inner = r * 0.4;
    final path = Path();
    for (int i = 0; i < 10; i++) {
      final angle = (i * math.pi / 5) - math.pi / 2;
      final radius = i.isEven ? r : inner;
      final x = center.dx + radius * math.cos(angle);
      final y = center.dy + radius * math.sin(angle);
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    path.close();
    canvas.drawPath(path, paint);
  }

  void _drawLaurelLeaves(Canvas canvas, Paint paint, Size size) {
    final w = size.width;
    final h = size.height;
    final leafPaint = Paint()
      ..color = const Color(0xFF92400E)
      ..style = PaintingStyle.fill;

    // Left laurel — 4 leaves
    for (int i = 0; i < 4; i++) {
      final angle = math.pi * 0.55 + i * 0.18;
      final dist = h * 0.25 + i * h * 0.04;
      final cx = w * 0.12 + dist * math.cos(angle);
      final cy = h * 0.65 - dist * math.sin(angle);
      _drawLeaf(canvas, leafPaint, Offset(cx, cy), angle + math.pi / 2, h * 0.07);
    }

    // Right laurel — 4 leaves (mirrored)
    for (int i = 0; i < 4; i++) {
      final angle = math.pi * 0.45 - i * 0.18;
      final dist = h * 0.25 + i * h * 0.04;
      final cx = w * 0.88 - dist * math.cos(angle);
      final cy = h * 0.65 - dist * math.sin(angle);
      _drawLeaf(canvas, leafPaint, Offset(cx, cy), math.pi - angle - math.pi / 2, h * 0.07);
    }
  }

  void _drawLeaf(Canvas canvas, Paint paint, Offset center, double angle, double size) {
    final path = Path();
    final cos = math.cos(angle);
    final sin = math.sin(angle);

    path.moveTo(center.dx, center.dy);
    path.cubicTo(
      center.dx + cos * size * 0.5 - sin * size * 0.3,
      center.dy + sin * size * 0.5 + cos * size * 0.3,
      center.dx + cos * size - sin * size * 0.2,
      center.dy + sin * size + cos * size * 0.2,
      center.dx + cos * size,
      center.dy + sin * size,
    );
    path.cubicTo(
      center.dx + cos * size + sin * size * 0.2,
      center.dy + sin * size - cos * size * 0.2,
      center.dx + cos * size * 0.5 + sin * size * 0.3,
      center.dy + sin * size * 0.5 - cos * size * 0.3,
      center.dx,
      center.dy,
    );
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// Subtle crowd silhouette for banner background.
class _CrowdBackgroundPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF7C3A00)
      ..style = PaintingStyle.fill;

    final w = size.width;
    final h = size.height;

    final path = Path();
    path.moveTo(0, h);
    path.lineTo(w * 0.6, h);

    // Simple crowd bumps
    for (int i = 0; i < 8; i++) {
      final x = w * (0.6 + i * 0.06);
      final y = h * (0.3 + (i % 2 == 0 ? 0.1 : 0.0));
      path.quadraticBezierTo(x - w * 0.03, h * 0.15, x, y);
      path.quadraticBezierTo(x + w * 0.03, h * 0.15, x + w * 0.06, h * 0.4);
    }
    path.lineTo(w, h);
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
