import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/theme/colors.dart';
import 'package:maatram_mobile/core/theme/radii.dart';
import 'package:maatram_mobile/core/theme/spacing.dart';
import 'package:maatram_mobile/core/theme/theme.dart';
import 'package:maatram_mobile/core/theme/typography.dart';

void main() {
  group('Design Tokens Verification', () {
    test('Core Brand Colors match locked specifications', () {
      expect(MaatramColors.background, const Color(0xFFFAF8F5));
      expect(MaatramColors.primaryGold, const Color(0xFFF5B817));
      expect(MaatramColors.deepNavy, const Color(0xFF1B2B48));
      expect(MaatramColors.white, const Color(0xFFFFFFFF));
      expect(MaatramColors.warmBorder, const Color(0xFFEFECE6));
      expect(MaatramColors.secondaryText, const Color(0xFF827D73));
    });

    test('Category scale colors match specifications', () {
      expect(MaatramColors.categoryStudent, const Color(0xFF2563EB));
      expect(MaatramColors.categoryAlumni, const Color(0xFF7C3AED));
      expect(MaatramColors.categoryCorporate, const Color(0xFFD97706));
    });

    test('Spacing tokens conform to 4pt/8pt grid', () {
      expect(MaatramSpacing.xxs, 2.0);
      expect(MaatramSpacing.xs, 4.0);
      expect(MaatramSpacing.sm, 8.0);
      expect(MaatramSpacing.md, 12.0);
      expect(MaatramSpacing.lg, 16.0);
      expect(MaatramSpacing.xl, 20.0);
      expect(MaatramSpacing.xxl, 24.0);
      expect(MaatramSpacing.xxxl, 32.0);
      expect(MaatramSpacing.huge, 40.0);
      expect(MaatramSpacing.massive, 48.0);
    });

    test('Radii tokens match geometric requirements', () {
      expect(MaatramRadii.cardRadius, const BorderRadius.all(Radius.circular(24.0)));
      expect(MaatramRadii.buttonRadius, const BorderRadius.all(Radius.circular(16.0)));
      expect(MaatramRadii.pill, 999.0);
      expect(MaatramRadii.bottomSheetRadius, const BorderRadius.vertical(top: Radius.circular(32.0)));
    });

    test('Typography uses Georgia for display/headings and Roboto for body', () {
      expect(MaatramTypography.headingFamily, 'Georgia');
      expect(MaatramTypography.bodyFamily, 'Roboto');
      expect(MaatramTypography.displayLarge.fontFamily, 'Georgia');
      expect(MaatramTypography.headlineMedium.fontFamily, 'Georgia');
      expect(MaatramTypography.bodyMedium.fontFamily, 'Roboto');
    });

    test('MaatramTheme.lightTheme initializes with valid Material 3 config', () {
      final theme = MaatramTheme.lightTheme;
      expect(theme.useMaterial3, isTrue);
      expect(theme.scaffoldBackgroundColor, MaatramColors.background);
      expect(theme.colorScheme.primary, MaatramColors.primaryGold);
      expect(theme.colorScheme.secondary, MaatramColors.deepNavy);
      expect(theme.colorScheme.surface, MaatramColors.white);
    });
  });
}
