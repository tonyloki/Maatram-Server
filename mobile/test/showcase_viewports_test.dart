import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/theme/theme.dart';
import 'package:maatram_mobile/features/dev_showcase/presentation/dev_showcase_screen.dart';

void main() {
  group('Multi-Viewport Responsive Verification (Section 12)', () {
    const viewports = [
      Size(320, 640), // Small phone (320dp)
      Size(360, 780), // Standard phone (360dp)
      Size(390, 844), // iPhone 14/15 (390dp)
      Size(430, 932), // Large phone / Pro Max (430dp)
      Size(800, 1200), // Tablet (800dp)
    ];

    for (final size in viewports) {
      testWidgets(
          'DevShowcaseScreen renders cleanly at ${size.width.toInt()}x${size.height.toInt()} without overflow',
          (tester) async {
        tester.view.physicalSize = size;
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          ProviderScope(
            child: MaterialApp(
              theme: MaatramTheme.lightTheme,
              home: const DevShowcaseScreen(),
            ),
          ),
        );

        await tester.pumpAndSettle();

        // Verify showcase header and tabs are mounted
        expect(find.text('Design Showcase'), findsOneWidget);
        expect(find.byType(TabBar), findsOneWidget);
        expect(find.text('Tokens & Palette'), findsOneWidget);

        // Verify no RenderFlex overflow exceptions occurred
        expect(tester.takeException(), isNull);
      });
    }
  });
}
