import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/layout/organic_background.dart';

class AboutMaatramScreen extends StatelessWidget {
  const AboutMaatramScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_rounded,
                color: MaatramColors.deepNavy),
            onPressed: () => context.pop(),
          ),
          title: Text(
            'About Maatram',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
        ),
        body: ListView(
          padding: const EdgeInsets.all(MaatramSpacing.md),
          children: [
            // Hero Brand Card
            Container(
              padding: const EdgeInsets.all(MaatramSpacing.xl),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
              ),
              child: Column(
                children: [
                  Image.asset(
                    'assets/images/logo.png',
                    height: 56,
                    errorBuilder: (_, __, ___) => const Icon(
                        Icons.wb_sunny_rounded,
                        size: 56,
                        color: MaatramColors.primaryGold),
                  ),
                  const SizedBox(height: 14),
                  Text(
                    'Maatram Foundation',
                    style: MaatramTypography.headlineSmall.copyWith(
                      fontFamily: 'Georgia',
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Volunteer Portal • Better Tomorrow',
                    style: MaatramTypography.labelSmall.copyWith(
                      color: MaatramColors.primaryGold,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.md),

            // Mission Card
            Container(
              padding: const EdgeInsets.all(MaatramSpacing.md),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Our Mission',
                    style: MaatramTypography.titleSmall.copyWith(
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Maatram Foundation provides free higher education opportunities to deserving underprivileged students. Through our committed volunteer ecosystem, we connect students with passionate mentors, alumni, and industry leaders to guide them toward fulfilling careers.',
                    style: MaatramTypography.bodyMedium.copyWith(
                      color: MaatramColors.deepNavy,
                      height: 1.5,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.md),

            // Impact Highlights
            Container(
              padding: const EdgeInsets.all(MaatramSpacing.md),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Our Impact',
                    style: MaatramTypography.titleSmall.copyWith(
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                  const SizedBox(height: 14),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      Expanded(
                          child: _buildStat('3,500+', 'Students',
                              MaatramColors.categoryStudent)),
                      Container(
                          width: 1,
                          height: 36,
                          color: MaatramColors.warmBorder),
                      Expanded(
                          child: _buildStat('1,200+', 'Volunteers',
                              MaatramColors.categoryAlumni)),
                      Container(
                          width: 1,
                          height: 36,
                          color: MaatramColors.warmBorder),
                      Expanded(
                          child: _buildStat(
                              '50,000+', 'Hours', MaatramColors.primaryGold)),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.lg),

            Center(
              child: Text(
                '© 2026 Maatram Foundation. All rights reserved.',
                style: MaatramTypography.labelSmall
                    .copyWith(color: MaatramColors.secondaryText),
              ),
            ),
            const SizedBox(height: MaatramSpacing.md),
          ],
        ),
      ),
    );
  }

  Widget _buildStat(String value, String label, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontFamily: 'Georgia',
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(
            fontFamily: 'Roboto',
            fontSize: 12,
            color: MaatramColors.secondaryText,
          ),
        ),
      ],
    );
  }
}
