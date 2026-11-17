import 'package:meta/meta.dart';

/// Models the backend `GamificationSummaryResponse` from `GET /api/v1/gamification/summary`.
@immutable
class GamificationSummaryModel {
  final String volunteerProfileId;
  final int cycleYear;
  final double totalPoints;
  final double totalHours;
  final int completedEventsCount;
  final int badgesEarnedCount;
  final int? rank;
  final int? eventsThisYear;

  const GamificationSummaryModel({
    required this.volunteerProfileId,
    required this.cycleYear,
    required this.totalPoints,
    required this.totalHours,
    required this.completedEventsCount,
    required this.badgesEarnedCount,
    this.rank,
    this.eventsThisYear,
  });

  int get thisYearCount => eventsThisYear ?? completedEventsCount;

  /// Format points cleanly (e.g. "180" or "180.5")
  String get formattedPoints {
    if (totalPoints % 1 == 0) {
      return totalPoints.toInt().toString();
    }
    return totalPoints.toStringAsFixed(1);
  }

  /// Format hours cleanly (e.g. "24" or "24.5")
  String get formattedHours {
    if (totalHours % 1 == 0) {
      return totalHours.toInt().toString();
    }
    return totalHours.toStringAsFixed(1);
  }

  /// Leaderboard rank representation (e.g. "#1" or "—")
  String get rankDisplay {
    if (rank != null && rank! > 0) {
      return '#$rank';
    }
    return '—';
  }

  String get rankLabel {
    if (rank != null && rank! <= 3 && rank! > 0) {
      return 'Top Volunteer';
    }
    return 'Leaderboard';
  }

  factory GamificationSummaryModel.fromJson(Map<String, dynamic> json) {
    return GamificationSummaryModel(
      volunteerProfileId: json['volunteer_profile_id']?.toString() ?? '',
      cycleYear: (json['cycle_year'] as num?)?.toInt() ?? DateTime.now().year,
      totalPoints: (json['total_points'] as num?)?.toDouble() ?? 0.0,
      totalHours: (json['total_hours'] as num?)?.toDouble() ?? 0.0,
      completedEventsCount:
          (json['completed_events_count'] as num?)?.toInt() ?? 0,
      badgesEarnedCount: (json['badges_earned_count'] as num?)?.toInt() ?? 0,
      rank: (json['rank'] as num?)?.toInt(),
    );
  }

  factory GamificationSummaryModel.empty() {
    return GamificationSummaryModel(
      volunteerProfileId: '',
      cycleYear: DateTime.now().year,
      totalPoints: 0.0,
      totalHours: 0.0,
      completedEventsCount: 0,
      badgesEarnedCount: 0,
      rank: null,
    );
  }
}
