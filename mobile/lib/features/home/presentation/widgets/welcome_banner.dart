import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/spacing.dart';

/// Warm, community-centered Welcome Banner.
/// Features personal volunteer greeting, encouraging copy, and golden
/// raised-hands crowd silhouette matching the approved reference design.
class WelcomeBanner extends StatelessWidget {
  final String volunteerName;
  final bool isLoading;

  const WelcomeBanner({
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
          vertical: 6,
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
                  // Greeting Line in Georgia
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
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 6),

                  // Supporting Message in Roboto
                  const Text(
                    'Ready to make a difference today? Explore new volunteering drives.',
                    style: TextStyle(
                      fontFamily: 'Roboto',
                      fontSize: 13,
                      color: MaatramColors.secondaryText,
                      height: 1.35,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),

            // Right Illustration: Crowd raising hands in golden tones
            SizedBox(
              width: 125,
              height: 100,
              child: ClipRRect(
                borderRadius: const BorderRadius.only(
                  topRight: Radius.circular(24),
                  bottomRight: Radius.circular(24),
                ),
                child: CustomPaint(
                  painter: _CrowdPainter(),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Custom painter for raising-hands crowd silhouette with golden warmth
class _CrowdPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    // Soft warm golden colors
    final goldDark = Paint()
      ..color = const Color(0xFFD97706).withValues(alpha: 0.85)
      ..style = PaintingStyle.fill;

    final goldMid = Paint()
      ..color = const Color(0xFFF5B817).withValues(alpha: 0.90)
      ..style = PaintingStyle.fill;

    final goldLight = Paint()
      ..color = const Color(0xFFFDE68A).withValues(alpha: 0.95)
      ..style = PaintingStyle.fill;

    // Helper to draw a stylized person with raised arm(s)
    void drawVolunteer({
      required double cx,
      required double cy,
      required double headR,
      required double armAngle1,
      required double armAngle2,
      required Paint paint,
      bool twoArms = true,
    }) {
      // Head
      canvas.drawCircle(Offset(cx, cy), headR, paint);

      // Torso / shoulders
      final bodyPath = Path();
      bodyPath.moveTo(cx - headR * 1.6, h);
      bodyPath.lineTo(cx - headR * 1.2, cy + headR * 1.6);
      bodyPath.quadraticBezierTo(cx, cy + headR * 1.3, cx + headR * 1.2, cy + headR * 1.6);
      bodyPath.lineTo(cx + headR * 1.6, h);
      bodyPath.close();
      canvas.drawPath(bodyPath, paint);

      // Arm 1
      final arm1 = Path();
      final armWidth = headR * 0.45;
      final armLen = headR * 2.8;
      arm1.moveTo(cx - headR * 1.0, cy + headR * 1.6);
      final ex1 = cx - headR * 1.0 + armLen * armAngle1;
      final ey1 = cy + headR * 1.6 - armLen * 0.9;
      arm1.lineTo(ex1, ey1);
      arm1.lineTo(ex1 + armWidth, ey1);
      arm1.lineTo(cx - headR * 1.0 + armWidth, cy + headR * 1.8);
      arm1.close();
      canvas.drawPath(arm1, paint);

      // Hand 1
      canvas.drawCircle(Offset(ex1 + armWidth * 0.5, ey1 - headR * 0.2), armWidth * 0.8, paint);

      if (twoArms) {
        // Arm 2
        final arm2 = Path();
        arm2.moveTo(cx + headR * 1.0, cy + headR * 1.6);
        final ex2 = cx + headR * 1.0 + armLen * armAngle2;
        final ey2 = cy + headR * 1.6 - armLen * 0.9;
        arm2.lineTo(ex2, ey2);
        arm2.lineTo(ex2 + armWidth, ey2);
        arm2.lineTo(cx + headR * 1.0 + armWidth, cy + headR * 1.8);
        arm2.close();
        canvas.drawPath(arm2, paint);

        // Hand 2
        canvas.drawCircle(Offset(ex2 + armWidth * 0.5, ey2 - headR * 0.2), armWidth * 0.8, paint);
      }
    }

    // Person 1 (Background left)
    drawVolunteer(
      cx: w * 0.18,
      cy: h * 0.46,
      headR: 8.0,
      armAngle1: -0.35,
      armAngle2: 0.30,
      paint: goldDark,
    );

    // Person 2 (Midground center-left)
    drawVolunteer(
      cx: w * 0.45,
      cy: h * 0.40,
      headR: 9.5,
      armAngle1: -0.25,
      armAngle2: 0.35,
      paint: goldMid,
    );

    // Person 3 (Foreground center-right)
    drawVolunteer(
      cx: w * 0.72,
      cy: h * 0.44,
      headR: 9.0,
      armAngle1: -0.40,
      armAngle2: 0.25,
      paint: goldLight,
    );

    // Person 4 (Rightmost)
    drawVolunteer(
      cx: w * 0.95,
      cy: h * 0.52,
      headR: 8.5,
      armAngle1: -0.30,
      armAngle2: 0.10,
      paint: goldMid,
    );

    // Decorative sparkles / floating stars
    final sparklePaint = Paint()
      ..color = const Color(0xFFF5B817).withValues(alpha: 0.6)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(Offset(w * 0.15, h * 0.18), 2.5, sparklePaint);
    canvas.drawCircle(Offset(w * 0.60, h * 0.15), 3.0, sparklePaint);
    canvas.drawCircle(Offset(w * 0.85, h * 0.22), 2.0, sparklePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
