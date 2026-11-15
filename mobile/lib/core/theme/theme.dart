import 'package:flutter/material.dart';
import 'colors.dart';
import 'radii.dart';
import 'spacing.dart';
import 'typography.dart';

/// Centralized Material 3 ThemeData definition for the Maatram Mobile client.
abstract final class MaatramTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: MaatramColors.background,
      fontFamily: MaatramTypography.bodyFamily,
      colorScheme: const ColorScheme.light(
        primary: MaatramColors.primaryGold,
        onPrimary: MaatramColors.deepNavy,
        secondary: MaatramColors.deepNavy,
        onSecondary: MaatramColors.white,
        surface: MaatramColors.white,
        onSurface: MaatramColors.charcoal900,
        error: MaatramColors.error,
        onError: MaatramColors.white,
        outline: MaatramColors.warmBorder,
      ),

      // App Bar Theme
      appBarTheme: const AppBarTheme(
        backgroundColor: MaatramColors.background,
        foregroundColor: MaatramColors.deepNavy,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: MaatramTypography.headlineMedium,
      ),

      // Card Theme
      cardTheme: CardThemeData(
        color: MaatramColors.white,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: MaatramRadii.cardRadius,
          side: const BorderSide(color: MaatramColors.warmBorder, width: 1.0),
        ),
        margin: EdgeInsets.zero,
      ),

      // Elevated Button Theme (Primary Gold)
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: MaatramColors.primaryGold,
          foregroundColor: MaatramColors.deepNavy,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: MaatramSpacing.xxl, vertical: MaatramSpacing.md),
          shape: RoundedRectangleBorder(borderRadius: MaatramRadii.buttonRadius),
          textStyle: MaatramTypography.labelLarge,
        ),
      ),

      // Outlined Button Theme
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: MaatramColors.deepNavy,
          side: const BorderSide(color: MaatramColors.warmBorder, width: 1.5),
          padding: const EdgeInsets.symmetric(horizontal: MaatramSpacing.xxl, vertical: MaatramSpacing.md),
          shape: RoundedRectangleBorder(borderRadius: MaatramRadii.buttonRadius),
          textStyle: MaatramTypography.labelLarge,
        ),
      ),

      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: MaatramColors.white,
        contentPadding: const EdgeInsets.symmetric(horizontal: MaatramSpacing.lg, vertical: MaatramSpacing.md),
        border: OutlineInputBorder(
          borderRadius: MaatramRadii.radiusLg,
          borderSide: const BorderSide(color: MaatramColors.warmBorder, width: 1.0),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: MaatramRadii.radiusLg,
          borderSide: const BorderSide(color: MaatramColors.warmBorder, width: 1.0),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: MaatramRadii.radiusLg,
          borderSide: const BorderSide(color: MaatramColors.primaryGold, width: 1.8),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: MaatramRadii.radiusLg,
          borderSide: const BorderSide(color: MaatramColors.error, width: 1.2),
        ),
        hintStyle: MaatramTypography.bodyMedium.copyWith(color: MaatramColors.secondaryText),
        labelStyle: MaatramTypography.bodyMedium.copyWith(color: MaatramColors.charcoal700),
      ),

      // Divider Theme
      dividerTheme: const DividerThemeData(
        color: MaatramColors.warmBorder,
        thickness: 1.0,
        space: 1.0,
      ),
    );
  }
}
