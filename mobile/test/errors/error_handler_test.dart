import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/errors/app_exception.dart';

void main() {
  group('ErrorHandler and Typed AppException mapping', () {
    test('maps 401 response to UnauthorizedException', () {
      final dioError = DioException(
        requestOptions: RequestOptions(path: '/api/v1/auth/me'),
        response: Response(
          requestOptions: RequestOptions(path: '/api/v1/auth/me'),
          statusCode: 401,
          data: {'detail': 'Invalid access token'},
        ),
        type: DioExceptionType.badResponse,
      );

      final exception = ErrorHandler.map(dioError);
      expect(exception, isA<UnauthorizedException>());
      expect(exception.message, contains('Invalid access token'));
    });

    test('maps 403 response to ForbiddenException', () {
      final dioError = DioException(
        requestOptions: RequestOptions(path: '/api/v1/admin/review'),
        response: Response(
          requestOptions: RequestOptions(path: '/api/v1/admin/review'),
          statusCode: 403,
          data: {'detail': 'Insufficient permissions'},
        ),
        type: DioExceptionType.badResponse,
      );

      final exception = ErrorHandler.map(dioError);
      expect(exception, isA<ForbiddenException>());
    });

    test('maps 404 response to NotFoundException', () {
      final dioError = DioException(
        requestOptions: RequestOptions(path: '/api/v1/events/123'),
        response: Response(
          requestOptions: RequestOptions(path: '/api/v1/events/123'),
          statusCode: 404,
          data: {'detail': 'Event not found'},
        ),
        type: DioExceptionType.badResponse,
      );

      final exception = ErrorHandler.map(dioError);
      expect(exception, isA<NotFoundException>());
    });

    test('maps 422 response to ValidationException', () {
      final dioError = DioException(
        requestOptions: RequestOptions(path: '/api/v1/volunteers/apply'),
        response: Response(
          requestOptions: RequestOptions(path: '/api/v1/volunteers/apply'),
          statusCode: 422,
          data: {
            'detail': [
              {
                'loc': ['body', 'email'],
                'msg': 'value is not a valid email'
              }
            ]
          },
        ),
        type: DioExceptionType.badResponse,
      );

      final exception = ErrorHandler.map(dioError);
      expect(exception, isA<ValidationException>());
    });

    test('maps 500 response to ServerException', () {
      final dioError = DioException(
        requestOptions: RequestOptions(path: '/api/v1/gamification/points'),
        response: Response(
          requestOptions: RequestOptions(path: '/api/v1/gamification/points'),
          statusCode: 500,
          data: {'detail': 'Internal database connection pool timeout'},
        ),
        type: DioExceptionType.badResponse,
      );

      final exception = ErrorHandler.map(dioError);
      expect(exception, isA<ServerException>());
    });

    test('maps connection timeout to NetworkException', () {
      final dioError = DioException(
        requestOptions: RequestOptions(path: '/api/v1/events'),
        type: DioExceptionType.connectionTimeout,
        message: 'Connection timed out',
      );

      final exception = ErrorHandler.map(dioError);
      expect(exception, isA<NetworkException>());
    });
  });
}
