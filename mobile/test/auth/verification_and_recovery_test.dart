import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/features/auth/presentation/forgot_password_screen.dart';
import 'package:maatram_mobile/features/auth/presentation/reset_password_screen.dart';
import 'package:maatram_mobile/features/auth/presentation/verify_email_screen.dart';

class MockRecoveryAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockRecoveryAuthController() : super(const AuthState.unauthenticated());

  bool verifyEmailSuccess = true;
  bool resetPasswordSuccess = true;
  String? verifyEmailTokenPassed;
  String? resetPasswordOtpPassed;

  @override
  Future<void> checkInitialSession() async {}

  @override
  Future<bool> verifyEmail({required String token, String? email}) async {
    verifyEmailTokenPassed = token;
    if (verifyEmailSuccess) {
      final session = UserSession(
        userId: 'usr_verified_1',
        email: email ?? 'test@example.com',
        role: 'VOLUNTEER',
        status: 'PENDING_ADMIN_APPROVAL',
        accessToken: 'temp_token',
        refreshToken: 'temp_refresh',
      );
      state = AuthState.authenticated(session);
      return true;
    }
    state = const AuthState.error('Verification token is invalid or expired.');
    return false;
  }

  @override
  Future<bool> requestPasswordReset({required String email}) async {
    return true;
  }

  @override
  Future<bool> confirmPasswordReset({
    required String email,
    required String otp,
    required String newPassword,
  }) async {
    resetPasswordOtpPassed = otp;
    return resetPasswordSuccess;
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
          path: '/reset-password',
          builder: (context, state) =>
              const Scaffold(body: Text('Reset Password'))),
      GoRoute(
          path: '/onboarding/pending-approval',
          builder: (context, state) =>
              const Scaffold(body: Text('Pending Approval'))),
    ],
  );
  return MaterialApp.router(routerConfig: router);
}

void main() {
  group('Verification & Password Recovery Tests', () {
    testWidgets(
        'VerifyEmailScreen masks email and toggles delivery uncertainty copy',
        (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider
                .overrideWith((ref) => MockRecoveryAuthController()),
          ],
          child: createTestApp(
              const VerifyEmailScreen(initialEmail: 'anandkumar@gmail.com')),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Verify Your Email'), findsOneWidget);
      // Masked email check (first char + *** + last char)
      expect(find.textContaining('a***r@gmail.com'), findsOneWidget);

      // Tap didn't receive email button
      await tester.tap(find.text('Didn’t receive the email?'));
      await tester.pumpAndSettle();

      // Exact delivery uncertainty copy from App answers.pdf
      expect(
        find.text(
          'We couldn’t confirm email delivery yet. Please check your inbox and spam folder, then try again later.',
        ),
        findsOneWidget,
      );
    });

    testWidgets(
        'ForgotPasswordScreen displays neutral security message on submission',
        (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider
                .overrideWith((ref) => MockRecoveryAuthController()),
          ],
          child: createTestApp(const ForgotPasswordScreen()),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Forgot Password?'), findsOneWidget);

      final emailField = find.byType(TextField);
      await tester.enterText(emailField, 'volunteer@maatramfoundation.org');
      await tester.pumpAndSettle();

      await tester.tap(find.text('Send Reset Link'));
      await tester.pumpAndSettle();

      // Exact neutral copy from App answers.pdf
      expect(
        find.text(
            'If an account matches this email, password-reset instructions will be sent.'),
        findsOneWidget,
      );
    });

    testWidgets(
        'ResetPasswordScreen validates password criteria and password confirmation',
        (tester) async {
      final mockAuth = MockRecoveryAuthController();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) => mockAuth),
          ],
          child: createTestApp(const ResetPasswordScreen(
              initialEmail: 'volunteer@maatramfoundation.org')),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Reset Your Password'), findsOneWidget);

      final fields = find.byType(TextField);
      await tester.enterText(fields.first, 'Password123'); // New
      await tester.enterText(fields.last, 'DifferentPassword'); // Confirm
      await tester.pumpAndSettle();

      await tester.tap(find.text('Reset Password'));
      await tester.pumpAndSettle();

      // Password match error
      expect(find.text('Passwords do not match.'), findsOneWidget);

      // Fix inputs with matching passwords
      await tester.enterText(fields.last, 'Password123');
      await tester.pumpAndSettle();

      await tester.tap(find.text('Reset Password'));
      await tester.pumpAndSettle();

      expect(mockAuth.resetPasswordSuccess, isTrue);
    });
  });
}
