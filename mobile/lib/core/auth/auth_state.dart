import '../models/user_session.dart';

enum AuthStatus {
  initial,
  loading,
  authenticated,
  unauthenticated,
  error,
}

/// Immutable state container for mobile authentication lifecycle.
class AuthState {
  final AuthStatus status;
  final UserSession? session;
  final String? errorMessage;
  final bool isFirstLaunch;

  const AuthState({
    required this.status,
    this.session,
    this.errorMessage,
    this.isFirstLaunch = false,
  });

  const AuthState.initial()
      : status = AuthStatus.initial,
        session = null,
        errorMessage = null,
        isFirstLaunch = false;

  const AuthState.loading({UserSession? previousSession})
      : status = AuthStatus.loading,
        session = previousSession,
        errorMessage = null,
        isFirstLaunch = false;

  const AuthState.authenticated(this.session, {this.isFirstLaunch = false})
      : status = AuthStatus.authenticated,
        errorMessage = null;

  const AuthState.unauthenticated()
      : status = AuthStatus.unauthenticated,
        session = null,
        errorMessage = null,
        isFirstLaunch = false;

  const AuthState.error(String message, {UserSession? previousSession})
      : status = AuthStatus.error,
        session = previousSession,
        errorMessage = message,
        isFirstLaunch = false;

  bool get isAuthenticated =>
      status == AuthStatus.authenticated && session != null;
  bool get isLoading => status == AuthStatus.loading;
  UserSession? get user => session;

  // Account Status Convenience Getters
  bool get isApproved => isAuthenticated && session!.isApproved;
  bool get isPendingVerification =>
      isAuthenticated && session!.isPendingVerification;
  bool get isPendingApproval => isAuthenticated && session!.isPendingApproval;
  bool get isRejected => isAuthenticated && session!.isRejected;
}
