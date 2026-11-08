import 'dart:async';
import 'package:dio/dio.dart';
import '../storage/token_storage.dart';

/// Thread-safe queued interceptor managing JWT Bearer injection and concurrent 401 token refresh.
class AuthInterceptor extends QueuedInterceptor {
  final Dio clientDio;
  final TokenStorage tokenStorage;
  final String apiBaseUrl;
  final void Function()? onSessionExpired;

  /// Dedicated Dio instance for token refresh to avoid circular interceptor triggers.
  late final Dio _refreshDio;

  AuthInterceptor({
    required this.clientDio,
    required this.tokenStorage,
    required this.apiBaseUrl,
    this.onSessionExpired,
    Dio? refreshDio,
  }) {
    _refreshDio = refreshDio ??
        Dio(
          BaseOptions(
            baseUrl: apiBaseUrl,
            connectTimeout: const Duration(seconds: 10),
            receiveTimeout: const Duration(seconds: 10),
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          ),
        );
  }

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // If the request doesn't explicitly override Authorization, attach stored token
    if (!options.headers.containsKey('Authorization')) {
      final token = await tokenStorage.getAccessToken();
      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final statusCode = err.response?.statusCode;
    final path = err.requestOptions.path;

    // Do not attempt refresh on auth endpoints (login, refresh, password reset)
    final isAuthEndpoint = path.contains('/auth/login') ||
        path.contains('/auth/refresh') ||
        path.contains('/auth/register');

    if (statusCode == 401 && !isAuthEndpoint) {
      final refreshToken = await tokenStorage.getRefreshToken();
      if (refreshToken == null || refreshToken.isEmpty) {
        await _handleRevocation(err, handler);
        return;
      }

      try {
        // Execute token refresh using isolated Dio client
        final response = await _refreshDio.post(
          '/auth/refresh',
          data: {'refresh_token': refreshToken},
        );

        if (response.statusCode == 200 && response.data != null) {
          final data = response.data is Map ? response.data as Map : {};
          final newAccessToken = data['access_token'] as String?;
          final newRefreshToken = data['refresh_token'] as String?;

          if (newAccessToken != null && newRefreshToken != null) {
            // Persist the newly rotated pair
            await tokenStorage.saveTokens(
              accessToken: newAccessToken,
              refreshToken: newRefreshToken,
            );

            // Re-execute original request with new access token
            final requestOptions = err.requestOptions;
            requestOptions.headers['Authorization'] = 'Bearer $newAccessToken';

            final retryResponse = await clientDio.fetch(requestOptions);
            return handler.resolve(retryResponse);
          }
        }

        // If response was not 200 or missing tokens
        await _handleRevocation(err, handler);
      } catch (_) {
        await _handleRevocation(err, handler);
      }
      return;
    }

    handler.next(err);
  }

  Future<void> _handleRevocation(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    await tokenStorage.clearTokens();
    onSessionExpired?.call();
    handler.reject(err);
  }
}
