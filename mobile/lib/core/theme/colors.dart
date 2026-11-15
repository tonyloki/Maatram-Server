import 'package:flutter/material.dart';

/// Centralized design tokens for the Maatram Volunteering & Gamification Portal mobile client.
/// Visual Source of Truth: Mentor reference layouts, warm ivory, golden accents & deep navy typography.
abstract final class MaatramColors {
  // Locked Initial Brand Tokens
  static const Color background = Color(0xFFFAF8F5); // Warm ivory background
  static const Color primaryGold = Color(0xFFF5B817); // Signature golden yellow accent
  static const Color deepNavy = Color(0xFF1B2B48); // Deep navy primary typography
  static const Color white = Color(0xFFFFFFFF); // Clean white card surface
  static const Color warmBorder = Color(0xFFEFECE6); // Organic warm neutral border
  static const Color secondaryText = Color(0xFF827D73); // Warm muted slate secondary text

  // Gold Scale
  static const Color goldLight = Color(0xFFFFF7E0);
  static const Color goldSurface = Color(0xFFFFF3D6);
  static const Color goldDark = Color(0xFFD97706);
  static const Color goldDeep = Color(0xFFB45309);

  // Navy & Charcoal Neutral Scale
  static const Color navySurface = Color(0xFF243656);
  static const Color navyMuted = Color(0xFF384B6E);
  static const Color charcoal900 = Color(0xFF1F2421);
  static const Color charcoal800 = Color(0xFF272F30);
  static const Color charcoal700 = Color(0xFF475569);
  static const Color charcoal600 = Color(0xFF64748B);
  static const Color charcoal400 = Color(0xFF94A3B8);
  static const Color stone100 = Color(0xFFF5F3EE);
  static const Color stone200 = Color(0xFFE9E5DD);
  static const Color stone300 = Color(0xFFD6D1C7);

  // Status & Feedback Tokens
  static const Color success = Color(0xFF10B981);
  static const Color successLight = Color(0xFFECFDF5);
  static const Color successDark = Color(0xFF059669);
  static const Color successBorder = Color(0xFFA7F3D0);

  static const Color error = Color(0xFFEF4444);
  static const Color errorLight = Color(0xFFFEF2F2);
  static const Color errorDark = Color(0xFFDC2626);
  static const Color errorBorder = Color(0xFFFECACA);

  static const Color warning = Color(0xFFF59E0B);
  static const Color warningLight = Color(0xFFFFFBEB);
  static const Color warningDark = Color(0xFFD97706);
  static const Color warningBorder = Color(0xFFFDE68A);

  static const Color info = Color(0xFF3B82F6);
  static const Color infoLight = Color(0xFFEFF6FF);
  static const Color infoDark = Color(0xFF1D4ED8);
  static const Color infoBorder = Color(0xFFBFDBFE);

  // Category Badges
  static const Color categoryStudent = Color(0xFF2563EB);
  static const Color categoryStudentBg = Color(0xFFEFF6FF);
  static const Color categoryStudentBorder = Color(0xFFBFDBFE);

  static const Color categoryAlumni = Color(0xFF7C3AED);
  static const Color categoryAlumniBg = Color(0xFFF5F3FF);
  static const Color categoryAlumniBorder = Color(0xFFDDD6FE);

  static const Color categoryCorporate = Color(0xFFD97706);
  static const Color categoryCorporateBg = Color(0xFFFFFBEB);
  static const Color categoryCorporateBorder = Color(0xFFFDE68A);

  // Shimmer Tokens
  static const Color shimmerBase = Color(0xFFEBE6DD);
  static const Color shimmerHighlight = Color(0xFFFAF8F5);

  // Overlays
  static const Color scrim = Color(0x66000000);
}

