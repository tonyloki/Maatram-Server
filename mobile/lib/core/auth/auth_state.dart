import '../models/user_session.dart';

enum AuthStatus { initial, loading, authenticated, unauthenticated, error }

/// Immutable state container for mobile authentication lifecycle.
class AuthState {
  final AuthStatus status;
  final UserSession? session;
  final String? errorMessage;

  const AuthState({
    required this.status,
    this.session,
    this.errorMessage,
  });

  const AuthState.initial()
      : status = AuthStatus.initial,
        session = null,
        errorMessage = null;

  const AuthState.loading()
      : status = AuthStatus.loading,
        session = null,
        errorMessage = null;

  const AuthState.authenticated(this.session)
      : status = AuthStatus.authenticated,
        errorMessage = null;

  const AuthState.unauthenticated()
      : status = AuthStatus.unauthenticated,
        session = null,
        errorMessage = null;

  const AuthState.error(String message)
      : status = AuthStatus.error,
        session = null,
        errorMessage = message;

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading => status == AuthStatus.loading;
}
