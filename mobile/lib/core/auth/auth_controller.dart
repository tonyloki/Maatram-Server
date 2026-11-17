import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/auth/data/auth_repository.dart';
import '../config/env_config.dart';
import '../errors/app_exception.dart';
import '../models/registration_payload.dart';
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

final Provider<AuthRepository> authRepositoryProvider =
    Provider<AuthRepository>((ref) {
  final client = ref.watch(apiClientProvider);
  return AuthRepository(client: client);
});

final StateNotifierProvider<AuthController, AuthState> authControllerProvider =
    StateNotifierProvider<AuthController, AuthState>((ref) {
  final storage = ref.watch(tokenStorageProvider);
  final repository = ref.watch(authRepositoryProvider);
  return AuthController(storage: storage, repository: repository);
});

/// Centralized state controller managing session restoration, login, registration,
/// verification, password recovery, and secure token lifecycle.
class AuthController extends StateNotifier<AuthState> {
  final TokenStorage _storage;
  final AuthRepository _repository;

  AuthController({
    required TokenStorage storage,
    required AuthRepository repository,
  })  : _storage = storage,
        _repository = repository,
        super(const AuthState.initial()) {
    checkInitialSession();
  }

  /// Check whether credentials exist in secure hardware storage on app launch.
  Future<void> checkInitialSession() async {
    state = const AuthState.loading();
    try {
      final hasSession = await _storage.hasValidSession();
      if (!hasSession) {
        state = const AuthState.unauthenticated();
        return;
      }

      // Read locally persisted user session
      final cachedSession = await _storage.getUserSession();
      final accessToken = await _storage.getAccessToken() ?? '';
      final refreshToken = await _storage.getRefreshToken() ?? '';

      UserSession activeSession = cachedSession ??
          UserSession(
            userId: 'restored',
            email: '',
            role: 'VOLUNTEER',
            status: 'APPROVED',
            accessToken: accessToken,
            refreshToken: refreshToken,
          );

      // Validate session with backend /users/me
      try {
        final userData = await _repository.getCurrentUser();
        activeSession = activeSession.copyWith(
          userId: userData['id']?.toString() ?? activeSession.userId,
          email: userData['email']?.toString() ?? activeSession.email,
          role: userData['role']?.toString() ?? activeSession.role,
          status: userData['status']?.toString() ?? activeSession.status,
        );
        await _storage.saveUserSession(activeSession);
      } on NetworkException {
        // Offline: trust hardware-persisted session
      } on AuthException {
        // Token expired/revoked and could not be refreshed
        await _storage.clearTokens();
        state = const AuthState.unauthenticated();
        return;
      } catch (_) {
        // Fallback to local session on unexpected error
      }

      const isFirstTime = false;
      state =
          AuthState.authenticated(activeSession, isFirstLaunch: isFirstTime);
    } catch (_) {
      state = const AuthState.unauthenticated();
    }
  }

  /// Authenticate credentials against canonical `/auth/login`.
  Future<bool> login({
    required String email,
    required String password,
  }) async {
    state = const AuthState.loading();
    try {
      final session = await _repository.login(
        email: email,
        password: password,
      );

      await _storage.saveTokens(
        accessToken: session.accessToken,
        refreshToken: session.refreshToken,
      );
      await _storage.saveUserSession(session);

      const isFirstTime = false;
      state = AuthState.authenticated(session, isFirstLaunch: isFirstTime);
      return true;
    } on AuthException catch (e) {
      state = AuthState.error(e.message);
      return false;
    } on NetworkException {
      state = const AuthState.error(
          'You’re offline. Check your internet connection and try again.');
      return false;
    } catch (e, st) {
      // Diagnostic log
      // ignore: avoid_print
      print('LOGIN FAILURE CAUSE: $e\n$st');
      state = const AuthState.error(
          'We couldn’t complete your request right now. Please try again.');
      return false;
    }
  }

  /// Register volunteer account against `/auth/register`.
  Future<bool> register(RegistrationPayload payload) async {
    state = const AuthState.loading();
    try {
      final response = await _repository.register(payload);
      final userId = response['user_id']?.toString() ?? '';
      final email = response['email']?.toString() ?? payload.email;
      final status = response['status']?.toString() ?? 'PENDING_VERIFICATION';

      // Temporary session for verification workflow
      final session = UserSession(
        userId: userId,
        email: email,
        role: 'VOLUNTEER',
        status: status,
        accessToken: '',
        refreshToken: '',
        firstName: payload.firstName,
        lastName: payload.lastName,
        category: payload.category,
      );

      await _storage.saveUserSession(session);
      state = AuthState.authenticated(session);
      return true;
    } on ValidationException catch (e) {
      state = AuthState.error(e.message);
      return false;
    } on NetworkException {
      state = const AuthState.error(
          'You’re offline. Check your internet connection and try again.');
      return false;
    } catch (_) {
      state = const AuthState.error(
          'We couldn’t complete your request right now. Please try again.');
      return false;
    }
  }

  /// Confirm email address token against `/auth/verify-email`.
  Future<bool> verifyEmail({
    required String token,
    String? email,
  }) async {
    state = AuthState.loading(previousSession: state.session);
    try {
      final currentEmail = email ?? state.session?.email;
      await _repository.verifyEmail(token: token, email: currentEmail);

      if (state.session != null) {
        final updatedSession =
            state.session!.copyWith(status: 'PENDING_APPROVAL');
        await _storage.saveUserSession(updatedSession);
        state = AuthState.authenticated(updatedSession);
      } else {
        state = const AuthState.unauthenticated();
      }
      return true;
    } on AuthException catch (e) {
      state = AuthState.error(e.message, previousSession: state.session);
      return false;
    } on NetworkException {
      state = AuthState.error(
        'You’re offline. Check your internet connection and try again.',
        previousSession: state.session,
      );
      return false;
    } catch (_) {
      state = AuthState.error(
        'We couldn’t complete your request right now. Please try again.',
        previousSession: state.session,
      );
      return false;
    }
  }

  /// Refresh session status from backend `/users/me`.
  Future<void> refreshSession() async {
    if (state.session == null) return;
    try {
      final userData = await _repository.getCurrentUser();
      final updated = state.session!.copyWith(
        status: userData['status']?.toString() ?? state.session!.status,
      );
      await _storage.saveUserSession(updated);

      final isFirstTime =
          !(await _storage.isFirstLaunchCompleted()) && updated.isApproved;
      state = AuthState.authenticated(updated, isFirstLaunch: isFirstTime);
    } catch (_) {
      // Ignored during status polling
    }
  }

  /// Request password reset 6-digit OTP against `/auth/password-reset/request`.
  Future<bool> requestPasswordReset({required String email}) async {
    state = const AuthState.loading();
    try {
      await _repository.requestPasswordReset(email: email);
      state = const AuthState.unauthenticated();
      return true;
    } on NetworkException {
      state = const AuthState.error(
          'You’re offline. Check your internet connection and try again.');
      return false;
    } catch (_) {
      state = const AuthState.error(
          'We couldn’t complete your request right now. Please try again.');
      return false;
    }
  }

  /// Confirm 6-digit OTP and reset password against `/auth/password-reset/confirm`.
  Future<bool> confirmPasswordReset({
    required String email,
    required String otp,
    required String newPassword,
  }) async {
    state = const AuthState.loading();
    try {
      await _repository.confirmPasswordReset(
        email: email,
        otp: otp,
        newPassword: newPassword,
      );
      state = const AuthState.unauthenticated();
      return true;
    } on AuthException catch (e) {
      state = AuthState.error(e.message);
      return false;
    } on NetworkException {
      state = const AuthState.error(
          'You’re offline. Check your internet connection and try again.');
      return false;
    } catch (e, st) {
      // Diagnostic log
      // ignore: avoid_print
      print('LOGIN FAILURE CAUSE: $e\n$st');
      state = const AuthState.error(
          'We couldn’t complete your request right now. Please try again.');
      return false;
    }
  }

  /// Complete first-time approved welcome flow.
  Future<void> completeFirstLaunchWelcome() async {
    await _storage.setFirstLaunchCompleted(true);
    if (state.session != null) {
      state = AuthState.authenticated(state.session!, isFirstLaunch: false);
    }
  }

  /// Cleanly logout, revoke tokens on backend, and clear hardware secure storage.
  Future<void> logout() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken != null && refreshToken.isNotEmpty) {
        await _repository.logout(refreshToken: refreshToken);
      }
    } catch (_) {
      // Wipe hardware state regardless
    } finally {
      await _storage.clearTokens();
      state = const AuthState.unauthenticated();
    }
  }

  /// Callback from AuthInterceptor when refresh token is invalid or expired.
  void handleSessionExpired() {
    _storage.clearTokens();
    state = const AuthState.unauthenticated();
  }
}
