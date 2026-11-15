import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/app/app.dart';
import 'package:maatram_mobile/features/events/presentation/events_placeholder_screen.dart';
import 'package:maatram_mobile/features/home/presentation/home_placeholder_screen.dart';
import 'package:maatram_mobile/features/leaderboard/presentation/leaderboard_placeholder_screen.dart';
import 'package:maatram_mobile/features/more/presentation/more_placeholder_screen.dart';

void main() {
  group('GoRouter 4-Destination Shell Navigation Tests', () {
    testWidgets('Initial route loads HomePlaceholderScreen with welcome greeting', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaatramApp(),
        ),
      );

      await tester.pumpAndSettle();
      expect(find.byType(HomePlaceholderScreen), findsOneWidget);
      expect(find.text('Vanakkam, Sneha!'), findsOneWidget);
    });

    testWidgets('Tapping bottom nav bars switches branches properly', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaatramApp(),
        ),
      );

      await tester.pumpAndSettle();

      // Tap Events
      await tester.tap(find.text('Events'));
      await tester.pumpAndSettle();
      expect(find.byType(EventsPlaceholderScreen), findsOneWidget);

      // Tap Leaderboard
      await tester.tap(find.text('Leaderboard'));
      await tester.pumpAndSettle();
      expect(find.byType(LeaderboardPlaceholderScreen), findsOneWidget);

      // Tap More
      await tester.tap(find.text('More'));
      await tester.pumpAndSettle();
      expect(find.byType(MorePlaceholderScreen), findsOneWidget);

      // Tap back to Home
      await tester.tap(find.text('Home'));
      await tester.pumpAndSettle();
      expect(find.byType(HomePlaceholderScreen), findsOneWidget);
    });
  });
}
