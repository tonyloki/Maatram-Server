import 'package:flutter/material.dart';
import 'colors.dart';

/// Centralized typographic scale combining editorial serif headings with crisp modern sans body.
abstract final class MaatramTypography {
  // Heading font family defaults to serif (e.g. Georgia / editorial serif fallback)
  static const String headingFamily = 'Georgia';
  // Body font family defaults to sans-serif
  static const String bodyFamily = 'Roboto';

  // Display / Editorial Headings
  static const TextStyle displayLarge = TextStyle(
    fontFamily: headingFamily,
    fontSize: 32,
    fontWeight: FontWeight.w700,
    color: MaatramColors.deepNavy,
    letterSpacing: -0.5,
    height: 1.2,
  );

  static const TextStyle displayMedium = TextStyle(
    fontFamily: headingFamily,
    fontSize: 26,
    fontWeight: FontWeight.w700,
    color: MaatramColors.deepNavy,
    letterSpacing: -0.3,
    height: 1.25,
  );

  static const TextStyle displaySmall = TextStyle(
    fontFamily: headingFamily,
    fontSize: 22,
    fontWeight: FontWeight.w700,
    color: MaatramColors.deepNavy,
    letterSpacing: -0.2,
    height: 1.3,
  );

  // Headlines
  static const TextStyle headlineMedium = TextStyle(
    fontFamily: headingFamily,
    fontSize: 20,
    fontWeight: FontWeight.w600,
    color: MaatramColors.deepNavy,
    height: 1.35,
  );

  static const TextStyle headlineSmall = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 18,
    fontWeight: FontWeight.w700,
    color: MaatramColors.deepNavy,
    height: 1.35,
  );

  // Titles
  static const TextStyle titleLarge = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 16,
    fontWeight: FontWeight.w700,
    color: MaatramColors.deepNavy,
    height: 1.4,
  );

  static const TextStyle titleMedium = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 15,
    fontWeight: FontWeight.w600,
    color: MaatramColors.charcoal900,
    height: 1.4,
  );

  static const TextStyle titleSmall = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 13,
    fontWeight: FontWeight.w600,
    color: MaatramColors.charcoal900,
    height: 1.4,
  );

  // Body
  static const TextStyle bodyLarge = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 15,
    fontWeight: FontWeight.w400,
    color: MaatramColors.charcoal800,
    height: 1.5,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: MaatramColors.charcoal800,
    height: 1.5,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: MaatramColors.secondaryText,
    height: 1.45,
  );

  // Labels & Badges
  static const TextStyle labelLarge = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 14,
    fontWeight: FontWeight.w700,
    color: MaatramColors.deepNavy,
    letterSpacing: 0.2,
  );

  static const TextStyle labelMedium = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 12,
    fontWeight: FontWeight.w700,
    letterSpacing: 0.3,
  );

  static const TextStyle labelSmall = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 11,
    fontWeight: FontWeight.w700,
    letterSpacing: 0.4,
  );

  // Number / Stat Display
  static const TextStyle statNumberLarge = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 28,
    fontWeight: FontWeight.w800,
    color: MaatramColors.deepNavy,
    letterSpacing: -0.5,
  );

  static const TextStyle statNumberMedium = TextStyle(
    fontFamily: bodyFamily,
    fontSize: 22,
    fontWeight: FontWeight.w800,
    color: MaatramColors.deepNavy,
  );

  // Aliases for M2 Ergonomics
  static const TextStyle headlineLarge = displayMedium;
  static const TextStyle caption = bodySmall;
  static const TextStyle cardTitle = titleMedium;
}
