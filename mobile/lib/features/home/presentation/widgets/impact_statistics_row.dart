import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/models/gamification_summary_model.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/shadows.dart';
import '../../../../core/theme/spacing.dart';

/// Section 4: Four Key Impact Statistics Cards.
/// Displays Total Eligible Hours, Completed Events, This Year's Events, and Current Leaderboard Rank.
class ImpactStatisticsRow extends StatelessWidget {
  final GamificationSummaryModel? summary;
  final bool isLoading;

  const ImpactStatisticsRow({
    super.key,
    this.summary,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    // When loading: show shimmer. When summary is null and not loading (API
    // error or no data): show '—' so unavailability is distinct from genuine
    // zero values returned by the backend.
    final String hours;
    final String events;
    final String thisYear;
    if (isLoading) {
      hours = '—';
      events = '—';
      thisYear = '—';
    } else if (summary != null) {
      hours = summary!.formattedHours;
      events = summary!.completedEventsCount.toString();
      thisYear = summary!.thisYearCount.toString();
    } else {
      hours = '—';
      events = '—';
      thisYear = '—';
    }
    final rank = summary != null ? summary!.rankDisplay : '—';
    final rankLabel = summary != null ? summary!.rankLabel : 'Leaderboard';

    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 360;

        return MaatramFadeSlideIn(
          direction: SlideDirection.fromBottom,
          delay: const Duration(milliseconds: 150),
          child: Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: MaatramSpacing.md,
              vertical: MaatramSpacing.xs,
            ),
            child: Row(
              children: [
                Expanded(
                  child: _StatCard(
                    icon: Icons.calendar_month_rounded,
                    value: hours,
                    label: 'Hours',
                    isCompact: isCompact,
                    isLoading: isLoading,
                  ),
                ),
                SizedBox(width: isCompact ? 6 : 8),
                Expanded(
                  child: _StatCard(
                    icon: Icons.emoji_events_rounded,
                    value: events,
                    label: 'Events',
                    isCompact: isCompact,
                    isLoading: isLoading,
                  ),
                ),
                SizedBox(width: isCompact ? 6 : 8),
                Expanded(
                  child: _StatCard(
                    icon: Icons.trending_up_rounded,
                    value: thisYear,
                    label: 'This Year',
                    isCompact: isCompact,
                    isLoading: isLoading,
                  ),
                ),
                SizedBox(width: isCompact ? 6 : 8),
                Expanded(
                  child: _StatCard(
                    icon: Icons.star_rounded,
                    value: rank,
                    label: rankLabel,
                    isCompact: isCompact,
                    isLoading: isLoading,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final bool isCompact;
  final bool isLoading;

  const _StatCard({
    required this.icon,
    required this.value,
    required this.label,
    required this.isCompact,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isCompact ? 4 : 8,
        vertical: isCompact ? 10 : 12,
      ),
      decoration: BoxDecoration(
        color: MaatramColors.white,
        borderRadius: MaatramRadii.radiusSm,
        border: Border.all(color: MaatramColors.warmBorder),
        boxShadow: MaatramShadows.card,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Gold Rounded Icon Container
          Container(
            padding: EdgeInsets.all(isCompact ? 4 : 6),
            decoration: BoxDecoration(
              color: const Color(0xFFFFF7E0),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              icon,
              size: isCompact ? 15 : 18,
              color: const Color(0xFFD97706),
            ),
          ),
          SizedBox(height: isCompact ? 4 : 6),

          // Numeric Metric
          if (isLoading)
            Container(
              height: isCompact ? 14 : 16,
              width: 24,
              decoration: BoxDecoration(
                color: MaatramColors.stone200,
                borderRadius: BorderRadius.circular(4),
              ),
            )
          else
            FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(
                value,
                style: TextStyle(
                  fontFamily: 'Roboto',
                  fontSize: isCompact ? 14 : 16,
                  fontWeight: FontWeight.w800,
                  color: MaatramColors.deepNavy,
                  letterSpacing: -0.3,
                ),
                maxLines: 1,
              ),
            ),
          const SizedBox(height: 2),

          // Label
          Text(
            label,
            style: TextStyle(
              fontFamily: 'Roboto',
              fontSize: isCompact ? 9.5 : 11,
              color: MaatramColors.secondaryText,
              fontWeight: FontWeight.w500,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
