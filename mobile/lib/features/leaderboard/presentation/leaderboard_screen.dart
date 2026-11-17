import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/animations/fade_slide_in.dart';
import '../../../core/models/leaderboard_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/shadows.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/layout/avatar.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../state/leaderboard_controller.dart';

/// Complete, production-grade Leaderboard Screen faithful to Master Screen 18.
/// Features Category Segmented Pills (Overall, Students, Alumni),
/// Responsive 3-Column Top Podium (#2, #1, #3) with Golden Trophy,
/// Ranked volunteer list, and adaptive layout that fits 320dp width with zero overflow.
class LeaderboardScreen extends ConsumerWidget {
  const LeaderboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(leaderboardControllerProvider);
    final displayItems = state.items;

    // Partition into Top 3 and remaining
    LeaderboardItemModel? rank1;
    LeaderboardItemModel? rank2;
    LeaderboardItemModel? rank3;
    final remainingItems = <LeaderboardItemModel>[];

    for (final item in displayItems) {
      if (item.rank == 1) {
        rank1 = item;
      } else if (item.rank == 2) {
        rank2 = item;
      } else if (item.rank == 3) {
        rank3 = item;
      } else {
        remainingItems.add(item);
      }
    }

    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          bottom: false,
          child: RefreshIndicator(
            color: MaatramColors.primaryGold,
            backgroundColor: Colors.white,
            onRefresh: () async {
              await ref.read(leaderboardControllerProvider.notifier).refresh();
            },
            child: ListView(
              physics: const AlwaysScrollableScrollPhysics(
                parent: BouncingScrollPhysics(),
              ),
              padding: const EdgeInsets.only(bottom: 32),
              children: [
                // 1. Header: "Leaderboard"
                Padding(
                  padding: const EdgeInsets.fromLTRB(
                    MaatramSpacing.md,
                    MaatramSpacing.md,
                    MaatramSpacing.md,
                    MaatramSpacing.xs,
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Leaderboard',
                        style: MaatramTypography.headlineLarge.copyWith(
                          fontFamily: 'Georgia',
                          fontSize: 26,
                          fontWeight: FontWeight.bold,
                          color: MaatramColors.deepNavy,
                        ),
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'Recognizing dedication and community service.',
                        style: TextStyle(
                          fontFamily: 'Roboto',
                          fontSize: 13,
                          color: MaatramColors.secondaryText,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: MaatramSpacing.sm),

                // 2. Segmented Category Filter Pills: "Overall" | "Students" | "Alumni"
                Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: MaatramSpacing.md),
                  child: Row(
                    children: [
                      _CategoryTabPill(
                        label: 'Overall',
                        isSelected: state.selectedCategory == 'OVERALL',
                        onTap: () => ref
                            .read(leaderboardControllerProvider.notifier)
                            .changeCategory('OVERALL'),
                      ),
                      const SizedBox(width: 8),
                      _CategoryTabPill(
                        label: 'Students',
                        isSelected: state.selectedCategory == 'STUDENTS',
                        onTap: () => ref
                            .read(leaderboardControllerProvider.notifier)
                            .changeCategory('STUDENTS'),
                      ),
                      const SizedBox(width: 8),
                      _CategoryTabPill(
                        label: 'Alumni',
                        isSelected: state.selectedCategory == 'ALUMNI',
                        onTap: () => ref
                            .read(leaderboardControllerProvider.notifier)
                            .changeCategory('ALUMNI'),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: MaatramSpacing.md),

                if (state.isLoading)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.all(48.0),
                      child: CircularProgressIndicator(color: MaatramColors.primaryGold),
                    ),
                  )
                else if (displayItems.isEmpty)
                  Padding(
                    padding: const EdgeInsets.all(MaatramSpacing.md),
                    child: Container(
                      padding: const EdgeInsets.all(MaatramSpacing.xl),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: MaatramRadii.cardRadius,
                        border: Border.all(color: MaatramColors.warmBorder),
                        boxShadow: MaatramShadows.card,
                      ),
                      child: const Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.leaderboard_outlined,
                            size: 48,
                            color: MaatramColors.charcoal400,
                          ),
                          SizedBox(height: 12),
                          Text(
                            'No Leaderboard Data Yet',
                            style: TextStyle(
                              fontFamily: 'Georgia',
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: MaatramColors.deepNavy,
                            ),
                          ),
                          SizedBox(height: 6),
                          Text(
                            'Leaderboard rankings will appear as volunteers participate in events.',
                            style: TextStyle(
                              fontSize: 13,
                              color: Color(0xFF6B655B),
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  )
                else ...[
                  // 3. Top 3 Golden Podium: #2 (left), #1 (center, elevated), #3 (right)
                  if (rank1 != null)
                    Padding(
                      padding: const EdgeInsets.symmetric(
                          horizontal: MaatramSpacing.md),
                      child: _PodiumContainer(
                        first: rank1,
                        second: rank2,
                        third: rank3,
                      ),
                    ),

                  const SizedBox(height: MaatramSpacing.lg),

                  // 4. Ranked List of Remaining Volunteers
                  if (remainingItems.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(
                          horizontal: MaatramSpacing.md),
                      child: Container(
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: MaatramRadii.cardRadius,
                          border: Border.all(color: MaatramColors.warmBorder),
                          boxShadow: MaatramShadows.card,
                        ),
                        child: Column(
                          children: [
                            for (int i = 0; i < remainingItems.length; i++) ...[
                              _LeaderboardRowItem(item: remainingItems[i]),
                              if (i < remainingItems.length - 1)
                                const Divider(
                                    height: 1,
                                    color: Color(0xFFF3F4F6),
                                    indent: 56,
                                    endIndent: 16),
                            ],
                          ],
                        ),
                      ),
                    ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Category Pill Tab Widget
class _CategoryTabPill extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _CategoryTabPill({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? MaatramColors.primaryGold : Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: isSelected
                  ? MaatramColors.primaryGold
                  : const Color(0xFFE5E7EB),
            ),
            boxShadow: isSelected
                ? [
                    const BoxShadow(
                        color: Color(0x18F5B817),
                        blurRadius: 4,
                        offset: Offset(0, 2))
                  ]
                : null,
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              fontFamily: 'Roboto',
              fontSize: 12,
              fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
              color: isSelected
                  ? MaatramColors.deepNavy
                  : MaatramColors.charcoal700,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ),
    );
  }
}

/// Responsive Top 3 Podium Container
class _PodiumContainer extends StatelessWidget {
  final LeaderboardItemModel first;
  final LeaderboardItemModel? second;
  final LeaderboardItemModel? third;

  const _PodiumContainer({
    required this.first,
    this.second,
    this.third,
  });

  @override
  Widget build(BuildContext context) {
    return MaatramFadeSlideIn(
      direction: SlideDirection.fromBottom,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: MaatramRadii.cardRadius,
          border: Border.all(color: MaatramColors.warmBorder),
          boxShadow: MaatramShadows.card,
        ),
        padding: const EdgeInsets.fromLTRB(8, 16, 8, 16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            // #2 Second Place (Left)
            Expanded(
              child: second != null
                  ? _PodiumColumn(
                      item: second!,
                      rankText: '#2',
                      rankColor: const Color(0xFF6B7280),
                      avatarBorderColor: const Color(0xFF9CA3AF),
                      avatarSize: 46,
                      isFirst: false,
                    )
                  : const SizedBox.shrink(),
            ),

            // #1 First Place (Center, Elevated with Golden Crown)
            Expanded(
              child: _PodiumColumn(
                item: first,
                rankText: '#1',
                rankColor: const Color(0xFFD97706),
                avatarBorderColor: MaatramColors.primaryGold,
                avatarSize: 58,
                isFirst: true,
              ),
            ),

            // #3 Third Place (Right)
            Expanded(
              child: third != null
                  ? _PodiumColumn(
                      item: third!,
                      rankText: '#3',
                      rankColor: const Color(0xFFB45309),
                      avatarBorderColor: const Color(0xFFD97706),
                      avatarSize: 46,
                      isFirst: false,
                    )
                  : const SizedBox.shrink(),
            ),
          ],
        ),
      ),
    );
  }
}

/// Single Podium Column with adaptive widths
class _PodiumColumn extends StatelessWidget {
  final LeaderboardItemModel item;
  final String rankText;
  final Color rankColor;
  final Color avatarBorderColor;
  final double avatarSize;
  final bool isFirst;

  const _PodiumColumn({
    required this.item,
    required this.rankText,
    required this.rankColor,
    required this.avatarBorderColor,
    required this.avatarSize,
    required this.isFirst,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Trophy / Crown Icon for #1
        if (isFirst)
          const Padding(
            padding: EdgeInsets.only(bottom: 2),
            child: Icon(Icons.emoji_events_rounded,
                color: Color(0xFFF59E0B), size: 24),
          ),

        // Avatar
        Container(
          padding: const EdgeInsets.all(2.5),
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(
                color: avatarBorderColor, width: isFirst ? 2.5 : 2.0),
          ),
          child: MaatramAvatar(
            name: item.volunteerName,
            imageUrl: item.avatarUrl,
            size: avatarSize,
          ),
        ),
        const SizedBox(height: 6),

        // Rank Badge
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 1.5),
          decoration: BoxDecoration(
            color: isFirst ? const Color(0xFFFEF3C7) : const Color(0xFFF3F4F6),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            rankText,
            style: TextStyle(
              fontFamily: 'Roboto',
              fontSize: 10.5,
              fontWeight: FontWeight.bold,
              color: rankColor,
            ),
          ),
        ),
        const SizedBox(height: 4),

        // Volunteer Name
        Text(
          item.volunteerName,
          style: TextStyle(
            fontFamily: 'Roboto',
            fontSize: isFirst ? 13 : 11.5,
            fontWeight: FontWeight.bold,
            color: MaatramColors.deepNavy,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 2),

        // Points
        Text(
          '${item.points} pts',
          style: TextStyle(
            fontFamily: 'Roboto',
            fontSize: isFirst ? 12 : 11,
            fontWeight: FontWeight.w700,
            color:
                isFirst ? const Color(0xFFD97706) : MaatramColors.charcoal600,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}

/// Single Ranked Row in the lower leaderboard list
class _LeaderboardRowItem extends StatelessWidget {
  final LeaderboardItemModel item;

  const _LeaderboardRowItem({required this.item});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 11),
      child: Row(
        children: [
          // Rank number
          SizedBox(
            width: 24,
            child: Text(
              '${item.rank}',
              style: const TextStyle(
                fontFamily: 'Roboto',
                fontSize: 13,
                fontWeight: FontWeight.w700,
                color: MaatramColors.charcoal600,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(width: 10),

          // Avatar
          MaatramAvatar(
            name: item.volunteerName,
            imageUrl: item.avatarUrl,
            size: 34,
          ),
          const SizedBox(width: 12),

          // Volunteer Name and category
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.volunteerName,
                  style: const TextStyle(
                    fontFamily: 'Roboto',
                    fontSize: 13.5,
                    fontWeight: FontWeight.w600,
                    color: MaatramColors.deepNavy,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 1),
                Text(
                  item.category.toLowerCase() == 'student'
                      ? 'Student'
                      : (item.category.toLowerCase() == 'alumni'
                          ? 'Alumni'
                          : 'Panelist'),
                  style: const TextStyle(
                    fontFamily: 'Roboto',
                    fontSize: 11,
                    color: MaatramColors.secondaryText,
                  ),
                ),
              ],
            ),
          ),

          // Points
          Text(
            '${item.points} pts',
            style: const TextStyle(
              fontFamily: 'Roboto',
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: Color(0xFFD97706),
            ),
          ),
        ],
      ),
    );
  }
}
