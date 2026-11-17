import 'package:meta/meta.dart';

/// Models the affirmative consent record from `GET /api/v1/consent/me`.
@immutable
class ConsentModel {
  final String id;
  final String volunteerProfileId;
  final bool leaderboardVisible;
  final bool nameVisible;
  final bool thankYouEmails;
  final bool linkedinContent;
  final bool contactAvailable;
  final bool mediaUsage;
  final int version;
  final DateTime updatedAt;

  const ConsentModel({
    required this.id,
    required this.volunteerProfileId,
    required this.leaderboardVisible,
    required this.nameVisible,
    required this.thankYouEmails,
    required this.linkedinContent,
    required this.contactAvailable,
    required this.mediaUsage,
    required this.version,
    required this.updatedAt,
  });

  factory ConsentModel.fromJson(Map<String, dynamic> json) {
    return ConsentModel(
      id: json['id']?.toString() ?? '',
      volunteerProfileId: json['volunteer_profile_id']?.toString() ?? '',
      leaderboardVisible: json['leaderboard_visible'] as bool? ?? false,
      nameVisible: json['name_visible'] as bool? ?? false,
      thankYouEmails: json['thank_you_emails'] as bool? ?? false,
      linkedinContent: json['linkedin_content'] as bool? ?? false,
      contactAvailable: json['contact_available'] as bool? ?? false,
      mediaUsage: json['media_usage'] as bool? ?? false,
      version: (json['version'] as num?)?.toInt() ?? 1,
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toUpdateJson() {
    return {
      'leaderboard_visible': leaderboardVisible,
      'name_visible': nameVisible,
      'thank_you_emails': thankYouEmails,
      'linkedin_content': linkedinContent,
      'contact_available': contactAvailable,
      'media_usage': mediaUsage,
    };
  }

  ConsentModel copyWith({
    bool? leaderboardVisible,
    bool? nameVisible,
    bool? thankYouEmails,
    bool? linkedinContent,
    bool? contactAvailable,
    bool? mediaUsage,
  }) {
    return ConsentModel(
      id: id,
      volunteerProfileId: volunteerProfileId,
      leaderboardVisible: leaderboardVisible ?? this.leaderboardVisible,
      nameVisible: nameVisible ?? this.nameVisible,
      thankYouEmails: thankYouEmails ?? this.thankYouEmails,
      linkedinContent: linkedinContent ?? this.linkedinContent,
      contactAvailable: contactAvailable ?? this.contactAvailable,
      mediaUsage: mediaUsage ?? this.mediaUsage,
      version: version,
      updatedAt: DateTime.now(),
    );
  }
}
