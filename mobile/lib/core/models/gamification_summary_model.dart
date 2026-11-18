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

  static double _parseDouble(dynamic value, [double defaultValue = 0.0]) {
    if (value == null) return defaultValue;
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? defaultValue;
    return defaultValue;
  }

  static int _parseInt(dynamic value, [int defaultValue = 0]) {
    if (value == null) return defaultValue;
    if (value is num) return value.toInt();
    if (value is String) {
      return int.tryParse(value) ??
          (double.tryParse(value)?.toInt() ?? defaultValue);
    }
    return defaultValue;
  }

  static int? _parseNullableInt(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toInt();
    if (value is String) {
      return int.tryParse(value) ?? double.tryParse(value)?.toInt();
    }
    return null;
  }

  factory GamificationSummaryModel.fromJson(Map<String, dynamic> json) {
    return GamificationSummaryModel(
      volunteerProfileId: json['volunteer_profile_id']?.toString() ?? '',
      cycleYear: _parseInt(json['cycle_year'], DateTime.now().year),
      totalPoints: _parseDouble(json['total_points'], 0.0),
      totalHours: _parseDouble(json['total_hours'], 0.0),
      completedEventsCount: _parseInt(json['completed_events_count'], 0),
      badgesEarnedCount: _parseInt(json['badges_earned_count'], 0),
      rank: _parseNullableInt(json['rank']),
      eventsThisYear: _parseNullableInt(json['events_this_year']),
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
