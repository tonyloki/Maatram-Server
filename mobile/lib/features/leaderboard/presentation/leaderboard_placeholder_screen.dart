import 'package:flutter/material.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/badges/category_badge.dart';
import '../../../core/widgets/cards/maatram_card.dart';
import '../../../core/widgets/layout/avatar.dart';
import '../../../core/widgets/layout/organic_background.dart';

/// M1 Leaderboard Destination Shell demonstrating podium ranks and volunteer list primitives.
class LeaderboardPlaceholderScreen extends StatelessWidget {
  const LeaderboardPlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          title: const Text('Volunteer Leaderboard'),
        ),
        body: ListView(
          padding: MaatramSpacing.screenPadding,
          children: [
            // Podiums Card
            MaatramCard(
              padding: MaatramSpacing.cardPadding,
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.emoji_events_rounded, color: MaatramColors.goldDark, size: 28),
                      const SizedBox(width: MaatramSpacing.sm),
                      Text(
                        'Top Community Leaders',
                        style: MaatramTypography.headlineMedium.copyWith(fontSize: 18),
                      ),
                    ],
                  ),
                  const SizedBox(height: MaatramSpacing.lg),
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _PodiumItem(rank: 2, name: 'Ananya S', points: 340, color: MaatramColors.charcoal600),
                      _PodiumItem(rank: 1, name: 'Karthik R', points: 410, color: MaatramColors.primaryGold, isFirst: true),
                      _PodiumItem(rank: 3, name: 'Deepak M', points: 295, color: MaatramColors.goldDark),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.xl),

            // Roster list item
            Text('Your Current Standing', style: MaatramTypography.headlineMedium.copyWith(fontSize: 18)),
            const SizedBox(height: MaatramSpacing.sm),
            MaatramCard(
              padding: MaatramSpacing.compactCardPadding,
              child: Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: MaatramColors.goldSurface,
                      shape: BoxShape.circle,
                    ),
                    alignment: Alignment.center,
                    child: const Text('#8', style: TextStyle(fontWeight: FontWeight.w800, color: MaatramColors.goldDeep)),
                  ),
                  const SizedBox(width: MaatramSpacing.md),
                  const MaatramAvatar(name: 'Sneha Raman', size: 36),
                  const SizedBox(width: MaatramSpacing.md),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Sneha Raman (You)', style: MaatramTypography.titleSmall),
                        Text('12 events completed', style: MaatramTypography.bodySmall),
                      ],
                    ),
                  ),
                  const MaatramCategoryBadge(category: VolunteerCategory.student, isCompact: true),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PodiumItem extends StatelessWidget {
  final int rank;
  final String name;
  final int points;
  final Color color;
  final bool isFirst;

  const _PodiumItem({
    required this.rank,
    required this.name,
    required this.points,
    required this.color,
    this.isFirst = false,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        MaatramAvatar(
          name: name,
          size: isFirst ? 54 : 44,
          borderColor: color,
        ),
        const SizedBox(height: 6),
        Text(name, style: MaatramTypography.titleSmall),
        Text('$points pts', style: MaatramTypography.labelSmall.copyWith(color: MaatramColors.goldDark)),
      ],
    );
  }
}

