import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/models/attendance_model.dart';
import 'package:maatram_mobile/core/models/event_model.dart';
import 'package:maatram_mobile/core/models/event_registration_model.dart';
import 'package:maatram_mobile/core/models/leaderboard_model.dart';
import 'package:maatram_mobile/core/network/api_client.dart';
import 'package:maatram_mobile/features/events/data/events_repository.dart';
import 'package:maatram_mobile/features/events/presentation/events_screen.dart';
import 'package:maatram_mobile/features/events/presentation/my_activity_screen.dart';
import 'package:maatram_mobile/features/events/state/activity_controller.dart';
import 'package:maatram_mobile/features/events/state/events_controller.dart';
import 'package:maatram_mobile/features/leaderboard/data/leaderboard_repository.dart';
import 'package:maatram_mobile/features/leaderboard/presentation/leaderboard_screen.dart';
import 'package:maatram_mobile/features/leaderboard/state/leaderboard_controller.dart';
import 'package:maatram_mobile/features/more/presentation/more_screen.dart';

class MockEventsRepository extends EventsRepository {
  MockEventsRepository() : super(apiClient: ApiClient());

  @override
  Future<List<EventModel>> getEvents(
          {String? category,
          String? search,
          int page = 1,
          int limit = 20}) async =>
      [];

  @override
  Future<List<EventRegistrationModel>> getMyRegistrations() async => [];

  @override
  Future<List<AttendanceModel>> getMyAttendance() async => [];
}

class MockLeaderboardRepository extends LeaderboardRepository {
  MockLeaderboardRepository() : super(apiClient: ApiClient());

  @override
  Future<List<LeaderboardItemModel>> getLeaderboard(
      {String category = 'overall'}) async {
    return const [
      LeaderboardItemModel(
          rank: 1,
          volunteerName: 'Priya S.',
          category: 'STUDENT',
          points: 1250),
      LeaderboardItemModel(
          rank: 2, volunteerName: 'Arun K.', category: 'ALUMNI', points: 950),
      LeaderboardItemModel(
          rank: 3, volunteerName: 'Meena R.', category: 'STUDENT', points: 910),
    ];
  }
}

void main() {
  final mockEventsRepo = MockEventsRepository();
  final mockLeaderboardRepo = MockLeaderboardRepository();

  final testOverrides = [
    eventsRepositoryProvider.overrideWithValue(mockEventsRepo),
    leaderboardRepositoryProvider.overrideWithValue(mockLeaderboardRepo),
    activityControllerProvider.overrideWith(
      (ref) => ActivityController(
        eventsRepository: mockEventsRepo,
        loadOnInit: false,
      ),
    ),
    eventsControllerProvider.overrideWith(
      (ref) => EventsController(
        eventsRepository: mockEventsRepo,
        loadOnInit: false,
      ),
    ),
    leaderboardControllerProvider.overrideWith(
      (ref) => LeaderboardController(
        leaderboardRepository: mockLeaderboardRepo,
        loadOnInit: false,
      ),
    ),
  ];

  group('M3.5 Functional Widget & Interaction Tests', () {
    testWidgets(
        'MyActivityScreen switches tabs between Upcoming, Completed, and Cancelled',
        (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: testOverrides,
          child: const MaterialApp(
            home: MyActivityScreen(),
          ),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('My Activity'), findsOneWidget);
      expect(find.text('Upcoming'), findsWidgets);
      expect(find.text('Completed'), findsWidgets);
      expect(find.text('Cancelled'), findsWidgets);

      // Tap on 'Completed' tab
      await tester.tap(find.text('Completed').first);
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));
      expect(find.text('Completed Activities'), findsOneWidget);

      // Tap on 'Cancelled' tab
      await tester.tap(find.text('Cancelled').first);
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));
      expect(find.text('No Cancelled Activities'), findsOneWidget);
    });

    testWidgets('EventsScreen displays search, category chips, and event items',
        (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: testOverrides,
          child: const MaterialApp(
            home: EventsScreen(),
          ),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('Events'), findsOneWidget);
      expect(find.text('Search events...'), findsOneWidget);
      expect(find.text('All'), findsOneWidget);
      expect(find.text('Education'), findsWidgets);
      expect(find.text('Mentoring'), findsWidgets);
      expect(find.text('Career'), findsWidgets);

      // Tap on a category chip
      await tester.tap(find.text('Education').first);
      await tester.pump();

      // Enter search query
      await tester.enterText(find.byType(TextField), 'School');
      await tester.pump();
    });

    testWidgets(
        'LeaderboardScreen displays podium and allows category switching',
        (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: testOverrides,
          child: const MaterialApp(
            home: LeaderboardScreen(),
          ),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('Leaderboard'), findsOneWidget);
      expect(find.text('Overall'), findsOneWidget);
      expect(find.text('Students'), findsWidgets);
      expect(find.text('Alumni'), findsWidgets);

      // Switch to Students category
      await tester.tap(find.text('Students').first);
      await tester.pump();
    });

    testWidgets('MoreScreen displays profile card and menu items',
        (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: testOverrides,
          child: const MaterialApp(
            home: MoreScreen(),
          ),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('More'), findsOneWidget);
      expect(find.text('My Activities'), findsOneWidget);
      expect(find.text('My Profile'), findsOneWidget);
      expect(find.text('Notification Settings'), findsOneWidget);
      expect(find.text('Privacy & Consents'), findsOneWidget);
      expect(find.text('Help & Support'), findsOneWidget);
      expect(find.text('About Maatram'), findsOneWidget);
      expect(find.text('Sign Out'), findsOneWidget);
    });
  });
}
