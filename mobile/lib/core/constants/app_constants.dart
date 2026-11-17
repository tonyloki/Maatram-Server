/// Application-wide constants, branding metadata, and storage keys.
abstract final class AppConstants {
  static const String appName = 'Maatram Volunteering';
  static const String appTagline = 'Empowering Communities, Transforming Lives';
  static const String foundationName = 'Maatram Foundation';

  // Storage Keys
  static const String keyAccessToken = 'maatram_jwt_access_token';
  static const String keyRefreshToken = 'maatram_jwt_refresh_token';
  static const String keyUserSession = 'maatram_user_session';
  static const String keyThemeMode = 'maatram_theme_mode';

  // Gamification & Attendance Standards
  static const int minHoursForCredit = 1;
  static const int defaultPointsPerEvent = 10;
  static const int pointsPerHour = 2; // Formula: Points = 10E + 2H
}
