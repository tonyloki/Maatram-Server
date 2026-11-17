import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/features/events/data/events_repository.dart';
import 'package:maatram_mobile/features/events/presentation/events_screen.dart';
import 'package:maatram_mobile/features/events/presentation/my_activity_screen.dart';
import 'package:maatram_mobile/features/events/state/activity_controller.dart';
import 'package:maatram_mobile/features/events/state/events_controller.dart';
import 'package:maatram_mobile/features/leaderboard/data/leaderboard_repository.dart';
import 'package:maatram_mobile/features/leaderboard/presentation/leaderboard_screen.dart';
import 'package:maatram_mobile/features/leaderboard/state/leaderboard_controller.dart';
import 'package:maatram_mobile/features/more/presentation/more_screen.dart';

void main() {
  const viewports = <String, Size>{
    '320dp (Compact / SE)': Size(320, 640),
    '360dp (Standard Android)': Size(360, 780),
    '390dp (Standard iPhone)': Size(390, 844),
    '430dp (Pro Max / Plus)': Size(430, 932),
    '800dp (Tablet)': Size(800, 1200),
  };

  final testOverrides = [
    activityControllerProvider.overrideWith(
      (ref) => ActivityController(
        eventsRepository: ref.watch(eventsRepositoryProvider),
        loadOnInit: false,
      ),
    ),
    eventsControllerProvider.overrideWith(
      (ref) => EventsController(
        eventsRepository: ref.watch(eventsRepositoryProvider),
        loadOnInit: false,
      ),
    ),
    leaderboardControllerProvider.overrideWith(
      (ref) => LeaderboardController(
        leaderboardRepository: ref.watch(leaderboardRepositoryProvider),
        loadOnInit: false,
      ),
    ),
  ];

  group('M3.5 Multi-Viewport Responsive Verification (Zero Overflow)', () {
    for (final entry in viewports.entries) {
      final name = entry.key;
      final size = entry.value;

      testWidgets('MyActivityScreen renders cleanly at $name without overflow',
          (tester) async {
        tester.view.physicalSize = Size(size.width * 2, size.height * 2);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          ProviderScope(
            overrides: testOverrides,
            child: const MaterialApp(
              home: MyActivityScreen(),
            ),
          ),
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 400));

        expect(find.byType(MyActivityScreen), findsOneWidget);
        expect(tester.takeException(), isNull);
      });

      testWidgets('EventsScreen renders cleanly at $name without overflow',
          (tester) async {
        tester.view.physicalSize = Size(size.width * 2, size.height * 2);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          ProviderScope(
            overrides: testOverrides,
            child: const MaterialApp(
              home: EventsScreen(),
            ),
          ),
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 400));

        expect(find.byType(EventsScreen), findsOneWidget);
        final exception = tester.takeException();
        if (exception is FlutterError) {
          for (final d in exception.diagnostics) {
            debugPrint('DIAGNOSTIC: ${d.toString()}');
          }
        }
        expect(exception, isNull);
      });

      testWidgets('LeaderboardScreen renders cleanly at $name without overflow',
          (tester) async {
        tester.view.physicalSize = Size(size.width * 2, size.height * 2);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          ProviderScope(
            overrides: testOverrides,
            child: const MaterialApp(
              home: LeaderboardScreen(),
            ),
          ),
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 400));

        expect(find.byType(LeaderboardScreen), findsOneWidget);
        final exception = tester.takeException();
        if (exception is FlutterError) {
          for (final d in exception.diagnostics) {
            debugPrint('DIAGNOSTIC: ${d.toString()}');
          }
        }
        expect(exception, isNull);
      });

      testWidgets('MoreScreen renders cleanly at $name without overflow',
          (tester) async {
        tester.view.physicalSize = Size(size.width * 2, size.height * 2);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          ProviderScope(
            overrides: testOverrides,
            child: const MaterialApp(
              home: MoreScreen(),
            ),
          ),
        );
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 400));

        expect(find.byType(MoreScreen), findsOneWidget);
        final exception = tester.takeException();
        if (exception is FlutterError) {
          for (final d in exception.diagnostics) {
            debugPrint('DIAGNOSTIC: ${d.toString()}');
          }
        }
        expect(exception, isNull);
      });
    }
  });
}
