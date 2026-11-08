/// Domain model representing an authenticated user session in the mobile app.
class UserSession {
  final String userId;
  final String email;
  final String role;
  final String status;
  final String accessToken;
  final String refreshToken;

  const UserSession({
    required this.userId,
    required this.email,
    required this.role,
    required this.status,
    required this.accessToken,
    required this.refreshToken,
  });

  factory UserSession.fromJson(Map<String, dynamic> json) {
    final user = json['user'] is Map ? json['user'] as Map<String, dynamic> : json;
    return UserSession(
      userId: user['id']?.toString() ?? '',
      email: user['email']?.toString() ?? '',
      role: user['role']?.toString() ?? 'VOLUNTEER',
      status: user['status']?.toString() ?? 'PENDING',
      accessToken: json['access_token']?.toString() ?? '',
      refreshToken: json['refresh_token']?.toString() ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
        'userId': userId,
        'email': email,
        'role': role,
        'status': status,
        'accessToken': accessToken,
        'refreshToken': refreshToken,
      };
}
