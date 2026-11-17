import 'package:flutter/material.dart';

/// Elevation and box-shadow tokens for warm organic depth.
abstract final class MaatramShadows {
  // Soft ambient card shadow
  static const List<BoxShadow> card = [
    BoxShadow(
      color: Color(0x0A1B2B48),
      offset: Offset(0, 2),
      blurRadius: 8,
      spreadRadius: 0,
    ),
    BoxShadow(
      color: Color(0x061B2B48),
      offset: Offset(0, 1),
      blurRadius: 2,
      spreadRadius: 0,
    ),
  ];

  // Elevated card or floating bottom navigation bar
  static const List<BoxShadow> elevated = [
    BoxShadow(
      color: Color(0x141B2B48),
      offset: Offset(0, 8),
      blurRadius: 24,
      spreadRadius: -4,
    ),
    BoxShadow(
      color: Color(0x081B2B48),
      offset: Offset(0, 2),
      blurRadius: 6,
      spreadRadius: 0,
    ),
  ];

  // Modal / Bottom Sheet shadow
  static const List<BoxShadow> modal = [
    BoxShadow(
      color: Color(0x281B2B48),
      offset: Offset(0, -4),
      blurRadius: 32,
      spreadRadius: 0,
    ),
  ];

  // Golden accent glow
  static const List<BoxShadow> goldGlow = [
    BoxShadow(
      color: Color(0x40F5B817),
      offset: Offset(0, 4),
      blurRadius: 16,
      spreadRadius: 0,
    ),
  ];
}
