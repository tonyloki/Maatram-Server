import 'package:dio/dio.dart';
import '../../../core/errors/app_exception.dart';
import '../../../core/models/registration_payload.dart';
import '../../../core/models/user_session.dart';
import '../../../core/network/api_client.dart';

/// Repository interacting with FastAPI authentication and identity endpoints.
class AuthRepository {
  final ApiClient _client;

  AuthRepository({required ApiClient client}) : _client = client;

  /// Authenticate credentials against `/auth/login`.
  Future<UserSession> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _client.post(
        '/auth/login',
        data: {
          'email': email.trim().toLowerCase(),
          'password': password,
          'client_type': 'MOBILE',
        },
      );

      final data = response.data as Map<String, dynamic>;
      return UserSession.fromJson(data);
    } on ApiException catch (e) {
      if (e.statusCode == 401) {
        throw const AuthException(
          message: 'The email address or password is incorrect.',
          code: 'INVALID_CREDENTIALS',
          statusCode: 401,
        );
      }
      if (e.statusCode == 403) {
        throw AuthException(
          message: e.message,
          code: e.code,
          statusCode: 403,
        );
      }
      rethrow;
    }
  }

  /// Register volunteer account against `/auth/register`.
  Future<Map<String, dynamic>> register(RegistrationPayload payload) async {
    try {
      final response = await _client.post(
        '/auth/register',
        data: payload.toJson(),
      );
      return response.data as Map<String, dynamic>;
    } on ApiException catch (e) {
      if (e.statusCode == 409) {
        throw const ValidationException(
          message:
              'An account with this email or mobile number already exists.',
          code: 'CONFLICT',
        );
      }
      rethrow;
    }
  }

  /// Verify email address using token against `/auth/verify-email`.
  Future<Map<String, dynamic>> verifyEmail({
    required String token,
    String? email,
  }) async {
    try {
      final response = await _client.post(
        '/auth/verify-email',
        data: {
          'token': token.trim(),
          if (email != null && email.isNotEmpty)
            'email': email.trim().toLowerCase(),
        },
      );
      return response.data as Map<String, dynamic>;
    } on ApiException catch (e) {
      if (e.statusCode == 410) {
        throw const AuthException(
          message:
              'Email verification token has expired. Please request a new code.',
          code: 'TOKEN_EXPIRED',
          statusCode: 410,
        );
      }
      rethrow;
    }
  }

  /// Request password reset 6-digit OTP against `/auth/password-reset/request`.
  Future<void> requestPasswordReset({required String email}) async {
    try {
      await _client.post(
        '/auth/password-reset/request',
        data: {'email': email.trim().toLowerCase()},
      );
    } on ApiException catch (e) {
      // Return cleanly even if not found to prevent user enumeration
      if (e.statusCode == 404) return;
      rethrow;
    }
  }

  /// Confirm 6-digit OTP and set new password against `/auth/password-reset/confirm`.
  Future<void> confirmPasswordReset({
    required String email,
    required String otp,
    required String newPassword,
  }) async {
    try {
      await _client.post(
        '/auth/password-reset/confirm',
        data: {
          'email': email.trim().toLowerCase(),
          'otp': otp.trim(),
          'new_password': newPassword,
        },
      );
    } on ApiException catch (e) {
      if (e.statusCode == 400 || e.statusCode == 401) {
        throw const AuthException(
          message: 'Invalid or expired reset code. Please request a new code.',
          code: 'INVALID_RESET_CODE',
          statusCode: 400,
        );
      }
      rethrow;
    }
  }

  /// Retrieve active user identity and status from `/users/me`.
  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _client.get('/users/me');
    return response.data as Map<String, dynamic>;
  }

  /// Retrieve volunteer profile details from `/volunteers/me`.
  Future<Map<String, dynamic>> getVolunteerProfile() async {
    final response = await _client.get('/volunteers/me');
    return response.data as Map<String, dynamic>;
  }

  /// Revoke refresh token against `/auth/logout`.
  Future<void> logout({required String refreshToken}) async {
    try {
      await _client.post(
        '/auth/logout',
        data: {'refresh_token': refreshToken},
        options: Options(headers: {'X-CSRF-Token': 'mobile-client'}),
      );
    } catch (_) {
      // Ignored during local teardown
    }
  }
}
