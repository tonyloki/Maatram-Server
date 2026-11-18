import 'package:intl/intl.dart';
import 'package:meta/meta.dart';

double _parseDouble(dynamic value, [double defaultValue = 0.0]) {
  if (value == null) return defaultValue;
  if (value is num) return value.toDouble();
  if (value is String) return double.tryParse(value) ?? defaultValue;
  return defaultValue;
}

int _parseInt(dynamic value, [int defaultValue = 0]) {
  if (value == null) return defaultValue;
  if (value is num) return value.toInt();
  if (value is String) {
    return int.tryParse(value) ??
        (double.tryParse(value)?.toInt() ?? defaultValue);
  }
  return defaultValue;
}

/// Models an achievement badge definition and earned status.
@immutable
class AchievementModel {
  final String id;
  final String code;
  final String title;
  final String description;
  final String iconUrl;
  final String category;
  final String criteriaType;
  final double criteriaThreshold;
  final bool isActive;
  final bool isEarned;
  final DateTime? awardedAt;

  const AchievementModel({
    required this.id,
    required this.code,
    required this.title,
    required this.description,
    required this.iconUrl,
    required this.category,
    required this.criteriaType,
    required this.criteriaThreshold,
    required this.isActive,
    this.isEarned = false,
    this.awardedAt,
  });

  factory AchievementModel.fromJson(Map<String, dynamic> json) {
    return AchievementModel(
      id: json['id']?.toString() ?? '',
      code: json['code']?.toString() ?? '',
      title: json['title']?.toString() ?? 'Badge',
      description: json['description']?.toString() ?? '',
      iconUrl: json['icon_url']?.toString() ?? '',
      category: json['category']?.toString() ?? 'GENERAL',
      criteriaType: json['criteria_type']?.toString() ?? 'HOURS',
      criteriaThreshold: _parseDouble(json['criteria_threshold'], 0.0),
      isActive: json['is_active'] as bool? ?? true,
      isEarned: json['is_earned'] as bool? ?? false,
      awardedAt: json['awarded_at'] != null
          ? DateTime.tryParse(json['awarded_at'] as String)
          : null,
    );
  }

  String get formattedAwardedDate {
    if (awardedAt == null) return '';
    return DateFormat('d MMM yyyy').format(awardedAt!.toLocal());
  }
}

/// Collection of achievements for a volunteer
@immutable
class VolunteerAchievementsModel {
  final List<AchievementModel> items;
  final int totalEarned;
  final int totalAvailable;

  const VolunteerAchievementsModel({
    required this.items,
    required this.totalEarned,
    required this.totalAvailable,
  });

  factory VolunteerAchievementsModel.fromJson(Map<String, dynamic> json) {
    final list = (json['items'] as List<dynamic>?) ?? [];
    return VolunteerAchievementsModel(
      items: list
          .map((i) => AchievementModel.fromJson(i as Map<String, dynamic>))
          .toList(),
      totalEarned: _parseInt(json['total_earned'], 0),
      totalAvailable: _parseInt(json['total_available'], 0),
    );
  }
}
