import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/features/onboarding/presentation/welcome_splash_screen.dart';

void main() {
  const viewports = <String, Size>{
    '320dp (Ultra Compact / SE)': Size(320, 568),
    '360dp (Standard Android)': Size(360, 800),
    '390dp (Standard iPhone)': Size(390, 844),
    '430dp (Large Flagship / Pro Max)': Size(430, 932),
    '800dp (Tablet / Large Screen)': Size(800, 1280),
  };

  group('WelcomeSplashScreen Responsive Multi-Viewport Audit', () {
    for (final entry in viewports.entries) {
      testWidgets('Renders cleanly on ${entry.key} with zero overflow',
          (tester) async {
        await tester.binding.setSurfaceSize(entry.value);
        addTearDown(() => tester.binding.setSurfaceSize(null));

        await tester.pumpWidget(
          MaterialApp(
            home: MediaQuery(
              data: MediaQueryData(size: entry.value),
              child: const WelcomeSplashScreen(),
            ),
          ),
        );

        await tester.pumpAndSettle();

        // 1. Verify no unhandled exceptions / RenderFlex overflow occurred
        expect(tester.takeException(), isNull);

        // 2. Verify key visual landmarks are present and rendered
        expect(find.text('Volunteer for a'), findsOneWidget);
        expect(find.text('Better Tomorrow'), findsOneWidget);
        expect(find.byKey(const Key('welcome_get_started_button')),
            findsOneWidget);
        expect(find.byKey(const Key('welcome_sign_in_button')), findsOneWidget);

        // 3. Verify touch target compliance on this viewport
        final buttonSize =
            tester.getSize(find.byKey(const Key('welcome_get_started_button')));
        expect(buttonSize.height, greaterThanOrEqualTo(48.0));
      });
    }
  });
}
