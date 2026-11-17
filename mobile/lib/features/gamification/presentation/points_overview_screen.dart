import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/models/gamification_summary_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/feedback/skeleton_loader.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../data/gamification_repository.dart';

class PointsOverviewScreen extends ConsumerStatefulWidget {
  const PointsOverviewScreen({super.key});

  @override
  ConsumerState<PointsOverviewScreen> createState() =>
      _PointsOverviewScreenState();
}

class _PointsOverviewScreenState extends ConsumerState<PointsOverviewScreen> {
  GamificationSummaryModel? _summary;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSummary();
  }

  Future<void> _loadSummary() async {
    final repo = ref.read(gamificationRepositoryProvider);
    final s = await repo.getSummary();
    if (mounted) {
      setState(() {
        _summary = s;
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
            'Points & Karma',
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
                        height: 180,
                        borderRadius: BorderRadius.all(Radius.circular(24))),
                    SizedBox(height: 16),
                    MaatramSkeletonBox(
                        width: double.infinity,
                        height: 140,
                        borderRadius: BorderRadius.all(Radius.circular(24))),
                  ],
                ),
              )
            : ListView(
                padding: const EdgeInsets.all(MaatramSpacing.md),
                children: [
                  // Hero Points Card
                  Container(
                    padding: const EdgeInsets.all(MaatramSpacing.lg),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFFFFFBEB), Color(0xFFFEF3C7)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(
                          color:
                              MaatramColors.primaryGold.withValues(alpha: 0.3)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: MaatramColors.primaryGold,
                                borderRadius: BorderRadius.circular(999),
                              ),
                              child: Text(
                                _summary?.rankLabel ?? 'Karma Tier',
                                style: MaatramTypography.labelSmall.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: MaatramColors.deepNavy,
                                ),
                              ),
                            ),
                            Text(
                              _summary?.rankDisplay ?? '—',
                              style: MaatramTypography.titleSmall.copyWith(
                                fontWeight: FontWeight.bold,
                                color: MaatramColors.deepNavy,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 14),
                        Text(
                          _summary?.formattedPoints ?? '0',
                          style: const TextStyle(
                            fontFamily: 'Georgia',
                            fontSize: 44,
                            fontWeight: FontWeight.bold,
                            color: MaatramColors.deepNavy,
                            height: 1.1,
                          ),
                        ),
                        Text(
                          'Total Karma Points Earned',
                          style: MaatramTypography.bodyMedium.copyWith(
                            color: MaatramColors.secondaryText,
                          ),
                        ),
                        const SizedBox(height: 16),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(999),
                          child: const LinearProgressIndicator(
                            value: 0.75,
                            backgroundColor: Color(0xFFFDE68A),
                            valueColor: AlwaysStoppedAnimation<Color>(
                                Color(0xFFD97706)),
                            minHeight: 8,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Keep volunteering to reach the next milestone badge!',
                          style: MaatramTypography.labelSmall
                              .copyWith(color: MaatramColors.secondaryText),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: MaatramSpacing.md),

                  // Official Formula Breakdown Card
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
                          'Points Formula & Breakdown',
                          style: MaatramTypography.titleSmall.copyWith(
                            fontWeight: FontWeight.bold,
                            color: MaatramColors.deepNavy,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Points = (Events × 10) + (Hours × 2)',
                          style: MaatramTypography.labelSmall.copyWith(
                            fontFamily: 'monospace',
                            color: MaatramColors.secondaryText,
                          ),
                        ),
                        const SizedBox(height: 16),
                        _buildBreakdownRow(
                          icon: Icons.event_available_rounded,
                          label: 'Events Completed',
                          countText:
                              '${_summary?.completedEventsCount ?? 0} events',
                          pointsText:
                              '+${(_summary?.completedEventsCount ?? 0) * 10} pts',
                          color: MaatramColors.categoryStudent,
                        ),
                        const Divider(
                            height: 20, color: MaatramColors.warmBorder),
                        _buildBreakdownRow(
                          icon: Icons.timer_outlined,
                          label: 'Volunteering Hours',
                          countText: '${_summary?.formattedHours ?? "0"} hrs',
                          pointsText:
                              '+${((_summary?.totalHours ?? 0) * 2).toInt()} pts',
                          color: MaatramColors.primaryGold,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: MaatramSpacing.md),

                  // Navigation Card to Achievements & History
                  Container(
                    padding: const EdgeInsets.all(MaatramSpacing.md),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: MaatramRadii.cardRadius,
                      border: Border.all(color: MaatramColors.warmBorder),
                    ),
                    child: Column(
                      children: [
                        InkWell(
                          onTap: () =>
                              context.push(RouteNames.pointsHistoryPath),
                          child: Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    color: MaatramColors.primaryGold
                                        .withValues(alpha: 0.15),
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  child: const Icon(Icons.history_edu_rounded,
                                      color: MaatramColors.deepNavy),
                                ),
                                const SizedBox(width: 12),
                                const Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text('Transaction History (Ledger)',
                                          style: TextStyle(
                                              fontWeight: FontWeight.bold,
                                              fontSize: 14)),
                                      Text(
                                          'View full audit log of earned karma points',
                                          style: TextStyle(
                                              fontSize: 12,
                                              color:
                                                  MaatramColors.secondaryText)),
                                    ],
                                  ),
                                ),
                                const Icon(Icons.chevron_right_rounded,
                                    color: MaatramColors.secondaryText),
                              ],
                            ),
                          ),
                        ),
                        const Divider(
                            height: 16, color: MaatramColors.warmBorder),
                        InkWell(
                          onTap: () =>
                              context.push(RouteNames.achievementsPath),
                          child: Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4),
                            child: Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    color: MaatramColors.categoryAlumni
                                        .withValues(alpha: 0.15),
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  child: const Icon(
                                      Icons.military_tech_outlined,
                                      color: MaatramColors.categoryAlumni),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      const Text('Achievements & Badges',
                                          style: TextStyle(
                                              fontWeight: FontWeight.bold,
                                              fontSize: 14)),
                                      Text(
                                          '${_summary?.badgesEarnedCount ?? 0} Badges Unlocked',
                                          style: const TextStyle(
                                              fontSize: 12,
                                              color:
                                                  MaatramColors.secondaryText)),
                                    ],
                                  ),
                                ),
                                const Icon(Icons.chevron_right_rounded,
                                    color: MaatramColors.secondaryText),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: MaatramSpacing.lg),

                  MaatramButton(
                    label: 'View Point Ledger',
                    onPressed: () => context.push(RouteNames.pointsHistoryPath),
                  ),
                  const SizedBox(height: MaatramSpacing.md),
                ],
              ),
      ),
    );
  }

  Widget _buildBreakdownRow({
    required IconData icon,
    required String label,
    required String countText,
    required String pointsText,
    required Color color,
  }) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.15),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 20),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label,
                  style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                      color: MaatramColors.deepNavy)),
              Text(countText,
                  style: const TextStyle(
                      fontSize: 12, color: MaatramColors.secondaryText)),
            ],
          ),
        ),
        Text(
          pointsText,
          style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 15,
              color: MaatramColors.deepNavy),
        ),
      ],
    );
  }
}
