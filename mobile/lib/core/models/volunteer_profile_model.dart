import 'package:meta/meta.dart';

/// Models the backend `VolunteerProfileResponse` from `GET /api/v1/volunteers/me`.
@immutable
class VolunteerProfileModel {
  final String id;
  final String userId;
  final String firstName;
  final String lastName;
  final String? mobileNumber;
  final int age;
  final String gender;
  final String category; // STUDENT, ALUMNI, CORPORATE
  final String? city;
  final String? state;
  final String? avatarMediaId;
  final String? avatarUrl;
  final bool parentalConsentVerified;
  final String? organizationOrCollege;

  const VolunteerProfileModel({
    required this.id,
    required this.userId,
    required this.firstName,
    required this.lastName,
    this.mobileNumber,
    required this.age,
    required this.gender,
    required this.category,
    this.city,
    this.state,
    this.avatarMediaId,
    this.avatarUrl,
    this.parentalConsentVerified = false,
    this.organizationOrCollege,
  });

  String get fullName => '$firstName $lastName'.trim();

  String get shortName {
    if (lastName.isNotEmpty) {
      return '$firstName ${lastName[0].toUpperCase()}.';
    }
    return firstName;
  }

  String get categoryDisplay {
    switch (category.toUpperCase()) {
      case 'STUDENT':
        return 'Student';
      case 'ALUMNI':
        return 'Alumni';
      case 'CORPORATE':
        return 'Corporate Panelist';
      default:
        return category;
    }
  }

  String get subtitle {
    final cat = categoryDisplay;
    if (organizationOrCollege != null && organizationOrCollege!.isNotEmpty) {
      return '$cat • $organizationOrCollege';
    }
    if (city != null && city!.isNotEmpty) {
      return '$cat • $city';
    }
    return cat;
  }

  factory VolunteerProfileModel.fromJson(Map<String, dynamic> json) {
    String? org;
    if (json['student_profile'] is Map) {
      final sp = json['student_profile'] as Map<String, dynamic>;
      org = (sp['college_name'] ?? sp['college'])?.toString();
    } else if (json['alumni_profile'] is Map) {
      final ap = json['alumni_profile'] as Map<String, dynamic>;
      org = (ap['organisation'] ??
              ap['college_name'] ??
              ap['company'] ??
              ap['current_organization'])
          ?.toString();
    } else if (json['corporate_profile'] is Map) {
      final cp = json['corporate_profile'] as Map<String, dynamic>;
      org = (cp['organisation'] ?? cp['company_name'])?.toString();
    }

    return VolunteerProfileModel(
      id: json['id']?.toString() ?? '',
      userId: json['user_id']?.toString() ?? '',
      firstName: json['first_name']?.toString() ?? '',
      lastName: json['last_name']?.toString() ?? '',
      mobileNumber: json['mobile_number']?.toString(),
      age: (json['age'] as num?)?.toInt() ?? 18,
      gender: json['gender']?.toString() ?? 'OTHER',
      category: json['category']?.toString() ?? 'STUDENT',
      city: json['city']?.toString(),
      state: json['state']?.toString(),
      avatarMediaId: json['avatar_media_id']?.toString(),
      avatarUrl: json['avatar_url']?.toString(),
      parentalConsentVerified: json['parental_consent_verified'] == true,
      organizationOrCollege: org,
    );
  }
}
