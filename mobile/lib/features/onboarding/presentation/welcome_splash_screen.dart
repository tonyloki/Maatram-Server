import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/animations/fade_slide_in.dart';
import '../../../core/animations/motion_tokens.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/buttons/maatram_button.dart';

/// Phase 13 / WP1: Approved Welcome & Splash Screen for Unauthenticated Volunteers.
///
/// Faithfully recreates the mentor reference `docs/audits/ui-ux/references/ref_01_welcome_splash.jpg`:
/// - Warm ivory background (#FAF8F5) with subtle botanical wheat watermark accents.
/// - Centered official Maatram Foundation logo (Tamil script + golden sun motif).
/// - Full-width authentic volunteer team hero photograph (`assets/images/volunteers-team-hero.jpg`).
/// - Two-tone organic golden wave swoop dividing the hero image and editorial content.
/// - Editorial Georgia serif headline:
///   - "Volunteer for a" in deep navy (#1B2B48)
///   - "Better Tomorrow" in warm gold (#D49504 / #F5B817)
///   - Organic curved golden brush-stroke underline
/// - Inspiring community subtitle in Roboto (#827D73).
/// - Primary signature gold button: "Get Started" -> /register.
/// - Secondary action: "Already have an account? Sign In" -> /login.
/// - Fully responsive across 320dp, 360dp, 390dp, 430dp, and 800dp viewports.
/// - Motion entrance with reduced-motion accessibility support.
class WelcomeSplashScreen extends StatelessWidget {
  const WelcomeSplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final reducedMotion = MaatramMotion.isReducedMotion(context);
    final size = MediaQuery.sizeOf(context);
    final isCompact = size.height < 680;
    final isVeryCompact = size.height < 600;

    return Scaffold(
      backgroundColor: MaatramColors.background,
      body: Stack(
        children: [
          // 1. Top-Left Wheat Stalks Watermark
          Positioned(
            top: -10,
            left: -15,
            width: 90,
            height: 180,
            child: IgnorePointer(
              child: Opacity(
                opacity: 0.18,
                child: SvgPicture.asset(
                  'assets/decorations/wheat-stalks.svg',
                  fit: BoxFit.contain,
                ),
              ),
            ),
          ),

          // 2. Bottom-Right Organic Golden Wave Accent
          Positioned(
            right: 0,
            bottom: 0,
            width: size.width * 0.55,
            height: isCompact ? 95 : 125,
            child: IgnorePointer(
              child: CustomPaint(
                painter: const _BottomCornerWavePainter(),
                size: Size(size.width * 0.55, isCompact ? 95 : 125),
              ),
            ),
          ),

          // 3. Bottom-Left Wheat Stalks Watermark
          Positioned(
            bottom: 0,
            left: 10,
            width: 75,
            height: 120,
            child: IgnorePointer(
              child: Opacity(
                opacity: 0.14,
                child: SvgPicture.asset(
                  'assets/decorations/wheat-stalks.svg',
                  fit: BoxFit.contain,
                ),
              ),
            ),
          ),

          // 4. Main Content Body
          SafeArea(
            top: false,
            bottom: false,
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 480),
                child: LayoutBuilder(
                  builder: (context, constraints) {
                    final topSpace = isVeryCompact
                        ? 24.0
                        : isCompact
                            ? 56.0
                            : (size.height * 0.155).clamp(80.0, 135.0);

                    final heroHeight = isVeryCompact
                        ? 220.0
                        : isCompact
                            ? 280.0
                            : (size.height * 0.41).clamp(310.0, 360.0);

                    final logoHeight = isVeryCompact ? 60.0 : isCompact ? 72.0 : 86.0;

                    return SingleChildScrollView(
                      physics: const ClampingScrollPhysics(),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Top Header: Generous breathing room matching mentor reference
                          SizedBox(height: topSpace),
                          MaatramFadeSlideIn(
                            direction: SlideDirection.fromTop,
                            delay: reducedMotion
                                ? Duration.zero
                                : const Duration(milliseconds: 50),
                            distance: 12,
                            child: Center(
                              child: Image.asset(
                                'assets/images/logo.png',
                                height: logoHeight,
                                fit: BoxFit.contain,
                                semanticLabel: 'Maatram Foundation Logo',
                              ),
                            ),
                          ),
                          SizedBox(height: isVeryCompact ? 14 : isCompact ? 20 : 26),

                          // Hero Volunteer Photo with Wave Swoop Overlay
                          MaatramFadeSlideIn(
                            direction: SlideDirection.fromBottom,
                            delay: reducedMotion
                                ? Duration.zero
                                : const Duration(milliseconds: 150),
                            distance: 14,
                            child: SizedBox(
                              height: heroHeight + 24,
                              child: Stack(
                                children: [
                                  // Volunteer Photo with Organic Bottom Wave Clip
                                  Positioned(
                                    top: 0,
                                    left: 0,
                                    right: 0,
                                    height: heroHeight,
                                    child: ClipPath(
                                      clipper: const _HeroWaveClipper(),
                                      child: Image.asset(
                                        'assets/images/mentor_welcome_hero.jpg',
                                        fit: BoxFit.cover,
                                        alignment: Alignment.topCenter,
                                      ),
                                    ),
                                  ),

                                  // Two-Tone Organic Wave Swoop at Photo Base
                                  Positioned(
                                    left: 0,
                                    right: 0,
                                    bottom: 0,
                                    height: 48,
                                    child: CustomPaint(
                                      painter: const _OrganicWaveSwoopPainter(),
                                      size: const Size(double.infinity, 48),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),

                          // Editorial Headline Section
                          SizedBox(height: isVeryCompact ? 10 : isCompact ? 14 : 18),
                          MaatramFadeSlideIn(
                            direction: SlideDirection.fromBottom,
                            delay: reducedMotion
                                ? Duration.zero
                                : const Duration(milliseconds: 250),
                            distance: 16,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: MaatramSpacing.xl),
                              child: Column(
                                children: [
                                  // Line 1: "Volunteer for a"
                                  Text(
                                    'Volunteer for a',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      fontFamily:
                                          MaatramTypography.headingFamily,
                                      fontFamilyFallback: const ['Georgia', 'serif'],
                                      fontSize: isVeryCompact
                                          ? 24
                                          : isCompact
                                              ? 26
                                              : 30,
                                      fontWeight: FontWeight.w700,
                                      color: MaatramColors.deepNavy,
                                      letterSpacing: -0.4,
                                      height: 1.15,
                                    ),
                                  ),
                                  const SizedBox(height: 2),

                                  // Line 2: "Better Tomorrow"
                                  Text(
                                    'Better Tomorrow',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      fontFamily:
                                          MaatramTypography.headingFamily,
                                      fontFamilyFallback: const ['Georgia', 'serif'],
                                      fontSize: isVeryCompact
                                          ? 28
                                          : isCompact
                                              ? 32
                                              : 36,
                                      fontWeight: FontWeight.w700,
                                      color: const Color(0xFFD49504),
                                      letterSpacing: -0.5,
                                      height: 1.15,
                                    ),
                                  ),
                                  const SizedBox(height: 6),

                                  // Golden Brush-Style Underline
                                  CustomPaint(
                                    painter: const _BrushUnderlinePainter(),
                                    size: Size(isVeryCompact ? 160 : 200, 8),
                                  ),
                                ],
                              ),
                            ),
                          ),

                          // Call to Action Buttons
                          SizedBox(height: isVeryCompact ? 16 : isCompact ? 22 : 28),
                          MaatramFadeSlideIn(
                            direction: SlideDirection.fromBottom,
                            delay: reducedMotion
                                ? Duration.zero
                                : const Duration(milliseconds: 400),
                            distance: 18,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: MaatramSpacing.xxl),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: [
                                  // Primary Button: "Get Started"
                                  MaatramButton(
                                    key:
                                        const Key('welcome_get_started_button'),
                                    label: 'Get Started',
                                    size: MaatramButtonSize.lg,
                                    isFullWidth: true,
                                    onPressed: () =>
                                        context.push(RouteNames.registerPath),
                                  ),
                                  const SizedBox(height: MaatramSpacing.sm),

                                  // Secondary Action: "Already have an account? Sign In"
                                  Semantics(
                                    button: true,
                                    label: 'Already have an account? Sign In',
                                    child: InkWell(
                                      key: const Key('welcome_sign_in_button'),
                                      onTap: () =>
                                          context.push(RouteNames.loginPath),
                                      borderRadius: MaatramRadii.buttonRadius,
                                      child: Container(
                                        height: 48,
                                        alignment: Alignment.center,
                                        padding: const EdgeInsets.symmetric(
                                            horizontal: MaatramSpacing.sm),
                                        child: Text.rich(
                                          TextSpan(
                                            text: 'Already have an account? ',
                                            style: TextStyle(
                                              fontFamily:
                                                  MaatramTypography.bodyFamily,
                                              fontSize: 14,
                                              color: MaatramColors.charcoal700,
                                              fontWeight: FontWeight.w400,
                                            ),
                                            children: const [
                                              TextSpan(
                                                text: 'Sign In',
                                                style: TextStyle(
                                                  color: MaatramColors.deepNavy,
                                                  fontWeight: FontWeight.w700,
                                                  decoration:
                                                      TextDecoration.underline,
                                                ),
                                              ),
                                            ],
                                          ),
                                          textAlign: TextAlign.center,
                                        ),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          SizedBox(height: isVeryCompact ? 16 : 32),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Organic clipper matching the wave curve at the bottom of the hero photograph.
class _HeroWaveClipper extends CustomClipper<Path> {
  const _HeroWaveClipper();

  @override
  Path getClip(Size size) {
    final path = Path();
    path.lineTo(0, size.height - 24);
    path.cubicTo(
      size.width * 0.28,
      size.height - 4,
      size.width * 0.68,
      size.height - 48,
      size.width,
      size.height - 18,
    );
    path.lineTo(size.width, 0);
    path.close();
    return path;
  }

  @override
  bool shouldReclip(covariant CustomClipper<Path> oldClipper) => false;
}

/// Two-tone organic golden wave swooping across the base of the hero photograph.
class _OrganicWaveSwoopPainter extends CustomPainter {
  const _OrganicWaveSwoopPainter();

  @override
  void paint(Canvas canvas, Size size) {
    // 1. Background Rich Golden Curve
    final goldPath = Path();
    goldPath.moveTo(0, size.height * 0.28);
    goldPath.cubicTo(
      size.width * 0.30,
      size.height * 0.65,
      size.width * 0.68,
      size.height * 0.15,
      size.width,
      size.height * 0.45,
    );
    goldPath.lineTo(size.width, size.height);
    goldPath.lineTo(0, size.height);
    goldPath.close();

    final goldPaint = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Color(0xFFF5B817),
          Color(0xFFE5A800),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    canvas.drawPath(goldPath, goldPaint);

    // 2. Translucent Soft Pale Gold Layer for Depth & Light Transition
    final lightPath = Path();
    lightPath.moveTo(0, size.height * 0.45);
    lightPath.cubicTo(
      size.width * 0.28,
      size.height * 0.80,
      size.width * 0.64,
      size.height * 0.35,
      size.width,
      size.height * 0.60,
    );
    lightPath.lineTo(size.width, size.height);
    lightPath.lineTo(0, size.height);
    lightPath.close();

    final lightPaint = Paint()
      ..color = const Color(0xFFFDE68A).withValues(alpha: 0.65);

    canvas.drawPath(lightPath, lightPaint);

    // 3. Warm Ivory Ground fill blending into page background
    final groundPath = Path();
    groundPath.moveTo(0, size.height * 0.65);
    groundPath.cubicTo(
      size.width * 0.30,
      size.height * 0.92,
      size.width * 0.62,
      size.height * 0.50,
      size.width,
      size.height * 0.78,
    );
    groundPath.lineTo(size.width, size.height);
    groundPath.lineTo(0, size.height);
    groundPath.close();

    final groundPaint = Paint()..color = MaatramColors.background;
    canvas.drawPath(groundPath, groundPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// Organic tapered golden brush-style underline accent for "Better Tomorrow".
class _BrushUnderlinePainter extends CustomPainter {
  const _BrushUnderlinePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final path = Path();
    final midY = size.height * 0.5;

    // Organic stroke: tapers at both ends, thicker in the center
    path.moveTo(4, midY + 1);
    path.quadraticBezierTo(size.width * 0.48, -1, size.width - 4, midY - 1);
    path.quadraticBezierTo(size.width * 0.52, size.height + 1, 4, midY + 1);
    path.close();

    final paint = Paint()
      ..shader = const LinearGradient(
        colors: [
          Color(0xFFF5B817),
          Color(0xFFE5A800),
          Color(0xFFFAC938),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))
      ..style = PaintingStyle.fill;

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// Organic golden swoop accent rising from the bottom right corner.
class _BottomCornerWavePainter extends CustomPainter {
  const _BottomCornerWavePainter();

  @override
  void paint(Canvas canvas, Size size) {
    // 1. Soft pale gold outer rim
    final softPath = Path();
    softPath.moveTo(size.width * 0.05, size.height);
    softPath.cubicTo(
      size.width * 0.35,
      size.height * 0.90,
      size.width * 0.65,
      size.height * 0.45,
      size.width,
      0,
    );
    softPath.lineTo(size.width, size.height);
    softPath.close();

    final softPaint = Paint()
      ..color = const Color(0xFFFDE68A).withValues(alpha: 0.5)
      ..style = PaintingStyle.fill;
    canvas.drawPath(softPath, softPaint);

    // 2. Rich warm gold main curve
    final path = Path();
    path.moveTo(size.width * 0.15, size.height);
    path.cubicTo(
      size.width * 0.45,
      size.height * 0.92,
      size.width * 0.72,
      size.height * 0.52,
      size.width,
      size.height * 0.08,
    );
    path.lineTo(size.width, size.height);
    path.close();

    final paint = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.bottomRight,
        end: Alignment.topLeft,
        colors: [
          Color(0xFFF5B817),
          Color(0xFFE5A800),
          Color(0xFFFAC938),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))
      ..style = PaintingStyle.fill;

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
