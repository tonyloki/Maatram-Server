import 'package:dio/dio.dart';
import '../config/env_config.dart';
import '../storage/token_storage.dart';
import 'auth_interceptor.dart';

/// Exception thrown when API returns a canonical error payload.
class ApiException implements Exception {
  final int? statusCode;
  final String code;
  final String message;
  final Map<String, dynamic>? details;

  const ApiException({
    this.statusCode,
    required this.code,
    required this.message,
    this.details,
  });

  @override
  String toString() => 'ApiException(status: $statusCode, code: $code, message: $message)';
}

/// Central HTTP API Client configuring Dio, interceptors, and error handling for Maatram Mobile.
class ApiClient {
  late final Dio dio;
  final TokenStorage tokenStorage;
  final EnvConfig envConfig;
  final void Function()? onSessionExpired;

  ApiClient({
    TokenStorage? tokenStorage,
    EnvConfig? envConfig,
    this.onSessionExpired,
    Dio? customDio,
  })  : tokenStorage = tokenStorage ?? TokenStorage(),
        envConfig = envConfig ?? EnvConfig.development() {
    dio = customDio ??
        Dio(
          BaseOptions(
            baseUrl: this.envConfig.apiBaseUrl,
            connectTimeout: this.envConfig.connectTimeout,
            receiveTimeout: this.envConfig.receiveTimeout,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          ),
        );

    // Register authentication interceptor with queueing
    dio.interceptors.add(
      AuthInterceptor(
        clientDio: dio,
        tokenStorage: this.tokenStorage,
        apiBaseUrl: this.envConfig.apiBaseUrl,
        onSessionExpired: onSessionExpired,
      ),
    );
  }

  /// Execute GET request
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _parseDioError(e);
    }
  }

  /// Execute POST request
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _parseDioError(e);
    }
  }

  /// Execute PATCH request
  Future<Response<T>> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await dio.patch<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _parseDioError(e);
    }
  }

  /// Execute DELETE request
  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await dio.delete<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _parseDioError(e);
    }
  }

  ApiException _parseDioError(DioException error) {
    final response = error.response;
    if (response?.data is Map) {
      final data = response!.data as Map;
      if (data.containsKey('error') && data['error'] is Map) {
        final err = data['error'] as Map;
        return ApiException(
          statusCode: response.statusCode,
          code: err['code']?.toString() ?? 'API_ERROR',
          message: err['message']?.toString() ?? 'An unexpected error occurred.',
          details: err['details'] is Map ? Map<String, dynamic>.from(err['details'] as Map) : null,
        );
      }
    }

    return ApiException(
      statusCode: response?.statusCode,
      code: 'NETWORK_ERROR',
      message: error.message ?? 'Network connection error.',
    );
  }
}
