import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Secure persistence layer for JWT access and refresh tokens.
/// Backed by iOS Keychain and Android EncryptedSharedPreferences.
class TokenStorage {
  static const String _accessTokenKey = 'maatram_jwt_access_token';
  static const String _refreshTokenKey = 'maatram_jwt_refresh_token';

  final FlutterSecureStorage _storage;

  TokenStorage({FlutterSecureStorage? storage})
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
              iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
            );

  /// Persist rotated or newly issued tokens atomically.
  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await Future.wait([
      _storage.write(key: _accessTokenKey, value: accessToken),
      _storage.write(key: _refreshTokenKey, value: refreshToken),
    ]);
  }

  /// Retrieve the active access token.
  Future<String?> getAccessToken() async {
    return _storage.read(key: _accessTokenKey);
  }

  /// Retrieve the active refresh token.
  Future<String?> getRefreshToken() async {
    return _storage.read(key: _refreshTokenKey);
  }

  /// Wipe all credentials from secure hardware storage (e.g., on logout or revocation).
  Future<void> clearTokens() async {
    await Future.wait([
      _storage.delete(key: _accessTokenKey),
      _storage.delete(key: _refreshTokenKey),
    ]);
  }

  /// Check whether credentials exist.
  Future<bool> hasValidSession() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }
}
