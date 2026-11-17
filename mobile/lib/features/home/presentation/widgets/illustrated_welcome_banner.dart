import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/spacing.dart';

/// Warm, community-centered Illustrated Welcome Banner.
/// Features personal volunteer greeting, encouraging copy, and vivid golden
/// raised-hands crowd silhouette matching the reference design.
class IllustratedWelcomeBanner extends StatelessWidget {
  final String volunteerName;
  final bool isLoading;

  const IllustratedWelcomeBanner({
    super.key,
    required this.volunteerName,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final displayName = volunteerName.isNotEmpty ? volunteerName : 'Volunteer';

    return MaatramFadeSlideIn(
      direction: SlideDirection.fromTop,
      child: Container(
        margin: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.md,
          vertical: MaatramSpacing.xs,
        ),
        padding: const EdgeInsets.fromLTRB(
          MaatramSpacing.md,
          MaatramSpacing.md,
          0,
          MaatramSpacing.md,
        ),
        decoration: BoxDecoration(
          borderRadius: MaatramRadii.cardRadius,
          gradient: const LinearGradient(
            colors: [
              Color(0xFFFFFDF8),
              Color(0xFFFFF6D9),
              Color(0xFFFEEDBA),
            ],
            stops: [0.0, 0.55, 1.0],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          border: Border.all(
            color: const Color(0xFFFBE6B3),
            width: 1.0,
          ),
          boxShadow: [
            BoxShadow(
              color: MaatramColors.primaryGold.withValues(alpha: 0.08),
              blurRadius: 16,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Left content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Greeting Line
                  RichText(
                    text: TextSpan(
                      style: const TextStyle(
                        fontFamily: 'Georgia',
                        fontSize: 21,
                        color: MaatramColors.deepNavy,
                        height: 1.25,
                      ),
                      children: [
                        const TextSpan(text: 'Hello, '),
                        TextSpan(
                          text: displayName,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: MaatramColors.deepNavy,
                          ),
                        ),
                        const TextSpan(text: ' 👋'),
                      ],
                    ),
                  ),
                  const SizedBox(height: 6),

                  // Inspiring Community Copy
                  const Text(
                    "Let's continue making\na difference together!",
                    style: TextStyle(
                      fontFamily: 'Roboto',
                      fontSize: 13,
                      color: Color(0xFF6B655B),
                      height: 1.35,
                      fontWeight: FontWeight.w400,
                    ),
                  ),
                ],
              ),
            ),

            // Right: vivid crowd silhouette
            SizedBox(
              width: 120,
              height: 100,
              child: CustomPaint(
                painter: _CheeringCrowdSilhouettePainter(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Vivid golden raised-hands crowd silhouette with sparkle accents.
/// Matches the reference image: 5 distinct people, raised arms, sparkles above.
class _CheeringCrowdSilhouettePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    // ── Main crowd body fill (solid golden) ──────────────────────────
    final bodyPaint = Paint()
      ..color = const Color(0xFFF5B817).withValues(alpha: 0.80)
      ..style = PaintingStyle.fill;

    final accentPaint = Paint()
      ..color = const Color(0xFFD97706).withValues(alpha: 0.65)
      ..style = PaintingStyle.fill;

    // ── Leaf decorations (top-right, like reference) ──────────────────
    final leafPaint = Paint()
      ..color = const Color(0xFFF5B817).withValues(alpha: 0.55)
      ..style = PaintingStyle.fill;

    // Top-right large leaf
    final leaf1 = Path();
    leaf1.moveTo(w * 0.70, h * 0.00);
    leaf1.cubicTo(w * 0.90, h * -0.05, w * 1.05, h * 0.12, w * 0.95, h * 0.22);
    leaf1.cubicTo(w * 0.80, h * 0.30, w * 0.60, h * 0.18, w * 0.70, h * 0.00);
    canvas.drawPath(leaf1, leafPaint);

    // Smaller secondary leaf
    final leaf2 = Path();
    leaf2.moveTo(w * 0.55, h * 0.02);
    leaf2.cubicTo(w * 0.68, h * -0.02, w * 0.76, h * 0.10, w * 0.68, h * 0.16);
    leaf2.cubicTo(w * 0.58, h * 0.20, w * 0.50, h * 0.10, w * 0.55, h * 0.02);
    canvas.drawPath(leaf2, leafPaint);

    // ── Crowd silhouette (5 people with raised arms) ──────────────────
    // Person 1 – far left, short
    _drawPerson(canvas, bodyPaint,
      cx: w * 0.08, baseY: h * 0.98,
      bodyH: h * 0.42, bodyW: w * 0.10,
      armAngleLeft: -0.9, armAngleRight: -1.3,
      armLen: h * 0.25,
    );

    // Person 2 – left-center
    _drawPerson(canvas, bodyPaint,
      cx: w * 0.26, baseY: h * 0.98,
      bodyH: h * 0.52, bodyW: w * 0.11,
      armAngleLeft: -1.1, armAngleRight: -0.7,
      armLen: h * 0.28,
    );

    // Person 3 – center (tallest)
    _drawPerson(canvas, accentPaint,
      cx: w * 0.46, baseY: h * 0.98,
      bodyH: h * 0.62, bodyW: w * 0.13,
      armAngleLeft: -1.2, armAngleRight: -1.0,
      armLen: h * 0.32,
    );

    // Person 4 – right-center
    _drawPerson(canvas, bodyPaint,
      cx: w * 0.66, baseY: h * 0.98,
      bodyH: h * 0.50, bodyW: w * 0.11,
      armAngleLeft: -0.8, armAngleRight: -1.2,
      armLen: h * 0.27,
    );

    // Person 5 – far right
    _drawPerson(canvas, bodyPaint,
      cx: w * 0.84, baseY: h * 0.98,
      bodyH: h * 0.44, bodyW: w * 0.10,
      armAngleLeft: -1.0, armAngleRight: -0.6,
      armLen: h * 0.24,
    );

    // ── Sparkles / starburst accents above crowd ──────────────────────
    final sparklePaint = Paint()
      ..color = const Color(0xFFD97706).withValues(alpha: 0.80)
      ..style = PaintingStyle.fill;

    _drawSparkle(canvas, sparklePaint, Offset(w * 0.30, h * 0.22), 4.5);
    _drawSparkle(canvas, sparklePaint, Offset(w * 0.50, h * 0.10), 5.5);
    _drawSparkle(canvas, sparklePaint, Offset(w * 0.68, h * 0.26), 3.5);
  }

  /// Draws a simplified human silhouette with arms raised.
  void _drawPerson(
    Canvas canvas,
    Paint paint, {
    required double cx,
    required double baseY,
    required double bodyH,
    required double bodyW,
    required double armAngleLeft,
    required double armAngleRight,
    required double armLen,
  }) {
    final halfW = bodyW / 2;
    final headR = bodyW * 0.42;
    final shoulderY = baseY - bodyH;
    final headY = shoulderY - headR;

    // Body (rounded rectangle)
    final bodyPath = Path();
    bodyPath.addRRect(RRect.fromRectAndRadius(
      Rect.fromLTRB(cx - halfW, shoulderY, cx + halfW, baseY),
      Radius.circular(halfW * 0.6),
    ));
    canvas.drawPath(bodyPath, paint);

    // Head
    canvas.drawCircle(Offset(cx, headY), headR, paint);

    // Left arm raised
    final armPaint = Paint()
      ..color = paint.color
      ..strokeWidth = bodyW * 0.38
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    canvas.drawLine(
      Offset(cx - halfW * 0.6, shoulderY + bodyH * 0.08),
      Offset(
        cx - halfW * 0.6 + armLen * _cos(armAngleLeft),
        shoulderY + bodyH * 0.08 + armLen * _sin(armAngleLeft),
      ),
      armPaint,
    );

    // Right arm raised
    canvas.drawLine(
      Offset(cx + halfW * 0.6, shoulderY + bodyH * 0.08),
      Offset(
        cx + halfW * 0.6 + armLen * _cos(armAngleRight),
        shoulderY + bodyH * 0.08 + armLen * _sin(armAngleRight),
      ),
      armPaint,
    );
  }

  /// Draws a 4-point sparkle star.
  void _drawSparkle(Canvas canvas, Paint paint, Offset center, double r) {
    final path = Path();
    final inner = r * 0.35;
    for (int i = 0; i < 8; i++) {
      final angle = (i * 3.14159265 / 4);
      final radius = i.isEven ? r : inner;
      final x = center.dx + radius * _cos(angle - 3.14159265 / 2);
      final y = center.dy + radius * _sin(angle - 3.14159265 / 2);
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    path.close();
    canvas.drawPath(path, paint);
  }

  double _cos(double radians) => _cosine(radians);
  double _sin(double radians) => _sine(radians);

  // Minimal trig (avoids dart:math import in painter)
  static double _cosine(double x) {
    // Taylor series cos(x) accurate for our small ranges
    double result = 1.0;
    double term = 1.0;
    for (int i = 1; i <= 8; i++) {
      term *= -x * x / ((2 * i - 1) * (2 * i));
      result += term;
    }
    return result;
  }

  static double _sine(double x) {
    double result = x;
    double term = x;
    for (int i = 1; i <= 8; i++) {
      term *= -x * x / ((2 * i) * (2 * i + 1));
      result += term;
    }
    return result;
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
