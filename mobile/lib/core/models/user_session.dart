/// Domain model representing an authenticated user session in the mobile app.
class UserSession {
  final String userId;
  final String email;
  final String role;
  final String status;
  final String accessToken;
  final String refreshToken;
  final String? firstName;
  final String? lastName;
  final String? category;
  final String? rejectionReason;

  const UserSession({
    required this.userId,
    required this.email,
    required this.role,
    required this.status,
    required this.accessToken,
    required this.refreshToken,
    this.firstName,
    this.lastName,
    this.category,
    this.rejectionReason,
  });

  bool get isApproved => status.toUpperCase() == 'APPROVED';
  bool get isPendingVerification =>
      status.toUpperCase() == 'PENDING_VERIFICATION';
  bool get isPendingApproval => status.toUpperCase() == 'PENDING_APPROVAL';
  bool get isRejected => status.toUpperCase() == 'REJECTED';

  String get displayName {
    if (firstName != null && firstName!.isNotEmpty) {
      if (lastName != null && lastName!.isNotEmpty) {
        return '$firstName $lastName';
      }
      return firstName!;
    }
    return email.split('@').first;
  }

  factory UserSession.fromJson(Map<String, dynamic> json) {
    final user =
        json['user'] is Map ? json['user'] as Map<String, dynamic> : json;
    return UserSession(
      userId: user['id']?.toString() ?? json['user_id']?.toString() ?? '',
      email: user['email']?.toString() ?? '',
      role: user['role']?.toString() ?? 'VOLUNTEER',
      status: user['status']?.toString() ?? 'PENDING_VERIFICATION',
      accessToken: json['access_token']?.toString() ?? '',
      refreshToken: json['refresh_token']?.toString() ?? '',
      firstName:
          user['first_name']?.toString() ?? json['first_name']?.toString(),
      lastName: user['last_name']?.toString() ?? json['last_name']?.toString(),
      category: user['category']?.toString() ?? json['category']?.toString(),
      rejectionReason: user['rejection_reason']?.toString() ??
          json['rejection_reason']?.toString(),
    );
  }

  Map<String, dynamic> toJson() => {
        'userId': userId,
        'email': email,
        'role': role,
        'status': status,
        'accessToken': accessToken,
        'refreshToken': refreshToken,
        'firstName': firstName,
        'lastName': lastName,
        'category': category,
        'rejectionReason': rejectionReason,
      };

  UserSession copyWith({
    String? userId,
    String? email,
    String? role,
    String? status,
    String? accessToken,
    String? refreshToken,
    String? firstName,
    String? lastName,
    String? category,
    String? rejectionReason,
  }) {
    return UserSession(
      userId: userId ?? this.userId,
      email: email ?? this.email,
      role: role ?? this.role,
      status: status ?? this.status,
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      category: category ?? this.category,
      rejectionReason: rejectionReason ?? this.rejectionReason,
    );
  }
}
