import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/registration_payload.dart';

class RegistrationFormState {
  final int currentStep; // 0 to 5 (representing Steps 1 to 6)

  // Step 1: Basic Details
  final String firstName;
  final String lastName;
  final String email;
  final String mobileNumber;
  final int? age;
  final String gender; // MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY

  // Step 2: Category
  final String category; // STUDENT, ALUMNI, CORPORATE

  // Step 3: Category Specifics
  // Student
  final String studentCollegeName;
  final String studentDegree;
  final String studentDepartment;
  final int studentBatchYear;
  final int studentCurrentYear;
  final String studentMaatramRegNo;

  // Alumni
  final String alumniCollegeName;
  final String alumniDegree;
  final String alumniDepartment;
  final int alumniBatchYear;
  final int alumniGraduationYear;
  final String alumniOrganisation;
  final String alumniJobRole;
  final double alumniYearsOfExp;
  final String alumniLocation;
  final List<String> alumniSkills;

  // Corporate
  final String corporateOrganisation;
  final String corporateDesignation;
  final double corporateYearsOfExp;
  final String corporateLocation;
  final List<String> corporateSkills;

  // Step 4: Volunteering Areas & Availability
  final List<String> selectedSkills;
  final String availability;

  // Step 5: Privacy and Consent
  final bool leaderboardVisible;
  final bool nameVisible;
  final bool thankYouEmails;
  final bool linkedinContent;
  final bool contactAvailable;
  final bool mediaUsage;
  final bool termsAccepted;

  // Step 6: Credentials
  final String password;
  final String confirmPassword;

  // Validation errors map
  final Map<String, String> errors;
  final bool isSubmitting;
  final String? submissionError;

  const RegistrationFormState({
    this.currentStep = 0,
    this.firstName = '',
    this.lastName = '',
    this.email = '',
    this.mobileNumber = '+91',
    this.age = 20,
    this.gender = 'PREFER_NOT_TO_SAY',
    this.category = 'STUDENT',
    this.studentCollegeName = '',
    this.studentDegree = 'B.E / B.Tech',
    this.studentDepartment = 'Computer Science',
    this.studentBatchYear = 2024,
    this.studentCurrentYear = 3,
    this.studentMaatramRegNo = '',
    this.alumniCollegeName = '',
    this.alumniDegree = '',
    this.alumniDepartment = '',
    this.alumniBatchYear = 2020,
    this.alumniGraduationYear = 2024,
    this.alumniOrganisation = '',
    this.alumniJobRole = '',
    this.alumniYearsOfExp = 1.0,
    this.alumniLocation = 'Chennai',
    this.alumniSkills = const [],
    this.corporateOrganisation = '',
    this.corporateDesignation = '',
    this.corporateYearsOfExp = 3.0,
    this.corporateLocation = 'Chennai',
    this.corporateSkills = const [],
    this.selectedSkills = const ['Mentoring', 'School Visits'],
    this.availability = 'Weekends',
    this.leaderboardVisible = false,
    this.nameVisible = false,
    this.thankYouEmails = false,
    this.linkedinContent = false,
    this.contactAvailable = false,
    this.mediaUsage = false,
    this.termsAccepted = true,
    this.password = '',
    this.confirmPassword = '',
    this.errors = const {},
    this.isSubmitting = false,
    this.submissionError,
  });

  RegistrationFormState copyWith({
    int? currentStep,
    String? firstName,
    String? lastName,
    String? email,
    String? mobileNumber,
    int? age,
    String? gender,
    String? category,
    String? studentCollegeName,
    String? studentDegree,
    String? studentDepartment,
    int? studentBatchYear,
    int? studentCurrentYear,
    String? studentMaatramRegNo,
    String? alumniCollegeName,
    String? alumniDegree,
    String? alumniDepartment,
    int? alumniBatchYear,
    int? alumniGraduationYear,
    String? alumniOrganisation,
    String? alumniJobRole,
    double? alumniYearsOfExp,
    String? alumniLocation,
    List<String>? alumniSkills,
    String? corporateOrganisation,
    String? corporateDesignation,
    double? corporateYearsOfExp,
    String? corporateLocation,
    List<String>? corporateSkills,
    List<String>? selectedSkills,
    String? availability,
    bool? leaderboardVisible,
    bool? nameVisible,
    bool? thankYouEmails,
    bool? linkedinContent,
    bool? contactAvailable,
    bool? mediaUsage,
    bool? termsAccepted,
    String? password,
    String? confirmPassword,
    Map<String, String>? errors,
    bool? isSubmitting,
    String? submissionError,
  }) {
    return RegistrationFormState(
      currentStep: currentStep ?? this.currentStep,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      email: email ?? this.email,
      mobileNumber: mobileNumber ?? this.mobileNumber,
      age: age ?? this.age,
      gender: gender ?? this.gender,
      category: category ?? this.category,
      studentCollegeName: studentCollegeName ?? this.studentCollegeName,
      studentDegree: studentDegree ?? this.studentDegree,
      studentDepartment: studentDepartment ?? this.studentDepartment,
      studentBatchYear: studentBatchYear ?? this.studentBatchYear,
      studentCurrentYear: studentCurrentYear ?? this.studentCurrentYear,
      studentMaatramRegNo: studentMaatramRegNo ?? this.studentMaatramRegNo,
      alumniCollegeName: alumniCollegeName ?? this.alumniCollegeName,
      alumniDegree: alumniDegree ?? this.alumniDegree,
      alumniDepartment: alumniDepartment ?? this.alumniDepartment,
      alumniBatchYear: alumniBatchYear ?? this.alumniBatchYear,
      alumniGraduationYear: alumniGraduationYear ?? this.alumniGraduationYear,
      alumniOrganisation: alumniOrganisation ?? this.alumniOrganisation,
      alumniJobRole: alumniJobRole ?? this.alumniJobRole,
      alumniYearsOfExp: alumniYearsOfExp ?? this.alumniYearsOfExp,
      alumniLocation: alumniLocation ?? this.alumniLocation,
      alumniSkills: alumniSkills ?? this.alumniSkills,
      corporateOrganisation:
          corporateOrganisation ?? this.corporateOrganisation,
      corporateDesignation: corporateDesignation ?? this.corporateDesignation,
      corporateYearsOfExp: corporateYearsOfExp ?? this.corporateYearsOfExp,
      corporateLocation: corporateLocation ?? this.corporateLocation,
      corporateSkills: corporateSkills ?? this.corporateSkills,
      selectedSkills: selectedSkills ?? this.selectedSkills,
      availability: availability ?? this.availability,
      leaderboardVisible: leaderboardVisible ?? this.leaderboardVisible,
      nameVisible: nameVisible ?? this.nameVisible,
      thankYouEmails: thankYouEmails ?? this.thankYouEmails,
      linkedinContent: linkedinContent ?? this.linkedinContent,
      contactAvailable: contactAvailable ?? this.contactAvailable,
      mediaUsage: mediaUsage ?? this.mediaUsage,
      termsAccepted: termsAccepted ?? this.termsAccepted,
      password: password ?? this.password,
      confirmPassword: confirmPassword ?? this.confirmPassword,
      errors: errors ?? this.errors,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      submissionError: submissionError,
    );
  }

  /// Convert state into backend-aligned `RegistrationPayload`.
  RegistrationPayload toPayload() {
    Map<String, dynamic>? studentDetails;
    Map<String, dynamic>? alumniDetails;
    Map<String, dynamic>? corporateDetails;

    if (category == 'STUDENT') {
      studentDetails = {
        'college_name': studentCollegeName.trim(),
        'degree': studentDegree.trim(),
        'department': studentDepartment.trim(),
        'batch_year': studentBatchYear,
        'current_year': studentCurrentYear,
        'maatram_reg_number': studentMaatramRegNo.trim().isNotEmpty
            ? studentMaatramRegNo.trim()
            : 'MAT-${studentBatchYear.toString().substring(2)}-${studentCurrentYear}01',
      };
    } else if (category == 'ALUMNI') {
      alumniDetails = {
        'college_name': alumniCollegeName.trim().isNotEmpty
            ? alumniCollegeName.trim()
            : 'College of Engineering Guindy',
        'degree': alumniDegree.trim().isNotEmpty ? alumniDegree.trim() : 'B.E',
        'department': alumniDepartment.trim().isNotEmpty
            ? alumniDepartment.trim()
            : 'ECE',
        'batch_year': alumniBatchYear,
        'graduation_year': alumniGraduationYear,
        'organisation': alumniOrganisation.trim().isNotEmpty
            ? alumniOrganisation.trim()
            : 'Maatram Alumnus',
        'job_role': alumniJobRole.trim().isNotEmpty
            ? alumniJobRole.trim()
            : 'Software Engineer',
        'years_of_experience': alumniYearsOfExp,
        'location': alumniLocation.trim().isNotEmpty
            ? alumniLocation.trim()
            : 'Chennai',
        'skills': alumniSkills.isNotEmpty
            ? alumniSkills
            : ['Mentorship', 'Career Guidance'],
      };
    } else if (category == 'CORPORATE') {
      corporateDetails = {
        'organisation': corporateOrganisation.trim(),
        'designation': corporateDesignation.trim(),
        'years_of_experience': corporateYearsOfExp,
        'location': corporateLocation.trim(),
        'skills': corporateSkills.isNotEmpty
            ? corporateSkills
            : ['Mock Interviews', 'Panel Review'],
      };
    }

    return RegistrationPayload(
      email: email.trim().toLowerCase(),
      password: password,
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      mobileNumber: mobileNumber.trim(),
      age: age ?? 21,
      gender: gender,
      category: category,
      studentDetails: studentDetails,
      alumniDetails: alumniDetails,
      corporateDetails: corporateDetails,
      leaderboardVisible: leaderboardVisible,
      nameVisible: nameVisible,
      thankYouEmails: thankYouEmails,
      linkedinContent: linkedinContent,
      contactAvailable: contactAvailable,
      mediaUsage: mediaUsage,
    );
  }
}

class RegistrationNotifier extends StateNotifier<RegistrationFormState> {
  RegistrationNotifier() : super(const RegistrationFormState());

  void setStep(int step) {
    state = state.copyWith(currentStep: step, errors: {});
  }

  void nextStep() {
    if (validateCurrentStep()) {
      if (state.currentStep < 5) {
        state = state.copyWith(currentStep: state.currentStep + 1, errors: {});
      }
    }
  }

  void previousStep() {
    if (state.currentStep > 0) {
      state = state.copyWith(currentStep: state.currentStep - 1, errors: {});
    }
  }

  void updateBasicDetails({
    String? firstName,
    String? lastName,
    String? email,
    String? mobileNumber,
    int? age,
    String? gender,
  }) {
    state = state.copyWith(
      firstName: firstName,
      lastName: lastName,
      email: email,
      mobileNumber: mobileNumber,
      age: age,
      gender: gender,
    );
  }

  void setCategory(String category) {
    state = state.copyWith(category: category);
  }

  void updateStudentDetails({
    String? collegeName,
    String? degree,
    String? department,
    int? batchYear,
    int? currentYear,
    String? maatramRegNo,
  }) {
    state = state.copyWith(
      studentCollegeName: collegeName,
      studentDegree: degree,
      studentDepartment: department,
      studentBatchYear: batchYear,
      studentCurrentYear: currentYear,
      studentMaatramRegNo: maatramRegNo,
    );
  }

  void updateAlumniDetails({
    String? collegeName,
    String? degree,
    String? department,
    int? batchYear,
    int? graduationYear,
    String? organisation,
    String? jobRole,
    double? yearsOfExp,
    String? location,
    List<String>? skills,
  }) {
    state = state.copyWith(
      alumniCollegeName: collegeName,
      alumniDegree: degree,
      alumniDepartment: department,
      alumniBatchYear: batchYear,
      alumniGraduationYear: graduationYear,
      alumniOrganisation: organisation,
      alumniJobRole: jobRole,
      alumniYearsOfExp: yearsOfExp,
      alumniLocation: location,
      alumniSkills: skills,
    );
  }

  void updateCorporateDetails({
    String? organisation,
    String? designation,
    double? yearsOfExp,
    String? location,
    List<String>? skills,
  }) {
    state = state.copyWith(
      corporateOrganisation: organisation,
      corporateDesignation: designation,
      corporateYearsOfExp: yearsOfExp,
      corporateLocation: location,
      corporateSkills: skills,
    );
  }

  void updateSkillsAndAvailability({
    List<String>? skills,
    String? availability,
  }) {
    state = state.copyWith(
      selectedSkills: skills,
      availability: availability,
    );
  }

  void updateConsent({
    bool? leaderboardVisible,
    bool? nameVisible,
    bool? thankYouEmails,
    bool? linkedinContent,
    bool? contactAvailable,
    bool? mediaUsage,
    bool? termsAccepted,
  }) {
    state = state.copyWith(
      leaderboardVisible: leaderboardVisible,
      nameVisible: nameVisible,
      thankYouEmails: thankYouEmails,
      linkedinContent: linkedinContent,
      contactAvailable: contactAvailable,
      mediaUsage: mediaUsage,
      termsAccepted: termsAccepted,
    );
  }

  void updateCredentials({
    String? password,
    String? confirmPassword,
  }) {
    state = state.copyWith(
      password: password,
      confirmPassword: confirmPassword,
    );
  }

  bool validateCurrentStep() {
    final errors = <String, String>{};

    switch (state.currentStep) {
      case 0: // Step 1: Basic Details
        if (state.firstName.trim().isEmpty) {
          errors['firstName'] = 'Enter your first name.';
        }
        if (state.lastName.trim().isEmpty) {
          errors['lastName'] = 'Enter your last name.';
        }
        if (state.email.trim().isEmpty) {
          errors['email'] = 'Enter your email address.';
        } else if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$')
            .hasMatch(state.email.trim())) {
          errors['email'] = 'Enter a valid email address.';
        }
        if (state.mobileNumber.trim().length < 8) {
          errors['mobileNumber'] =
              'Enter a valid mobile number with country code.';
        }
        break;

      case 1: // Step 2: Category Selection
        // Valid by default
        break;

      case 2: // Step 3: Category Specifics
        if (state.category == 'STUDENT') {
          if (state.studentCollegeName.trim().isEmpty) {
            errors['studentCollegeName'] = 'Enter your college name.';
          }
          if (state.studentDegree.trim().isEmpty) {
            errors['studentDegree'] = 'Enter your degree program.';
          }
          if (state.studentDepartment.trim().isEmpty) {
            errors['studentDepartment'] = 'Enter your department / major.';
          }
        } else if (state.category == 'ALUMNI') {
          if (state.alumniCollegeName.trim().isEmpty) {
            errors['alumniCollegeName'] = 'Enter your alma mater college name.';
          }
          if (state.alumniOrganisation.trim().isEmpty) {
            errors['alumniOrganisation'] =
                'Enter your current company or organization.';
          }
        } else if (state.category == 'CORPORATE') {
          if (state.corporateOrganisation.trim().isEmpty) {
            errors['corporateOrganisation'] = 'Enter your organization name.';
          }
          if (state.corporateDesignation.trim().isEmpty) {
            errors['corporateDesignation'] =
                'Enter your professional designation.';
          }
        }
        break;

      case 3: // Step 4: Skills and Availability
        // Valid
        break;

      case 4: // Step 5: Privacy and Consent
        if (!state.termsAccepted) {
          errors['termsAccepted'] =
              'You must agree to the Maatram Terms and Privacy Policy to continue.';
        }
        break;

      case 5: // Step 6: Credentials & Review
        if (state.password.length < 8) {
          errors['password'] = 'Password must be at least 8 characters long.';
        }
        if (state.confirmPassword != state.password) {
          errors['confirmPassword'] = 'Passwords do not match.';
        }
        break;
    }

    state = state.copyWith(errors: errors);
    return errors.isEmpty;
  }
}

final registrationProvider =
    StateNotifierProvider<RegistrationNotifier, RegistrationFormState>((ref) {
  return RegistrationNotifier();
});

final registrationNotifierProvider = registrationProvider;
