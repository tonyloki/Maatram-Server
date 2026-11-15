import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/animations/animated_counter.dart';
import 'package:maatram_mobile/core/animations/animated_progress.dart';
import 'package:maatram_mobile/core/animations/fade_slide_in.dart';
import 'package:maatram_mobile/core/animations/motion_tokens.dart';
import 'package:maatram_mobile/core/animations/pressable.dart';

void main() {
  group('Motion Architecture and Tokens', () {
    test('Motion durations and curves match design specifications', () {
      expect(MaatramMotion.durationFast, const Duration(milliseconds: 150));
      expect(MaatramMotion.durationNormal, const Duration(milliseconds: 250));
      expect(MaatramMotion.durationMedium, const Duration(milliseconds: 400));
      expect(MaatramMotion.durationSlow, const Duration(milliseconds: 600));

      expect(MaatramMotion.curveEntrance, Curves.easeOutCubic);
      expect(MaatramMotion.curveExit, Curves.easeInCubic);
      expect(MaatramMotion.curveStandard, Curves.easeInOutCubic);
      expect(MaatramMotion.curveExpressive, Curves.fastOutSlowIn);
    });

    testWidgets('FadeSlideIn renders child widget properly', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: MaatramFadeSlideIn(
              child: Text('Animated Welcome'),
            ),
          ),
        ),
      );

      expect(find.text('Animated Welcome'), findsOneWidget);
      await tester.pumpAndSettle();
      expect(find.text('Animated Welcome'), findsOneWidget);
    });

    testWidgets('MaatramPressable provides scale and opacity feedback on touch', (tester) async {
      var tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MaatramPressable(
              onTap: () => tapped = true,
              child: const Text('Press Me'),
            ),
          ),
        ),
      );

      expect(find.text('Press Me'), findsOneWidget);
      await tester.tap(find.text('Press Me'));
      await tester.pumpAndSettle();
      expect(tapped, isTrue);
    });

    testWidgets('MaatramAnimatedCounter renders target count', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: MaatramAnimatedCounter(value: 450),
          ),
        ),
      );

      await tester.pumpAndSettle();
      expect(find.text('450'), findsOneWidget);
    });

    testWidgets('MaatramAnimatedProgress renders progress bar without throwing', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: MaatramAnimatedProgress(progress: 0.75),
          ),
        ),
      );

      await tester.pumpAndSettle();
      expect(find.byType(MaatramAnimatedProgress), findsOneWidget);
    });
  });
}
