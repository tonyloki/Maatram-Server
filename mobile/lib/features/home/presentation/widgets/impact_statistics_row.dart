export 'volunteer_statistics.dart';

import 'package:flutter/material.dart';
import '../../../../core/models/gamification_summary_model.dart';
import 'volunteer_statistics.dart';

/// Backward-compatible alias for VolunteerStatistics
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
    return VolunteerStatistics(
      summary: summary,
      isLoading: isLoading,
    );
  }
}
