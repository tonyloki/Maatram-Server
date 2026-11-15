import 'package:flutter/widgets.dart';

/// Centralized motion tokens defining timing, easing curves, and accessibility compliance.
abstract final class MaatramMotion {
  // Durations
  static const Duration durationFast = Duration(milliseconds: 150);
  static const Duration durationNormal = Duration(milliseconds: 250);
  static const Duration durationMedium = Duration(milliseconds: 400);
  static const Duration durationSlow = Duration(milliseconds: 600);

  // Curves (natural, purposeful easing without excessive bounce)
  static const Curve curveEntrance = Curves.easeOutCubic;
  static const Curve curveExit = Curves.easeInCubic;
  static const Curve curveStandard = Curves.easeInOutCubic;
  static const Curve curveExpressive = Curves.fastOutSlowIn;

  /// Check whether the user has requested reduced motion in system accessibility settings.
  static bool isReducedMotion(BuildContext context) {
    return MediaQuery.maybeOf(context)?.accessibleNavigation ?? false;
  }

  /// Get effective duration considering reduced-motion accessibility setting.
  static Duration getEffectiveDuration(BuildContext context, Duration standardDuration) {
    if (isReducedMotion(context)) {
      return Duration.zero;
    }
    return standardDuration;
  }
}

