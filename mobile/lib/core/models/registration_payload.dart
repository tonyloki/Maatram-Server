/// Domain model representing the 6-step volunteer registration payload
/// strictly aligned with the backend `RegisterRequest` Pydantic schema.
class RegistrationPayload {
  final String email;
  final String password;
  final String firstName;
  final String lastName;
  final String mobileNumber;
  final int age;
  final String gender; // MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY
  final String category; // STUDENT, ALUMNI, CORPORATE

  // Minor Safeguarding
  final String? parentGuardianName;
  final String? parentGuardianRelationship;
  final String? parentGuardianContact;
  final bool parentalConsentClaimed;
  final bool parentalConsentSubmitted;

  // Category Details
  final Map<String, dynamic>? studentDetails;
  final Map<String, dynamic>? alumniDetails;
  final Map<String, dynamic>? corporateDetails;

  // Consent Preferences (6 Independent Flags)
  final bool leaderboardVisible;
  final bool nameVisible;
  final bool thankYouEmails;
  final bool linkedinContent;
  final bool contactAvailable;
  final bool mediaUsage;

  const RegistrationPayload({
    required this.email,
    required this.password,
    required this.firstName,
    required this.lastName,
    required this.mobileNumber,
    required this.age,
    required this.gender,
    required this.category,
    this.parentGuardianName,
    this.parentGuardianRelationship,
    this.parentGuardianContact,
    this.parentalConsentClaimed = false,
    this.parentalConsentSubmitted = false,
    this.studentDetails,
    this.alumniDetails,
    this.corporateDetails,
    this.leaderboardVisible = false,
    this.nameVisible = false,
    this.thankYouEmails = false,
    this.linkedinContent = false,
    this.contactAvailable = false,
    this.mediaUsage = false,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'email': email.trim().toLowerCase(),
      'password': password,
      'first_name': firstName.trim(),
      'last_name': lastName.trim(),
      'mobile_number': mobileNumber.trim(),
      'age': age,
      'gender': gender,
      'category': category,
      'parental_consent_claimed': parentalConsentClaimed,
      'parental_consent_submitted': parentalConsentSubmitted,
      'parental_consent_evidence_submitted': false,
      'consent': {
        'leaderboard_visible': leaderboardVisible,
        'name_visible': nameVisible,
        'thank_you_emails': thankYouEmails,
        'linkedin_content': linkedinContent,
        'contact_available': contactAvailable,
        'media_usage': mediaUsage,
      },
    };

    if (parentGuardianName != null && parentGuardianName!.isNotEmpty) {
      map['parent_guardian_name'] = parentGuardianName;
    }
    if (parentGuardianRelationship != null &&
        parentGuardianRelationship!.isNotEmpty) {
      map['parent_guardian_relationship'] = parentGuardianRelationship;
    }
    if (parentGuardianContact != null && parentGuardianContact!.isNotEmpty) {
      map['parent_guardian_contact'] = parentGuardianContact;
    }

    if (category == 'STUDENT' && studentDetails != null) {
      map['student_details'] = studentDetails;
    } else if (category == 'ALUMNI' && alumniDetails != null) {
      map['alumni_details'] = alumniDetails;
    } else if (category == 'CORPORATE' && corporateDetails != null) {
      map['corporate_details'] = corporateDetails;
    }

    return map;
  }
}
