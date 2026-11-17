import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/registration_payload.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/features/registration/presentation/registration_flow_screen.dart';
import 'package:maatram_mobile/features/registration/presentation/widgets/category_card.dart';
import 'package:maatram_mobile/features/registration/state/registration_state.dart';

class MockRegistrationAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockRegistrationAuthController() : super(const AuthState.unauthenticated());

  RegistrationPayload? submittedPayload;

  @override
  Future<void> checkInitialSession() async {}

  @override
  Future<bool> register(RegistrationPayload payload) async {
    submittedPayload = payload;
    final session = UserSession(
      userId: 'usr_new_999',
      email: payload.email,
      role: 'VOLUNTEER',
      status: 'PENDING_VERIFICATION',
      accessToken: '',
      refreshToken: '',
      firstName: payload.firstName,
      lastName: payload.lastName,
      category: payload.category,
    );
    state = AuthState.authenticated(session);
    return true;
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
          path: '/onboarding/pending-verification',
          builder: (context, state) =>
              const Scaffold(body: Text('Pending Verification'))),
    ],
  );
  return MaterialApp.router(routerConfig: router);
}

void main() {
  group('Six-Step Guided Registration Tests', () {
    testWidgets('Wizard steps forward and backward correctly with validation',
        (tester) async {
      tester.view.physicalSize = const Size(800, 1600);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final mockAuth = MockRegistrationAuthController();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) => mockAuth),
            registrationProvider.overrideWith((ref) => RegistrationNotifier()),
          ],
          child: createTestApp(const RegistrationFlowScreen()),
        ),
      );

      await tester.pump(const Duration(milliseconds: 300));

      // Step 1: Basic Details visible
      expect(find.text('Step 1 of 6'), findsOneWidget);
      expect(find.text('Basic Details'), findsWidgets);

      // Attempt continue without inputs
      await tester.tap(find.text('Continue'));
      await tester.pump(const Duration(milliseconds: 300));

      // Step 1 validation errors
      expect(find.text('Enter your first name.'), findsOneWidget);
      expect(find.text('Enter your last name.'), findsOneWidget);
      expect(find.text('Enter your email address.'), findsOneWidget);

      // Fill Step 1 valid values
      final textFields = find.byType(TextField);
      await tester.enterText(textFields.at(0), 'Logesh');
      await tester.enterText(textFields.at(1), 'Kannan');
      await tester.enterText(textFields.at(2), 'logesh@example.com');
      await tester.enterText(textFields.at(3), '+919876543210');
      await tester.pump(const Duration(milliseconds: 300));

      // Tap Continue -> advances to Step 2
      await tester.tap(find.text('Continue'));
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('Step 2 of 6'), findsOneWidget);
      expect(find.text('Select Category'), findsWidgets);
      expect(find.byType(CategorySelectionCard), findsNWidgets(3));

      // Select Alumni
      await tester.tap(find.text('Alumni'));
      await tester.pump(const Duration(milliseconds: 300));

      // Tap Continue -> advances to Step 3 (Alumni Specifics)
      await tester.tap(find.text('Continue'));
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('Step 3 of 6'), findsOneWidget);
      expect(find.text('Alumni & Professional Background'), findsOneWidget);

      // Fill Alumni details
      final alumniFields = find.byType(TextField);
      await tester.enterText(alumniFields.at(0), 'CEG Anna University');
      await tester.enterText(alumniFields.at(3), 'Zoho Corporation');
      await tester.pump(const Duration(milliseconds: 300));

      // Tap Continue -> advances to Step 4
      await tester.tap(find.text('Continue'));
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('Step 4 of 6'), findsOneWidget);
      expect(find.text('Skills & Availability'), findsWidgets);

      // Tap a skill chip
      await tester.tap(find.text('Mentoring'));
      await tester.pump(const Duration(milliseconds: 300));

      // Tap Continue -> advances to Step 5 (Privacy & Consent)
      await tester.tap(find.text('Continue'));
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('Step 5 of 6'), findsOneWidget);
      expect(find.text('Privacy & Consent'), findsWidgets);

      // Tap Continue -> advances to Step 6 (Review & Submit)
      await tester.tap(find.text('Continue'));
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('Step 6 of 6'), findsOneWidget);
      expect(find.text('Review & Submit'), findsWidgets);
      expect(find.text('Submit Application'), findsOneWidget);

      // Fill password
      final pwFields = find.byType(TextField);
      if (pwFields.evaluate().isNotEmpty) {
        await tester.enterText(pwFields.first, 'Secret@123');
        if (pwFields.evaluate().length > 1) {
          await tester.enterText(pwFields.at(1), 'Secret@123');
        }
      }
      await tester.pump(const Duration(milliseconds: 300));

      // Tap Submit Application
      await tester.tap(find.text('Submit Application'));
      await tester.pump(const Duration(milliseconds: 300));

      // Verify payload submitted to controller
      expect(mockAuth.submittedPayload, isNotNull);
      expect(mockAuth.submittedPayload?.email, 'logesh@example.com');
      expect(mockAuth.submittedPayload?.firstName, 'Logesh');
      expect(mockAuth.submittedPayload?.category, 'ALUMNI');
    });

    testWidgets(
        'Tapping Back button navigates to previous step without data loss',
        (tester) async {
      tester.view.physicalSize = const Size(800, 1600);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final mockAuth = MockRegistrationAuthController();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith((ref) => mockAuth),
            registrationProvider.overrideWith((ref) => RegistrationNotifier()),
          ],
          child: createTestApp(const RegistrationFlowScreen()),
        ),
      );

      await tester.pump(const Duration(milliseconds: 300));

      // Fill Step 1
      final textFields = find.byType(TextField);
      await tester.enterText(textFields.at(0), 'Ramesh');
      await tester.enterText(textFields.at(1), 'S');
      await tester.enterText(textFields.at(2), 'ramesh@example.com');
      await tester.enterText(textFields.at(3), '+919876543210');
      await tester.pump();

      await tester.tap(find.text('Continue'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 500));

      expect(find.text('Step 2 of 6'), findsOneWidget);

      // Tap Back
      await tester.tap(find.text('Back'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 500));

      expect(find.text('Step 1 of 6'), findsOneWidget);
      // Data preserved
      expect(find.text('Ramesh'), findsOneWidget);
      expect(find.text('ramesh@example.com'), findsOneWidget);
    });
  });
}
