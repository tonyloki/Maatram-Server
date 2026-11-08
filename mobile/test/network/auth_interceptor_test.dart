import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:maatram_mobile/core/network/auth_interceptor.dart';
import 'package:maatram_mobile/core/storage/token_storage.dart';

class MockDio extends Mock implements Dio {}
class MockTokenStorage extends Mock implements TokenStorage {}
class MockRequestInterceptorHandler extends Mock implements RequestInterceptorHandler {}
class MockErrorInterceptorHandler extends Mock implements ErrorInterceptorHandler {}

void main() {
  late MockDio mockClientDio;
  late MockDio mockRefreshDio;
  late MockTokenStorage mockTokenStorage;
  late AuthInterceptor authInterceptor;
  bool sessionExpiredCalled = false;

  setUpAll(() {
    registerFallbackValue(RequestOptions(path: '/'));
    registerFallbackValue(Response<dynamic>(requestOptions: RequestOptions(path: '/')));
    registerFallbackValue(DioException(requestOptions: RequestOptions(path: '/')));
  });

  setUp(() {
    mockClientDio = MockDio();
    mockRefreshDio = MockDio();
    mockTokenStorage = MockTokenStorage();
    sessionExpiredCalled = false;

    authInterceptor = AuthInterceptor(
      clientDio: mockClientDio,
      tokenStorage: mockTokenStorage,
      apiBaseUrl: 'http://test:8000/api/v1',
      refreshDio: mockRefreshDio,
      onSessionExpired: () {
        sessionExpiredCalled = true;
      },
    );
  });

  group('AuthInterceptor Tests', () {
    test('onRequest appends Authorization Bearer header when token exists', () async {
      when(() => mockTokenStorage.getAccessToken())
          .thenAnswer((_) async => 'mocked_jwt_access');

      final options = RequestOptions(path: '/events');
      final handler = MockRequestInterceptorHandler();
      when(() => handler.next(any())).thenReturn(null);

      await authInterceptor.onRequest(options, handler);

      expect(options.headers['Authorization'], equals('Bearer mocked_jwt_access'));
      verify(() => handler.next(options)).called(1);
    });

    test('onRequest preserves custom Authorization header if already present', () async {
      when(() => mockTokenStorage.getAccessToken())
          .thenAnswer((_) async => 'mocked_jwt_access');

      final options = RequestOptions(
        path: '/events',
        headers: {'Authorization': 'CustomExistingToken'},
      );
      final handler = MockRequestInterceptorHandler();
      when(() => handler.next(any())).thenReturn(null);

      await authInterceptor.onRequest(options, handler);

      expect(options.headers['Authorization'], equals('CustomExistingToken'));
      verify(() => handler.next(options)).called(1);
    });

    test('onError on 401 performs token refresh and retries original request', () async {
      when(() => mockTokenStorage.getRefreshToken())
          .thenAnswer((_) async => 'valid_refresh_token');
      when(() => mockTokenStorage.saveTokens(
            accessToken: any(named: 'accessToken'),
            refreshToken: any(named: 'refreshToken'),
          )).thenAnswer((_) async {});

      final requestOptions = RequestOptions(path: '/events');
      final response = Response(
        requestOptions: requestOptions,
        statusCode: 401,
      );
      final dioException = DioException(
        requestOptions: requestOptions,
        response: response,
      );

      // Mock refresh response
      when(() => mockRefreshDio.post(
            '/auth/refresh',
            data: {'refresh_token': 'valid_refresh_token'},
          )).thenAnswer((_) async => Response(
            requestOptions: RequestOptions(path: '/auth/refresh'),
            statusCode: 200,
            data: {
              'access_token': 'new_rotated_access',
              'refresh_token': 'new_rotated_refresh',
            },
          ));

      // Mock clientDio.fetch retry
      final retriedResponse = Response(
        requestOptions: requestOptions,
        statusCode: 200,
        data: {'items': []},
      );
      when(() => mockClientDio.fetch(any()))
          .thenAnswer((_) async => retriedResponse);

      final handler = MockErrorInterceptorHandler();
      when(() => handler.resolve(any())).thenReturn(null);

      await authInterceptor.onError(dioException, handler);

      verify(() => mockRefreshDio.post(
            '/auth/refresh',
            data: {'refresh_token': 'valid_refresh_token'},
          )).called(1);

      verify(() => mockTokenStorage.saveTokens(
            accessToken: 'new_rotated_access',
            refreshToken: 'new_rotated_refresh',
          )).called(1);

      verify(() => mockClientDio.fetch(any())).called(1);
      verify(() => handler.resolve(retriedResponse)).called(1);
      expect(sessionExpiredCalled, isFalse);
    });

    test('onError on 401 with missing refresh token clears storage and invokes onSessionExpired', () async {
      when(() => mockTokenStorage.getRefreshToken())
          .thenAnswer((_) async => null);
      when(() => mockTokenStorage.clearTokens())
          .thenAnswer((_) async {});

      final requestOptions = RequestOptions(path: '/events');
      final response = Response(
        requestOptions: requestOptions,
        statusCode: 401,
      );
      final dioException = DioException(
        requestOptions: requestOptions,
        response: response,
      );

      final handler = MockErrorInterceptorHandler();
      when(() => handler.reject(any())).thenReturn(null);

      await authInterceptor.onError(dioException, handler);

      verify(() => mockTokenStorage.clearTokens()).called(1);
      verify(() => handler.reject(dioException)).called(1);
      expect(sessionExpiredCalled, isTrue);
    });

    test('onError on 401 with refresh failure clears storage and invokes onSessionExpired', () async {
      when(() => mockTokenStorage.getRefreshToken())
          .thenAnswer((_) async => 'expired_refresh_token');
      when(() => mockTokenStorage.clearTokens())
          .thenAnswer((_) async {});

      final requestOptions = RequestOptions(path: '/events');
      final response = Response(
        requestOptions: requestOptions,
        statusCode: 401,
      );
      final dioException = DioException(
        requestOptions: requestOptions,
        response: response,
      );

      // Mock refresh failure (e.g. 401 from backend indicating revoked token)
      when(() => mockRefreshDio.post(
            '/auth/refresh',
            data: {'refresh_token': 'expired_refresh_token'},
          )).thenThrow(DioException(
            requestOptions: RequestOptions(path: '/auth/refresh'),
            response: Response(
              requestOptions: RequestOptions(path: '/auth/refresh'),
              statusCode: 401,
            ),
          ));

      final handler = MockErrorInterceptorHandler();
      when(() => handler.reject(any())).thenReturn(null);

      await authInterceptor.onError(dioException, handler);

      verify(() => mockTokenStorage.clearTokens()).called(1);
      verify(() => handler.reject(dioException)).called(1);
      expect(sessionExpiredCalled, isTrue);
    });
  });
}
