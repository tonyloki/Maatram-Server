import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/env_config.dart';
import '../models/user_session.dart';
import '../network/api_client.dart';
import '../storage/token_storage.dart';
import 'auth_state.dart';

final envConfigProvider = Provider<EnvConfig>((ref) => EnvConfig.development());
final tokenStorageProvider = Provider<TokenStorage>((ref) => TokenStorage());

final Provider<ApiClient> apiClientProvider = Provider<ApiClient>((ref) {
  final storage = ref.watch(tokenStorageProvider);
  final config = ref.watch(envConfigProvider);
  return ApiClient(
    tokenStorage: storage,
    envConfig: config,
    onSessionExpired: () {
      ref.read(authControllerProvider.notifier).handleSessionExpired();
    },
  );
});

final StateNotifierProvider<AuthController, AuthState> authControllerProvider =
    StateNotifierProvider<AuthController, AuthState>((ref) {
  final storage = ref.watch(tokenStorageProvider);
  final client = ref.watch(apiClientProvider);
  return AuthController(storage: storage, client: client);
});

/// Centralized state controller managing session restoration, login, logout, and token revocation.
class AuthController extends StateNotifier<AuthState> {
  final TokenStorage _storage;
  final ApiClient _client;

  AuthController({
    required TokenStorage storage,
    required ApiClient client,
  })  : _storage = storage,
        _client = client,
        super(const AuthState.initial()) {
    checkInitialSession();
  }

  /// Check whether credentials exist in secure hardware storage on app launch.
  Future<void> checkInitialSession() async {
    state = const AuthState.loading();
    try {
      final hasSession = await _storage.hasValidSession();
      if (hasSession) {
        // Read access token to construct initial restored session
        final accessToken = await _storage.getAccessToken() ?? '';
        final refreshToken = await _storage.getRefreshToken() ?? '';

        final session = UserSession(
          userId: 'restored-session',
          email: '',
          role: 'VOLUNTEER',
          status: 'APPROVED',
          accessToken: accessToken,
          refreshToken: refreshToken,
        );
        state = AuthState.authenticated(session);
      } else {
        state = const AuthState.unauthenticated();
      }
    } catch (_) {
      state = const AuthState.unauthenticated();
    }
  }

  /// Execute login against the canonical FastAPI auth endpoint.
  Future<bool> login({required String email, required String password}) async {
    state = const AuthState.loading();
    try {
      final response = await _client.post(
        '/auth/login',
        data: {
          'email': email.trim().toLowerCase(),
          'password': password,
          'client_type': 'MOBILE',
        },
      );

      if (response.statusCode == 200 && response.data is Map) {
        final data = response.data as Map<String, dynamic>;
        final session = UserSession.fromJson(data);

        await _storage.saveTokens(
          accessToken: session.accessToken,
          refreshToken: session.refreshToken,
        );

        state = AuthState.authenticated(session);
        return true;
      }

      state = const AuthState.error('Invalid credentials.');
      return false;
    } catch (e) {
      state = AuthState.error(e.toString());
      return false;
    }
  }

  /// Cleanly logout, revoke tokens on backend, and clear hardware secure storage.
  Future<void> logout() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken != null && refreshToken.isNotEmpty) {
        await _client.post(
          '/auth/logout',
          data: {'refresh_token': refreshToken},
        );
      }
    } catch (_) {
      // Proceed with local wipe even if server revocation times out
    } finally {
      await _storage.clearTokens();
      state = const AuthState.unauthenticated();
    }
  }

  /// Callback from AuthInterceptor when refresh token is invalid or expired.
  void handleSessionExpired() {
    state = const AuthState.unauthenticated();
  }
}
