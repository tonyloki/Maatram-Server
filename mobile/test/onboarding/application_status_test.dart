import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/features/onboarding/presentation/pending_approval_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/pending_verification_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/rejected_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/welcome_screen.dart';

class MockStatusAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockStatusAuthController(super.initial);

  bool logoutCalled = false;
  bool refreshCalled = false;
  bool welcomeCompleted = false;

  @override
  Future<void> checkInitialSession() async {}

  @override
  Future<void> logout() async {
    logoutCalled = true;
    state = const AuthState.unauthenticated();
  }

  @override
  Future<void> refreshSession() async {
    refreshCalled = true;
  }

  @override
  Future<void> completeFirstLaunchWelcome() async {
    welcomeCompleted = true;
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

Widget createTestApp(Widget child) {
  final router = GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/', builder: (context, state) => child),
      GoRoute(
          path: '/login',
          builder: (context, state) =>
              const Scaffold(body: Text('Login Screen'))),
      GoRoute(
          path: '/home',
          builder: (context, state) =>
              const Scaffold(body: Text('Home Screen'))),
      GoRoute(
          path: '/verify-email',
          builder: (context, state) =>
              const Scaffold(body: Text('Verify Email'))),
    ],
  );
  return MaterialApp.router(routerConfig: router);
}

void main() {
  group('Dedicated Application Status & Onboarding Experience Tests', () {
    testWidgets('PendingVerificationScreen displays exact guidance and email',
        (tester) async {
      const session = UserSession(
        userId: 'usr_1',
        email: 'volunteer@maatram.org',
        role: 'VOLUNTEER',
        status: 'PENDING_VERIFICATION',
        accessToken: '',
        refreshToken: '',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) =>
                MockStatusAuthController(AuthState.authenticated(session))),
          ],
          child: createTestApp(const PendingVerificationScreen()),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Email Verification Pending'), findsOneWidget);
      expect(find.text('Enter Verification Code'), findsOneWidget);
      expect(find.text('Sign Out'), findsOneWidget);
    });

    testWidgets(
        'PendingApprovalScreen displays exact review copy and check status CTA',
        (tester) async {
      const session = UserSession(
        userId: 'usr_2',
        email: 'volunteer@maatram.org',
        role: 'VOLUNTEER',
        status: 'PENDING_ADMIN_APPROVAL',
        accessToken: '',
        refreshToken: '',
      );
      final mock = MockStatusAuthController(AuthState.authenticated(session));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) => mock),
          ],
          child: createTestApp(const PendingApprovalScreen()),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Pending Under Review'), findsOneWidget);

      await tester.tap(find.text('Check Approval Status'));
      await tester.pumpAndSettle();
      expect(mock.refreshCalled, isTrue);
    });

    testWidgets(
        'WelcomeScreen displays exact welcome copy and onboarding points',
        (tester) async {
      const session = UserSession(
        userId: 'usr_3',
        email: 'volunteer@maatram.org',
        role: 'VOLUNTEER',
        status: 'APPROVED',
        accessToken: '',
        refreshToken: '',
        firstName: 'Dharani',
      );
      final mock = MockStatusAuthController(
          AuthState.authenticated(session, isFirstLaunch: true));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) => mock),
          ],
          child: createTestApp(const WelcomeScreen()),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Welcome to\nMaatram!'), findsOneWidget);
      expect(find.text('Go to Home'), findsOneWidget);

      await tester.tap(find.text('Go to Home'));
      await tester.pumpAndSettle();
      expect(mock.welcomeCompleted, isTrue);
    });

    testWidgets('RejectedScreen displays respectful copy and support info',
        (tester) async {
      const session = UserSession(
        userId: 'usr_4',
        email: 'volunteer@maatram.org',
        role: 'VOLUNTEER',
        status: 'REJECTED',
        accessToken: '',
        refreshToken: '',
      );
      final mock = MockStatusAuthController(AuthState.authenticated(session));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) => mock),
          ],
          child: createTestApp(const RejectedScreen()),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Application Update'), findsOneWidget);
      expect(find.text('Contact Support'), findsOneWidget);
      expect(find.text('Sign Out'), findsOneWidget);

      await tester.tap(find.text('Sign Out'));
      await tester.pumpAndSettle();
      expect(mock.logoutCalled, isTrue);
    });
  });
}
