import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/animations/fade_slide_in.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/badges/category_badge.dart';
import '../../../core/widgets/cards/maatram_card.dart';
import '../../../core/widgets/cards/maatram_stat_card.dart';
import '../../../core/widgets/layout/avatar.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../../../core/widgets/navigation/section_header.dart';
import '../../../app/router/route_names.dart';

/// M1 Home Screen Shell introducing the volunteer visual identity and metric primitives.
class HomePlaceholderScreen extends StatelessWidget {
  const HomePlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          title: Row(
            children: [
              Image.asset(
                'assets/images/logo.png',
                height: 32,
                errorBuilder: (_, __, ___) => const Text(
                  'MAATRAM',
                  style: TextStyle(
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.2,
                    color: MaatramColors.deepNavy,
                  ),
                ),
              ),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.palette_outlined,
                  color: MaatramColors.goldDeep),
              tooltip: 'Developer Showcase',
              onPressed: () => context.push(RouteNames.devShowcasePath),
            ),
            const Padding(
              padding: EdgeInsets.only(right: MaatramSpacing.md),
              child: MaatramAvatar(
                name: 'Sneha Raman',
                size: 36,
              ),
            ),
          ],
        ),
        body: ListView(
          padding: MaatramSpacing.screenPadding,
          children: [
            // Welcome Header
            const MaatramFadeSlideIn(
              direction: SlideDirection.fromTop,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        'Vanakkam, Sneha!',
                        style: MaatramTypography.displayMedium,
                      ),
                      SizedBox(width: MaatramSpacing.sm),
                      MaatramCategoryBadge(
                          category: VolunteerCategory.student, isCompact: true),
                    ],
                  ),
                  SizedBox(height: MaatramSpacing.xxs),
                  Text(
                    'Together transforming lives through education & mentorship.',
                    style: MaatramTypography.bodyMedium,
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.xl),

            // Metrics Row (4 Core Stats)
            MaatramFadeSlideIn(
              delay: const Duration(milliseconds: 100),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: MaatramStatCard(
                          label: 'Events Completed',
                          value: 12,
                          icon: Icons.event_available_outlined,
                          iconColor: MaatramColors.infoDark,
                          iconBackgroundColor: MaatramColors.infoLight,
                        ),
                      ),
                      const SizedBox(width: MaatramSpacing.md),
                      Expanded(
                        child: MaatramStatCard(
                          label: 'Hours Dedicated',
                          value: 36.5,
                          suffix: 'h',
                          icon: Icons.access_time_outlined,
                          iconColor: MaatramColors.categoryAlumni,
                          iconBackgroundColor: MaatramColors.categoryAlumniBg,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: MaatramSpacing.md),
                  Row(
                    children: [
                      Expanded(
                        child: MaatramStatCard(
                          label: 'Points Earned',
                          value: 193,
                          icon: Icons.stars_rounded,
                          iconColor: MaatramColors.goldDark,
                          iconBackgroundColor: MaatramColors.goldSurface,
                        ),
                      ),
                      const SizedBox(width: MaatramSpacing.md),
                      Expanded(
                        child: MaatramStatCard(
                          label: 'State Rank',
                          value: 8,
                          prefix: '#',
                          icon: Icons.emoji_events_outlined,
                          iconColor: MaatramColors.successDark,
                          iconBackgroundColor: MaatramColors.successLight,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.xl),

            // Foundation Banner Card
            MaatramFadeSlideIn(
              delay: const Duration(milliseconds: 200),
              child: MaatramCard(
                onTap: () => context.push(RouteNames.devShowcasePath),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: const BoxDecoration(
                        color: MaatramColors.goldSurface,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.auto_awesome,
                          color: MaatramColors.goldDark),
                    ),
                    const SizedBox(width: MaatramSpacing.md),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Explore M1 Component Library',
                            style: MaatramTypography.titleMedium,
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Inspect buttons, badges, motion tokens & typography',
                            style: MaatramTypography.bodySmall,
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.arrow_forward_ios_rounded,
                        size: 14, color: MaatramColors.charcoal400),
                  ],
                ),
              ),
            ),
            const SizedBox(height: MaatramSpacing.xl),

            // Section Header preview
            const MaatramSectionHeader(
              title: 'Upcoming Volunteering',
              subtitle: 'Published events matching your verified profile',
              actionLabel: 'View All',
            ),
          ],
        ),
      ),
    );
  }
}
