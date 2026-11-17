import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/models/achievement_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/feedback/skeleton_loader.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../data/gamification_repository.dart';
import 'achievement_details_modal.dart';

class AchievementsScreen extends ConsumerStatefulWidget {
  const AchievementsScreen({super.key});

  @override
  ConsumerState<AchievementsScreen> createState() => _AchievementsScreenState();
}

class _AchievementsScreenState extends ConsumerState<AchievementsScreen> {
  VolunteerAchievementsModel? _achievements;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAchievements();
  }

  Future<void> _loadAchievements() async {
    final repo = ref.read(gamificationRepositoryProvider);
    final a = await repo.getAchievements();
    if (mounted) {
      setState(() {
        _achievements = a;
        _isLoading = false;
      });
    }
  }

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
            'Achievements',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
        ),
        body: _isLoading
            ? const Padding(
                padding: EdgeInsets.all(MaatramSpacing.md),
                child: Column(
                  children: [
                    MaatramSkeletonBox(
                        width: double.infinity,
                        height: 80,
                        borderRadius: BorderRadius.all(Radius.circular(20))),
                    SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                            child: MaatramSkeletonBox(
                                width: double.infinity,
                                height: 150,
                                borderRadius:
                                    BorderRadius.all(Radius.circular(20)))),
                        SizedBox(width: 12),
                        Expanded(
                            child: MaatramSkeletonBox(
                                width: double.infinity,
                                height: 150,
                                borderRadius:
                                    BorderRadius.all(Radius.circular(20)))),
                      ],
                    ),
                  ],
                ),
              )
            : ListView(
                padding: const EdgeInsets.all(MaatramSpacing.md),
                children: [
                  // Summary Banner
                  Container(
                    padding: const EdgeInsets.all(MaatramSpacing.md),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: MaatramRadii.cardRadius,
                      border: Border.all(color: MaatramColors.warmBorder),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 52,
                          height: 52,
                          decoration: BoxDecoration(
                            color: MaatramColors.primaryGold
                                .withValues(alpha: 0.15),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.military_tech_rounded,
                              color: MaatramColors.deepNavy, size: 28),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '${_achievements?.totalEarned ?? 0} of ${_achievements?.totalAvailable ?? 0} Badges',
                                style: MaatramTypography.titleMedium.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: MaatramColors.deepNavy,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Earn badges by hitting volunteering milestones',
                                style: MaatramTypography.bodySmall.copyWith(
                                  color: MaatramColors.secondaryText,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: MaatramSpacing.md),

                  // Badge Grid
                  if (_achievements != null && _achievements!.items.isNotEmpty)
                    GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      gridDelegate:
                          const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                        childAspectRatio: 0.85,
                      ),
                      itemCount: _achievements!.items.length,
                      itemBuilder: (context, index) {
                        final badge = _achievements!.items[index];
                        return _buildBadgeCard(context, badge);
                      },
                    )
                  else
                    // Fallback list of canonical badges
                    GridView.count(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 0.85,
                      children: [
                        _buildStaticBadgeCard(context, 'First Step',
                            'Attended first event', true, Icons.stars_rounded),
                        _buildStaticBadgeCard(context, '10 Hours',
                            'Dedicated 10 hours', true, Icons.schedule_rounded),
                        _buildStaticBadgeCard(
                            context,
                            'Community Hero',
                            '5 community events',
                            false,
                            Icons.volunteer_activism_rounded),
                        _buildStaticBadgeCard(context, 'Centurion',
                            '100 volunteer hours', false, Icons.shield_rounded),
                      ],
                    ),
                  const SizedBox(height: MaatramSpacing.lg),
                ],
              ),
      ),
    );
  }

  Widget _buildBadgeCard(BuildContext context, AchievementModel badge) {
    final isEarned = badge.isEarned;
    return InkWell(
      onTap: () => showModalBottomSheet(
        context: context,
        backgroundColor: Colors.transparent,
        builder: (_) => AchievementDetailsModal(achievement: badge),
      ),
      borderRadius: BorderRadius.circular(24),
      child: Container(
        padding: const EdgeInsets.all(MaatramSpacing.md),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: MaatramRadii.cardRadius,
          border: Border.all(
            color: isEarned
                ? MaatramColors.primaryGold.withValues(alpha: 0.5)
                : MaatramColors.warmBorder,
            width: isEarned ? 1.5 : 1.0,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 54,
              height: 54,
              decoration: BoxDecoration(
                color: isEarned
                    ? const Color(0xFFFEF3C7)
                    : const Color(0xFFF3F4F6),
                shape: BoxShape.circle,
              ),
              child: Icon(
                isEarned
                    ? Icons.military_tech_rounded
                    : Icons.lock_outline_rounded,
                color: isEarned
                    ? const Color(0xFFB45309)
                    : MaatramColors.secondaryText,
                size: 28,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              badge.title,
              style: MaatramTypography.titleSmall.copyWith(
                fontWeight: FontWeight.bold,
                color: MaatramColors.deepNavy,
              ),
              textAlign: TextAlign.center,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            Text(
              badge.description,
              style: MaatramTypography.bodySmall.copyWith(
                fontSize: 11,
                color: MaatramColors.secondaryText,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: isEarned
                    ? const Color(0xFFECFDF5)
                    : const Color(0xFFF3F4F6),
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(
                isEarned ? 'Unlocked' : 'Locked',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: isEarned
                      ? MaatramColors.success
                      : MaatramColors.secondaryText,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStaticBadgeCard(BuildContext context, String title, String desc,
      bool isEarned, IconData icon) {
    return InkWell(
      onTap: () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$title: $desc')),
        );
      },
      borderRadius: BorderRadius.circular(24),
      child: Container(
        padding: const EdgeInsets.all(MaatramSpacing.md),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: MaatramRadii.cardRadius,
          border: Border.all(
            color: isEarned
                ? MaatramColors.primaryGold.withValues(alpha: 0.5)
                : MaatramColors.warmBorder,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 54,
              height: 54,
              decoration: BoxDecoration(
                color: isEarned
                    ? const Color(0xFFFEF3C7)
                    : const Color(0xFFF3F4F6),
                shape: BoxShape.circle,
              ),
              child: Icon(
                isEarned ? icon : Icons.lock_outline_rounded,
                color: isEarned
                    ? const Color(0xFFB45309)
                    : MaatramColors.secondaryText,
                size: 28,
              ),
            ),
            const SizedBox(height: 10),
            Text(title,
                style: MaatramTypography.titleSmall.copyWith(
                    fontWeight: FontWeight.bold,
                    color: MaatramColors.deepNavy)),
            const SizedBox(height: 4),
            Text(desc,
                style: const TextStyle(
                    fontSize: 11, color: MaatramColors.secondaryText),
                textAlign: TextAlign.center),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: isEarned
                    ? const Color(0xFFECFDF5)
                    : const Color(0xFFF3F4F6),
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(
                isEarned ? 'Unlocked' : 'Locked',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: isEarned
                      ? MaatramColors.success
                      : MaatramColors.secondaryText,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
