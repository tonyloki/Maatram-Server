import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:maatram_mobile/app/router/route_names.dart';
import 'package:maatram_mobile/core/widgets/buttons/maatram_button.dart';
import 'package:maatram_mobile/features/onboarding/presentation/welcome_splash_screen.dart';

void main() {
  Widget buildTestWidget({
    Size size = const Size(390, 844),
    bool reducedMotion = false,
    GoRouter? router,
  }) {
    if (router != null) {
      return MaterialApp.router(
        routerConfig: router,
      );
    }

    return MaterialApp(
      home: MediaQuery(
        data: MediaQueryData(
          size: size,
          accessibleNavigation: reducedMotion,
        ),
        child: const WelcomeSplashScreen(),
      ),
    );
  }

  group('WelcomeSplashScreen Component & Visual Fidelity Tests', () {
    testWidgets('Renders logo, hero photo, and editorial typography',
        (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(buildTestWidget());
      await tester.pumpAndSettle();

      // Official Maatram Logo
      expect(find.bySemanticsLabel('Maatram Foundation Logo'), findsOneWidget);

      // Hero Image
      expect(find.byType(Image), findsNWidgets(2)); // Logo and hero photo

      // Editorial Georgia Serif Headlines
      expect(find.text('Volunteer for a'), findsOneWidget);
      expect(find.text('Better Tomorrow'), findsOneWidget);

      // Primary & Secondary Action Elements
      expect(
          find.byKey(const Key('welcome_get_started_button')), findsOneWidget);
      expect(find.byKey(const Key('welcome_sign_in_button')), findsOneWidget);
      expect(find.text('Get Started'), findsOneWidget);
      expect(
          find.textContaining('Sign In', findRichText: true), findsOneWidget);
    });

    testWidgets('Primary action "Get Started" triggers registration navigation',
        (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      var pushedRegister = false;

      final testRouter = GoRouter(
        initialLocation: '/welcome',
        routes: [
          GoRoute(
            path: '/welcome',
            builder: (context, state) => const WelcomeSplashScreen(),
          ),
          GoRoute(
            path: RouteNames.registerPath,
            builder: (context, state) {
              pushedRegister = true;
              return const Scaffold(body: Text('Registration Screen Mock'));
            },
          ),
          GoRoute(
            path: RouteNames.loginPath,
            builder: (context, state) =>
                const Scaffold(body: Text('Login Screen Mock')),
          ),
        ],
      );

      await tester.pumpWidget(buildTestWidget(router: testRouter));
      await tester.pumpAndSettle();

      final getStartedFinder =
          find.byKey(const Key('welcome_get_started_button'));
      expect(getStartedFinder, findsOneWidget);

      await tester.ensureVisible(getStartedFinder);
      await tester.tap(getStartedFinder);
      await tester.pumpAndSettle();

      expect(pushedRegister, isTrue);
      expect(find.text('Registration Screen Mock'), findsOneWidget);
    });

    testWidgets('Secondary action "Sign In" triggers login navigation',
        (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      var pushedLogin = false;

      final testRouter = GoRouter(
        initialLocation: '/welcome',
        routes: [
          GoRoute(
            path: '/welcome',
            builder: (context, state) => const WelcomeSplashScreen(),
          ),
          GoRoute(
            path: RouteNames.registerPath,
            builder: (context, state) =>
                const Scaffold(body: Text('Registration Screen Mock')),
          ),
          GoRoute(
            path: RouteNames.loginPath,
            builder: (context, state) {
              pushedLogin = true;
              return const Scaffold(body: Text('Login Screen Mock'));
            },
          ),
        ],
      );

      await tester.pumpWidget(buildTestWidget(router: testRouter));
      await tester.pumpAndSettle();

      final signInFinder = find.byKey(const Key('welcome_sign_in_button'));
      expect(signInFinder, findsOneWidget);

      await tester.ensureVisible(signInFinder);
      await tester.tap(signInFinder);
      await tester.pumpAndSettle();

      expect(pushedLogin, isTrue);
      expect(find.text('Login Screen Mock'), findsOneWidget);
    });

    testWidgets('Supports reduced-motion accessibility without animation delay',
        (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      // Pump with accessibleNavigation: true
      await tester.pumpWidget(buildTestWidget(reducedMotion: true));
      await tester.pump(const Duration(milliseconds: 50));

      // Immediately present without waiting full staggered durations
      expect(find.text('Volunteer for a'), findsOneWidget);
      expect(find.text('Better Tomorrow'), findsOneWidget);
      expect(find.byType(MaatramButton), findsOneWidget);
    });

    testWidgets('Interactive elements satisfy minimum 48dp touch targets',
        (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(buildTestWidget());
      await tester.pumpAndSettle();

      final getStartedSize =
          tester.getSize(find.byKey(const Key('welcome_get_started_button')));
      expect(getStartedSize.height, greaterThanOrEqualTo(48.0));

      final signInSize =
          tester.getSize(find.byKey(const Key('welcome_sign_in_button')));
      expect(signInSize.height, greaterThanOrEqualTo(48.0));
    });
  });
}
