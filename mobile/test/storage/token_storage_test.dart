import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:mocktail/mocktail.dart';
import 'package:maatram_mobile/core/storage/token_storage.dart';

class MockFlutterSecureStorage extends Mock implements FlutterSecureStorage {}

void main() {
  late MockFlutterSecureStorage mockStorage;
  late TokenStorage tokenStorage;

  setUp(() {
    mockStorage = MockFlutterSecureStorage();
    tokenStorage = TokenStorage(storage: mockStorage);
  });

  group('TokenStorage Tests', () {
    test('saveTokens persists both access and refresh tokens', () async {
      when(() => mockStorage.write(
            key: any(named: 'key'),
            value: any(named: 'value'),
          )).thenAnswer((_) async {});

      await tokenStorage.saveTokens(
        accessToken: 'sample_access_jwt',
        refreshToken: 'sample_refresh_jwt',
      );

      verify(() => mockStorage.write(
            key: 'maatram_jwt_access_token',
            value: 'sample_access_jwt',
          )).called(1);

      verify(() => mockStorage.write(
            key: 'maatram_jwt_refresh_token',
            value: 'sample_refresh_jwt',
          )).called(1);
    });

    test('getAccessToken returns stored token value', () async {
      when(() => mockStorage.read(key: 'maatram_jwt_access_token'))
          .thenAnswer((_) async => 'active_access_token');

      final result = await tokenStorage.getAccessToken();
      expect(result, equals('active_access_token'));
      verify(() => mockStorage.read(key: 'maatram_jwt_access_token')).called(1);
    });

    test('getRefreshToken returns stored refresh token value', () async {
      when(() => mockStorage.read(key: 'maatram_jwt_refresh_token'))
          .thenAnswer((_) async => 'active_refresh_token');

      final result = await tokenStorage.getRefreshToken();
      expect(result, equals('active_refresh_token'));
      verify(() => mockStorage.read(key: 'maatram_jwt_refresh_token')).called(1);
    });

    test('clearTokens deletes both keys from secure storage', () async {
      when(() => mockStorage.delete(key: any(named: 'key')))
          .thenAnswer((_) async {});

      await tokenStorage.clearTokens();

      verify(() => mockStorage.delete(key: 'maatram_jwt_access_token')).called(1);
      verify(() => mockStorage.delete(key: 'maatram_jwt_refresh_token')).called(1);
    });

    test('hasValidSession returns true when access token is present', () async {
      when(() => mockStorage.read(key: 'maatram_jwt_access_token'))
          .thenAnswer((_) async => 'valid_token');

      final isValid = await tokenStorage.hasValidSession();
      expect(isValid, isTrue);
    });

    test('hasValidSession returns false when access token is absent or null', () async {
      when(() => mockStorage.read(key: 'maatram_jwt_access_token'))
          .thenAnswer((_) async => null);

      final isValid = await tokenStorage.hasValidSession();
      expect(isValid, isFalse);
    });
  });
}
