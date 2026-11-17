import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/user_session.dart';

/// Secure persistence layer for JWT access and refresh tokens, plus session metadata.
/// Backed by iOS Keychain and Android EncryptedSharedPreferences.
class TokenStorage {
  static const String _accessTokenKey = 'maatram_jwt_access_token';
  static const String _refreshTokenKey = 'maatram_jwt_refresh_token';
  static const String _userSessionKey = 'maatram_user_session_metadata';
  static const String _biometricEnabledKey = 'maatram_biometric_enabled';
  static const String _firstLaunchCompletedKey =
      'maatram_first_launch_welcome_seen';

  // In-memory fallback layer for seamless web/offline resilience
  static String? _memAccessToken;
  static String? _memRefreshToken;
  static UserSession? _memUserSession;

  final FlutterSecureStorage _storage;

  TokenStorage({FlutterSecureStorage? storage})
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
              iOptions:
                  IOSOptions(accessibility: KeychainAccessibility.first_unlock),
            );

  /// Persist rotated or newly issued tokens atomically.
  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    _memAccessToken = accessToken;
    _memRefreshToken = refreshToken;
    try {
      await Future.wait([
        _storage.write(key: _accessTokenKey, value: accessToken),
        _storage.write(key: _refreshTokenKey, value: refreshToken),
      ]);
    } catch (_) {
      // In-memory fallback if platform storage fails
    }
  }

  /// Retrieve the active access token.
  Future<String?> getAccessToken() async {
    try {
      final token = await _storage.read(key: _accessTokenKey);
      if (token != null && token.isNotEmpty) return token;
    } catch (_) {}
    return _memAccessToken;
  }

  /// Retrieve the active refresh token.
  Future<String?> getRefreshToken() async {
    try {
      final token = await _storage.read(key: _refreshTokenKey);
      if (token != null && token.isNotEmpty) return token;
    } catch (_) {}
    return _memRefreshToken;
  }

  /// Persist serialized user session metadata for instant offline hydration.
  Future<void> saveUserSession(UserSession session) async {
    _memUserSession = session;
    try {
      await _storage.write(
        key: _userSessionKey,
        value: jsonEncode(session.toJson()),
      );
    } catch (_) {}
  }

  /// Retrieve serialized user session metadata if available.
  Future<UserSession?> getUserSession() async {
    try {
      final raw = await _storage.read(key: _userSessionKey);
      if (raw != null && raw.isNotEmpty) {
        final decoded = jsonDecode(raw) as Map<String, dynamic>;
        return UserSession(
          userId: decoded['userId']?.toString() ?? '',
          email: decoded['email']?.toString() ?? '',
          role: decoded['role']?.toString() ?? 'VOLUNTEER',
          status: decoded['status']?.toString() ?? 'PENDING_VERIFICATION',
          accessToken: decoded['accessToken']?.toString() ?? '',
          refreshToken: decoded['refreshToken']?.toString() ?? '',
          firstName: decoded['firstName']?.toString(),
          lastName: decoded['lastName']?.toString(),
          category: decoded['category']?.toString(),
          rejectionReason: decoded['rejectionReason']?.toString(),
        );
      }
    } catch (_) {}
    return _memUserSession;
  }

  /// Biometric preference persistence
  Future<void> setBiometricEnabled(bool enabled) async {
    try {
      await _storage.write(
          key: _biometricEnabledKey, value: enabled ? 'true' : 'false');
    } catch (_) {}
  }

  Future<bool> isBiometricEnabled() async {
    try {
      final val = await _storage.read(key: _biometricEnabledKey);
      return val == 'true';
    } catch (_) {
      return false;
    }
  }

  /// Track whether first-launch welcome screen has been shown
  Future<void> setFirstLaunchCompleted(bool completed) async {
    try {
      await _storage.write(
          key: _firstLaunchCompletedKey, value: completed ? 'true' : 'false');
    } catch (_) {}
  }

  Future<bool> isFirstLaunchCompleted() async {
    try {
      final val = await _storage.read(key: _firstLaunchCompletedKey);
      return val == 'true';
    } catch (_) {
      return false;
    }
  }

  /// Wipe all credentials from secure hardware storage (e.g., on logout or revocation).
  Future<void> clearTokens() async {
    _memAccessToken = null;
    _memRefreshToken = null;
    _memUserSession = null;
    try {
      await Future.wait([
        _storage.delete(key: _accessTokenKey),
        _storage.delete(key: _refreshTokenKey),
        _storage.delete(key: _userSessionKey),
      ]);
    } catch (_) {}
  }

  /// Check whether credentials exist.
  Future<bool> hasValidSession() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }
}
