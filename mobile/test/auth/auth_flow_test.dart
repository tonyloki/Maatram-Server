import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/features/auth/presentation/login_screen.dart';

class MockAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockAuthController([AuthState? initial])
      : super(initial ?? const AuthState.unauthenticated());

  bool loginResult = true;
  String? loginErrorMessage;

  @override
  Future<void> checkInitialSession() async {}

  @override
  Future<bool> login({required String email, required String password}) async {
    if (!loginResult) {
      state = AuthState.error(
          loginErrorMessage ?? 'The email address or password is incorrect.');
      return false;
    }
    final session = UserSession(
      userId: 'usr_test_123',
      email: email,
      role: 'VOLUNTEER',
      status: 'APPROVED',
      accessToken: 'acc_token',
      refreshToken: 'ref_token',
      firstName: 'Anand',
      lastName: 'Kumar',
      category: 'STUDENT',
    );
    state = AuthState.authenticated(session);
    return true;
  }

  @override
  Future<void> logout() async {
    state = const AuthState.unauthenticated();
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  group('Login Experience & Post-Login Routing Tests', () {
    testWidgets(
        'Login screen displays hero header, exact copy, and form fields',
        (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) => MockAuthController()),
          ],
          child: const MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Brand Logo
      expect(find.bySemanticsLabel('Maatram Foundation Logo'), findsOneWidget);

      // Headline
      expect(find.text('Together, We Make\na Difference.'), findsOneWidget);

      // Input labels
      expect(find.text('Email address'), findsOneWidget);
      expect(find.text('Password'), findsOneWidget);
      expect(find.text('Forgot Password?'), findsOneWidget);
      expect(find.text('Sign In'), findsOneWidget);
      expect(find.text('Create a new account'), findsOneWidget);
    });

    testWidgets(
        'Validation triggers exact error copy for empty or malformed inputs',
        (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) => MockAuthController()),
          ],
          child: const MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Tap Sign In without filling inputs
      await tester.tap(find.text('Sign In'));
      await tester.pumpAndSettle();

      // Exact error copy from App answers.pdf
      expect(find.text('Enter your email address.'), findsOneWidget);
      expect(find.text('Enter your password.'), findsOneWidget);

      // Fill invalid email
      final emailField = find.byType(TextField).first;
      await tester.enterText(emailField, 'invalid-email');
      await tester.tap(find.text('Sign In'));
      await tester.pumpAndSettle();

      expect(find.text('Enter a valid email address.'), findsOneWidget);
    });

    testWidgets('Password visibility toggle toggles obscureText',
        (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) => MockAuthController()),
          ],
          child: const MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Locate password TextField
      final passwordFieldFinder = find.byType(TextField).last;
      TextField passwordField = tester.widget<TextField>(passwordFieldFinder);
      expect(passwordField.obscureText, isTrue);

      // Tap visibility icon (initially visibility_off_outlined)
      final visibilityButton = find.byIcon(Icons.visibility_off_outlined);
      expect(visibilityButton, findsOneWidget);
      await tester.tap(visibilityButton);
      await tester.pumpAndSettle();

      // Now obscureText should be false and icon should be visibility_outlined
      passwordField = tester.widget<TextField>(passwordFieldFinder);
      expect(passwordField.obscureText, isFalse);
      expect(find.byIcon(Icons.visibility_outlined), findsOneWidget);
    });

    testWidgets('Failed login renders error banner with exact message',
        (tester) async {
      final mock = MockAuthController();
      mock.loginResult = false;
      mock.loginErrorMessage = 'The email address or password is incorrect.';

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) => mock),
          ],
          child: const MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Enter credentials
      final textFields = find.byType(TextField);
      await tester.enterText(
          textFields.first, 'volunteer@maatramfoundation.org');
      await tester.enterText(textFields.last, 'wrongpassword');

      await tester.tap(find.text('Sign In'));
      await tester.pumpAndSettle();

      expect(find.text('The email address or password is incorrect.'),
          findsOneWidget);
    });
  });
}
