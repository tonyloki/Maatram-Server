import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/badges/category_badge.dart';
import '../../../core/widgets/cards/maatram_card.dart';
import '../../../core/widgets/layout/avatar.dart';
import '../../../core/widgets/layout/organic_background.dart';

/// M1 More Destination Shell providing route access to secondary volunteer flows.
class MorePlaceholderScreen extends StatelessWidget {
  const MorePlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          title: const Text('More Options'),
        ),
        body: ListView(
          padding: MaatramSpacing.screenPadding,
          children: [
            // User Profile Header Card
            MaatramCard(
              padding: MaatramSpacing.cardPadding,
              child: Row(
                children: [
                  const MaatramAvatar(
                    name: 'Sneha Raman',
                    size: 52,
                  ),
                  const SizedBox(width: MaatramSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Sneha Raman',
                          style: MaatramTypography.titleLarge,
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'sneha.r@example.com',
                          style: MaatramTypography.bodySmall,
                        ),
                        const SizedBox(height: MaatramSpacing.xs),
                        const MaatramCategoryBadge(
                            category: VolunteerCategory.student,
                            isCompact: true),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.xl),

            // Navigation Options
            Text('Volunteer Portal',
                style: MaatramTypography.labelLarge
                    .copyWith(color: MaatramColors.charcoal700)),
            const SizedBox(height: MaatramSpacing.sm),
            _buildNavigationTile(
              context,
              icon: Icons.history_edu_outlined,
              title: 'My Volunteering Activity',
              subtitle: 'Attendance logs, check-ins and hours verified',
            ),
            _buildNavigationTile(
              context,
              icon: Icons.military_tech_outlined,
              title: 'Gamification & Badges',
              subtitle: 'Points ledger, tier progression and trophies',
            ),
            _buildNavigationTile(
              context,
              icon: Icons.notifications_none_rounded,
              title: 'Notifications & Alerts',
              subtitle: 'Event reminders and selection updates',
            ),
            _buildNavigationTile(
              context,
              icon: Icons.privacy_tip_outlined,
              title: 'Privacy & Consent Preferences',
              subtitle: 'Leaderboard visibility and media usage controls',
            ),
            const SizedBox(height: MaatramSpacing.xl),

            // Developer Showcase Entry
            Text('Engineering & Quality Tools',
                style: MaatramTypography.labelLarge
                    .copyWith(color: MaatramColors.charcoal700)),
            const SizedBox(height: MaatramSpacing.sm),
            _buildNavigationTile(
              context,
              icon: Icons.palette_outlined,
              title: 'M1 Design Showcase',
              subtitle: 'Inspect design tokens, components, motion and states',
              highlight: true,
              onTap: () => context.push(RouteNames.devShowcasePath),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNavigationTile(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    bool highlight = false,
    VoidCallback? onTap,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: MaatramSpacing.sm),
      child: MaatramCard(
        onTap: onTap ?? () {},
        padding: MaatramSpacing.compactCardPadding,
        borderColor:
            highlight ? MaatramColors.primaryGold : MaatramColors.warmBorder,
        backgroundColor: highlight
            ? MaatramColors.goldLight.withOpacity(0.5)
            : MaatramColors.white,
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: highlight
                    ? MaatramColors.goldSurface
                    : MaatramColors.stone100,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon,
                  size: 20,
                  color: highlight
                      ? MaatramColors.goldDeep
                      : MaatramColors.deepNavy),
            ),
            const SizedBox(width: MaatramSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: MaatramTypography.titleSmall),
                  Text(subtitle,
                      style: MaatramTypography.bodySmall,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis),
                ],
              ),
            ),
            const Icon(Icons.chevron_right_rounded,
                size: 18, color: MaatramColors.charcoal400),
          ],
        ),
      ),
    );
  }
}
