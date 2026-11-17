import 'package:dio/dio.dart';
import '../network/api_client.dart';

/// Base exception hierarchy for typed error handling across the mobile application.
sealed class AppException implements Exception {
  final String message;
  final String? code;
  final int? statusCode;

  const AppException({
    required this.message,
    this.code,
    this.statusCode,
  });

  @override
  String toString() =>
      '$runtimeType(message: $message, code: $code, status: $statusCode)';
}

/// Network disconnection or timeout
class NetworkException extends AppException {
  const NetworkException({
    super.message =
        'Network connection unavailable. Please check your internet.',
    super.code = 'NETWORK_ERROR',
  });
}

/// Authentication failure (401)
class UnauthorizedException extends AppException {
  const UnauthorizedException({
    super.message = 'Session expired. Please log in again.',
    super.code = 'UNAUTHORIZED',
    super.statusCode = 401,
  });
}

/// Alias for UnauthorizedException for auth flows
typedef AuthException = UnauthorizedException;

/// Insufficient permission (403)
class ForbiddenException extends AppException {
  const ForbiddenException({
    super.message = 'You do not have permission to access this resource.',
    super.code = 'FORBIDDEN',
    super.statusCode = 403,
  });
}

/// Resource not found (404)
class NotFoundException extends AppException {
  const NotFoundException({
    super.message = 'The requested resource was not found.',
    super.code = 'NOT_FOUND',
    super.statusCode = 404,
  });
}

/// Business validation or domain exception
class ValidationException extends AppException {
  final dynamic validationErrors;

  const ValidationException({
    required super.message,
    super.code = 'VALIDATION_ERROR',
    super.statusCode = 422,
    this.validationErrors,
  });
}

/// Server side internal error (500+)
class ServerException extends AppException {
  const ServerException({
    super.message = 'Internal server error occurred. Please try again later.',
    super.code = 'SERVER_ERROR',
    super.statusCode = 500,
  });
}

/// Unknown or unexpected client exception
class UnexpectedException extends AppException {
  const UnexpectedException({
    required super.message,
    super.code = 'UNEXPECTED_ERROR',
  });
}

/// Maps raw exceptions, DioExceptions, or ApiExceptions into typed AppExceptions.
abstract final class ErrorHandler {
  static AppException map(dynamic error) {
    if (error is AppException) return error;

    if (error is DioException) {
      if (error.type == DioExceptionType.connectionTimeout ||
          error.type == DioExceptionType.sendTimeout ||
          error.type == DioExceptionType.receiveTimeout ||
          error.type == DioExceptionType.connectionError) {
        return NetworkException(
            message: error.message ?? 'Network connection unavailable.');
      }

      final statusCode = error.response?.statusCode;
      final responseData = error.response?.data;
      String message = error.message ?? 'An error occurred';
      String? code;
      dynamic details;

      if (responseData is Map<String, dynamic>) {
        final detail = responseData['detail'];
        if (detail is String) {
          message = detail;
        } else if (detail != null) {
          details = detail;
          message = detail.toString();
        }
        code = responseData['code'] as String?;
      }

      if (statusCode == 401) {
        return UnauthorizedException(message: message, code: code);
      }
      if (statusCode == 403) {
        return ForbiddenException(message: message, code: code);
      }
      if (statusCode == 404) {
        return NotFoundException(message: message, code: code);
      }
      if (statusCode == 422 || statusCode == 400) {
        return ValidationException(
          message: message,
          code: code ?? 'VALIDATION_ERROR',
          validationErrors: details,
        );
      }
      if (statusCode != null && statusCode >= 500) {
        return ServerException(message: message, code: code);
      }

      return UnexpectedException(message: message, code: code);
    }

    if (error is ApiException) {
      final status = error.statusCode;
      if (status == 401) {
        return UnauthorizedException(message: error.message, code: error.code);
      }
      if (status == 403) {
        return ForbiddenException(message: error.message, code: error.code);
      }
      if (status == 404) {
        return NotFoundException(message: error.message, code: error.code);
      }
      if (status == 422 || status == 400) {
        return ValidationException(
          message: error.message,
          code: error.code,
          validationErrors: error.details,
        );
      }
      if (status != null && status >= 500) {
        return ServerException(message: error.message, code: error.code);
      }
      return UnexpectedException(message: error.message, code: error.code);
    }

    return UnexpectedException(
      message: error?.toString() ?? 'An unexpected error occurred.',
    );
  }
}
