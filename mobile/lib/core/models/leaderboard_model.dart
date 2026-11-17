import 'package:meta/meta.dart';

/// Models a single entry in the Leaderboard rankings.
@immutable
class LeaderboardItemModel {
  final int rank;
  final String? volunteerProfileId;
  final String volunteerName;
  final String category;
  final int points;
  final int eventsAttended;
  final double totalHours;
  final bool isAnonymous;
  final String? avatarUrl;

  const LeaderboardItemModel({
    required this.rank,
    this.volunteerProfileId,
    required this.volunteerName,
    required this.category,
    required this.points,
    this.eventsAttended = 0,
    this.totalHours = 0.0,
    this.isAnonymous = false,
    this.avatarUrl,
  });

  factory LeaderboardItemModel.fromJson(Map<String, dynamic> json) {
    return LeaderboardItemModel(
      rank: json['rank'] as int? ?? 0,
      volunteerProfileId: json['volunteer_profile_id'] as String?,
      volunteerName: json['volunteer_name'] as String? ?? 'Volunteer',
      category: json['category'] as String? ?? 'STUDENT',
      points: json['total_points'] != null
          ? (json['total_points'] is num
              ? (json['total_points'] as num).round()
              : (double.tryParse(json['total_points'].toString()) ?? 0.0)
                  .round())
          : 0,
      eventsAttended: json['events_attended'] as int? ?? 0,
      totalHours: json['total_hours'] != null
          ? (json['total_hours'] is num
              ? (json['total_hours'] as num).toDouble()
              : double.tryParse(json['total_hours'].toString()) ?? 0.0)
          : 0.0,
      isAnonymous: json['is_anonymous'] as bool? ?? false,
      avatarUrl: json['avatar_url'] as String?,
    );
  }
}
