import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/features/auth/presentation/login_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/welcome_screen.dart';
import 'package:maatram_mobile/features/registration/presentation/registration_flow_screen.dart';

class MockViewportAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockViewportAuthController([AuthState? state])
      : super(state ?? const AuthState.unauthenticated());

  @override
  Future<void> checkInitialSession() async {}

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  const viewports = <String, Size>{
    'Compact 320dp': Size(320, 640),
    'Android 360dp': Size(360, 800),
    'Standard 390dp': Size(390, 844),
    'Large 430dp': Size(430, 932),
    'Tablet 800dp': Size(800, 1280),
  };

  group('M2 Multi-Viewport Responsive Tests', () {
    for (final entry in viewports.entries) {
      testWidgets('LoginScreen renders cleanly on ${entry.key}',
          (tester) async {
        FlutterErrorDetails? errorCaught;
        final originalOnError = FlutterError.onError;
        FlutterError.onError = (details) {
          errorCaught = details;
        };

        tester.view.physicalSize = entry.value;
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          FlutterError.onError = originalOnError;
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              authControllerProvider
                  .overrideWith((ref) => MockViewportAuthController()),
            ],
            child: const MaterialApp(
              home: LoginScreen(),
            ),
          ),
        );

        await tester.pumpAndSettle();
        expect(find.byType(LoginScreen), findsOneWidget);
        FlutterError.onError = originalOnError;
        expect(errorCaught, isNull);
      });

      testWidgets('RegistrationFlowScreen renders cleanly on ${entry.key}',
          (tester) async {
        FlutterErrorDetails? errorCaught;
        final originalOnError = FlutterError.onError;
        FlutterError.onError = (details) {
          errorCaught = details;
        };

        tester.view.physicalSize = entry.value;
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          FlutterError.onError = originalOnError;
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              authControllerProvider
                  .overrideWith((ref) => MockViewportAuthController()),
            ],
            child: const MaterialApp(
              home: RegistrationFlowScreen(),
            ),
          ),
        );

        await tester.pumpAndSettle();
        expect(find.byType(RegistrationFlowScreen), findsOneWidget);
        FlutterError.onError = originalOnError;
        expect(errorCaught, isNull);
      });

      testWidgets('WelcomeScreen renders cleanly on ${entry.key}',
          (tester) async {
        FlutterErrorDetails? errorCaught;
        final originalOnError = FlutterError.onError;
        FlutterError.onError = (details) {
          errorCaught = details;
        };

        tester.view.physicalSize = entry.value;
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          FlutterError.onError = originalOnError;
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        const session = UserSession(
          userId: 'usr_viewport',
          email: 'volunteer@maatram.org',
          role: 'VOLUNTEER',
          status: 'APPROVED',
          accessToken: '',
          refreshToken: '',
          firstName: 'Karthik',
        );

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              authControllerProvider.overrideWith(
                (ref) => MockViewportAuthController(
                    AuthState.authenticated(session, isFirstLaunch: true)),
              ),
            ],
            child: const MaterialApp(
              home: WelcomeScreen(),
            ),
          ),
        );

        await tester.pumpAndSettle();
        expect(find.byType(WelcomeScreen), findsOneWidget);
        FlutterError.onError = originalOnError;
        expect(errorCaught, isNull);
      });
    }
  });
}
