import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/models/point_ledger_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/feedback/empty_state.dart';
import '../../../core/widgets/feedback/skeleton_loader.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../data/gamification_repository.dart';

class PointsHistoryScreen extends ConsumerStatefulWidget {
  const PointsHistoryScreen({super.key});

  @override
  ConsumerState<PointsHistoryScreen> createState() =>
      _PointsHistoryScreenState();
}

class _PointsHistoryScreenState extends ConsumerState<PointsHistoryScreen> {
  PointLedgerModel? _ledger;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadLedger();
  }

  Future<void> _loadLedger() async {
    final repo = ref.read(gamificationRepositoryProvider);
    final l = await repo.getLedger();
    if (mounted) {
      setState(() {
        _ledger = l;
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
            'Points Ledger',
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
                        height: 70,
                        borderRadius: BorderRadius.all(Radius.circular(16))),
                    SizedBox(height: 12),
                    MaatramSkeletonBox(
                        width: double.infinity,
                        height: 70,
                        borderRadius: BorderRadius.all(Radius.circular(16))),
                    SizedBox(height: 12),
                    MaatramSkeletonBox(
                        width: double.infinity,
                        height: 70,
                        borderRadius: BorderRadius.all(Radius.circular(16))),
                  ],
                ),
              )
            : _ledger == null || _ledger!.items.isEmpty
                ? const Center(
                    child: MaatramEmptyState(
                      title: 'No Transactions Yet',
                      description:
                          'Points will appear here after participating in events and logging verified hours.',
                      icon: Icons.history_toggle_off_rounded,
                    ),
                  )
                : ListView.separated(
                    padding: const EdgeInsets.all(MaatramSpacing.md),
                    itemCount: _ledger!.items.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 10),
                    itemBuilder: (context, index) {
                      final item = _ledger!.items[index];
                      return Container(
                        padding: const EdgeInsets.all(MaatramSpacing.md),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: MaatramRadii.cardRadius,
                          border: Border.all(color: MaatramColors.warmBorder),
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 44,
                              height: 44,
                              decoration: BoxDecoration(
                                color: MaatramColors.primaryGold
                                    .withValues(alpha: 0.15),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.stars_rounded,
                                  color: MaatramColors.deepNavy, size: 24),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    item.displayTitle,
                                    style:
                                        MaatramTypography.titleSmall.copyWith(
                                      fontWeight: FontWeight.bold,
                                      color: MaatramColors.deepNavy,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    item.formattedDate,
                                    style: MaatramTypography.bodySmall.copyWith(
                                      color: MaatramColors.secondaryText,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFFFEF3C7),
                                borderRadius: BorderRadius.circular(999),
                              ),
                              child: Text(
                                item.pointsDisplay,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 13,
                                  color: Color(0xFFB45309),
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
      ),
    );
  }
}
