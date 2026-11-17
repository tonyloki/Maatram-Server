import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/spacing.dart';

/// Warm, community-centered Illustrated Welcome Banner.
/// Features personal volunteer greeting, encouraging copy, and golden community celebration illustration.
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
        padding: const EdgeInsets.all(MaatramSpacing.md),
        decoration: BoxDecoration(
          borderRadius: MaatramRadii.cardRadius,
          gradient: const LinearGradient(
            colors: [
              Color(0xFFFFFDF8),
              Color(0xFFFFF6D9),
              Color(0xFFFEEDBA),
            ],
            stops: [0.0, 0.65, 1.0],
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
        child: Stack(
          children: [
            // Decorative Background Silhouette Graphic
            Positioned(
              right: -8,
              bottom: -10,
              top: -10,
              width: 140,
              child: Opacity(
                opacity: 0.85,
                child: CustomPaint(
                  painter: _CheeringCrowdSilhouettePainter(),
                ),
              ),
            ),

            // Content Foreground
            Row(
              children: [
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
                      const SizedBox(height: 10),

                      // Subtle golden brush underline indicator
                      Container(
                        width: 48,
                        height: 3,
                        decoration: BoxDecoration(
                          color: MaatramColors.primaryGold,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                    ],
                  ),
                ),
                // Reserved right space for crowd graphic
                const SizedBox(width: 90),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/// Custom painter rendering organic silhouettes of volunteers with raised cheering hands and subtle leaf accents
class _CheeringCrowdSilhouettePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final goldBrush = Paint()
      ..color = const Color(0xFFF5B817).withValues(alpha: 0.35)
      ..style = PaintingStyle.fill;

    final leafBrush = Paint()
      ..color = const Color(0xFFF5B817).withValues(alpha: 0.25)
      ..style = PaintingStyle.fill;

    // Raised hands & crowd silhouettes
    final crowdPath = Path();
    crowdPath.moveTo(size.width, size.height);
    crowdPath.lineTo(0, size.height);

    // Left person raising hands
    crowdPath.quadraticBezierTo(size.width * 0.1, size.height * 0.5,
        size.width * 0.2, size.height * 0.4);
    crowdPath.lineTo(size.width * 0.22, size.height * 0.25); // Left arm
    crowdPath.quadraticBezierTo(size.width * 0.25, size.height * 0.22,
        size.width * 0.28, size.height * 0.28);
    crowdPath.lineTo(size.width * 0.3, size.height * 0.45);

    // Center tall person
    crowdPath.quadraticBezierTo(size.width * 0.45, size.height * 0.3,
        size.width * 0.5, size.height * 0.15); // Hand
    crowdPath.quadraticBezierTo(size.width * 0.55, size.height * 0.12,
        size.width * 0.6, size.height * 0.2);
    crowdPath.quadraticBezierTo(size.width * 0.65, size.height * 0.38,
        size.width * 0.7, size.height * 0.35);

    // Right person cheering
    crowdPath.lineTo(size.width * 0.75, size.height * 0.18);
    crowdPath.quadraticBezierTo(size.width * 0.8, size.height * 0.15,
        size.width * 0.85, size.height * 0.24);
    crowdPath.lineTo(size.width * 0.88, size.height * 0.4);
    crowdPath.quadraticBezierTo(
        size.width * 0.95, size.height * 0.35, size.width, size.height * 0.3);
    crowdPath.lineTo(size.width, size.height);
    crowdPath.close();

    canvas.drawPath(crowdPath, goldBrush);

    // Floating subtle leaf motifs in top-right
    final leaf1 = Path();
    leaf1.moveTo(size.width * 0.75, size.height * 0.08);
    leaf1.quadraticBezierTo(size.width * 0.85, size.height * 0.04,
        size.width * 0.9, size.height * 0.12);
    leaf1.quadraticBezierTo(size.width * 0.82, size.height * 0.16,
        size.width * 0.75, size.height * 0.08);
    canvas.drawPath(leaf1, leafBrush);

    final leaf2 = Path();
    leaf2.moveTo(size.width * 0.6, size.height * 0.02);
    leaf2.quadraticBezierTo(
        size.width * 0.68, 0, size.width * 0.7, size.height * 0.06);
    leaf2.quadraticBezierTo(size.width * 0.64, size.height * 0.09,
        size.width * 0.6, size.height * 0.02);
    canvas.drawPath(leaf2, leafBrush);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
