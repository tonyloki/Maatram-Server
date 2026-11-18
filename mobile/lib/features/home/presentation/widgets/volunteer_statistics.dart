import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/models/gamification_summary_model.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/spacing.dart';

/// Section 4: Four Key Volunteer Impact Statistics Cards.
/// Displays Total Eligible Hours, Completed Events, This Year's Events, and Leaderboard Rank.
/// Matches the approved reference design with warm ivory backgrounds and gold icons.
class VolunteerStatistics extends StatelessWidget {
  final GamificationSummaryModel? summary;
  final bool isLoading;

  const VolunteerStatistics({
    super.key,
    this.summary,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
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
              vertical: 6,
            ),
            child: Row(
              children: [
                Expanded(
                  child: _StatCard(
                    icon: Icons.access_time_rounded,
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
        horizontal: isCompact ? 4 : 6,
        vertical: isCompact ? 10 : 12,
      ),
      decoration: BoxDecoration(
        color: const Color(0xFFFEFAF1),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: const Color(0xFFFBE6B3),
          width: 1.0,
        ),
        boxShadow: const [
          BoxShadow(
            color: Color(0x06000000),
            blurRadius: 6,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Gold Icon
          Icon(
            icon,
            size: isCompact ? 17 : 20,
            color: const Color(0xFFD97706),
          ),
          SizedBox(height: isCompact ? 5 : 7),

          // Numeric Metric in Roboto
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
                  fontSize: isCompact ? 15 : 17,
                  fontWeight: FontWeight.w800,
                  color: MaatramColors.deepNavy,
                  letterSpacing: -0.3,
                ),
                maxLines: 1,
              ),
            ),
          const SizedBox(height: 3),

          // Label in Roboto
          Text(
            label,
            style: TextStyle(
              fontFamily: 'Roboto',
              fontSize: isCompact ? 10 : 11,
              fontWeight: FontWeight.w500,
              color: MaatramColors.secondaryText,
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
