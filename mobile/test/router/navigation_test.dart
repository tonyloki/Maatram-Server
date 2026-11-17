import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/app/app.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/attendance_model.dart';
import 'package:maatram_mobile/core/models/event_model.dart';
import 'package:maatram_mobile/core/models/event_registration_model.dart';
import 'package:maatram_mobile/core/models/gamification_summary_model.dart';
import 'package:maatram_mobile/core/models/leaderboard_model.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/core/models/volunteer_profile_model.dart';
import 'package:maatram_mobile/core/network/api_client.dart';
import 'package:maatram_mobile/features/auth/presentation/login_screen.dart';
import 'package:maatram_mobile/features/events/data/events_repository.dart';
import 'package:maatram_mobile/features/events/presentation/events_screen.dart';
import 'package:maatram_mobile/features/events/state/events_controller.dart';
import 'package:maatram_mobile/features/home/presentation/home_screen.dart';
import 'package:maatram_mobile/features/home/state/home_controller.dart';
import 'package:maatram_mobile/features/leaderboard/data/leaderboard_repository.dart';
import 'package:maatram_mobile/features/leaderboard/presentation/leaderboard_screen.dart';
import 'package:maatram_mobile/features/leaderboard/state/leaderboard_controller.dart';
import 'package:maatram_mobile/features/more/presentation/more_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/welcome_splash_screen.dart';

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
          {String category = 'overall'}) async =>
      [];
}

class MockNavigationAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockNavigationAuthController(super.state);

  @override
  Future<void> checkInitialSession() async {}

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class MockNavigationHomeController extends StateNotifier<HomeState>
    implements HomeController {
  MockNavigationHomeController()
      : super(
          HomeState(
            profile: AsyncValue.data(
              const VolunteerProfileModel(
                id: 'prof_test',
                userId: 'usr_nav_test',
                firstName: 'Sneha',
                lastName: 'R',
                age: 22,
                gender: 'FEMALE',
                category: 'STUDENT',
                parentalConsentVerified: true,
              ),
            ),
            gamification: AsyncValue.data(
              const GamificationSummaryModel(
                volunteerProfileId: 'prof_test',
                cycleYear: 2026,
                totalPoints: 120.0,
                totalHours: 18.0,
                completedEventsCount: 4,
                badgesEarnedCount: 2,
                rank: 3,
              ),
            ),
            events: const AsyncValue.data([]),
          ),
        );

  @override
  Future<void> loadAll() async {}

  @override
  Future<void> refresh() async {}

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  const approvedSession = UserSession(
    userId: 'usr_nav_test',
    email: 'sneha@maatram.org',
    role: 'VOLUNTEER',
    status: 'APPROVED',
    accessToken: 'test_token',
    refreshToken: 'test_refresh',
    firstName: 'Sneha',
    lastName: 'R',
  );

  group('GoRouter 4-Destination Shell Navigation Tests', () {
    testWidgets(
        'Unauthenticated user lands on WelcomeSplashScreen and can navigate to LoginScreen',
        (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith(
              (ref) => MockNavigationAuthController(
                  const AuthState.unauthenticated()),
            ),
            homeControllerProvider.overrideWith(
              (ref) => MockNavigationHomeController(),
            ),
          ],
          child: const MaatramApp(),
        ),
      );

      await tester.pumpAndSettle();
      expect(find.byType(WelcomeSplashScreen), findsOneWidget);

      // Tap Sign In to proceed to LoginScreen
      final signInFinder = find.byKey(const Key('welcome_sign_in_button'));
      await tester.ensureVisible(signInFinder);
      await tester.tap(signInFinder);
      await tester.pumpAndSettle();
      expect(find.byType(LoginScreen), findsOneWidget);
    });

    testWidgets(
        'Initial route loads HomeScreen with welcome greeting when authenticated',
        (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith(
              (ref) => MockNavigationAuthController(
                  AuthState.authenticated(approvedSession)),
            ),
            homeControllerProvider.overrideWith(
              (ref) => MockNavigationHomeController(),
            ),
          ],
          child: const MaatramApp(),
        ),
      );

      await tester.pumpAndSettle();
      expect(find.byType(HomeScreen), findsOneWidget);
      expect(find.textContaining('Sneha'), findsWidgets);
    });

    testWidgets('Tapping bottom nav bars switches branches properly',
        (tester) async {
      final mockEventsRepo = MockEventsRepository();
      final mockLeaderboardRepo = MockLeaderboardRepository();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authControllerProvider.overrideWith(
              (ref) => MockNavigationAuthController(
                  AuthState.authenticated(approvedSession)),
            ),
            homeControllerProvider.overrideWith(
              (ref) => MockNavigationHomeController(),
            ),
            eventsRepositoryProvider.overrideWithValue(mockEventsRepo),
            leaderboardRepositoryProvider
                .overrideWithValue(mockLeaderboardRepo),
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
          ],
          child: const MaatramApp(),
        ),
      );

      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));

      // Tap Events in Bottom Nav
      await tester.tap(find.byIcon(Icons.calendar_month_outlined));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));
      expect(find.byType(EventsScreen), findsOneWidget);

      // Tap Leaderboard in Bottom Nav
      await tester.tap(find.byIcon(Icons.emoji_events_outlined));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));
      expect(find.byType(LeaderboardScreen), findsOneWidget);

      // Tap More in Bottom Nav
      await tester.tap(find.byIcon(Icons.grid_view_outlined));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));
      expect(find.byType(MoreScreen), findsOneWidget);

      // Tap back to Home in Bottom Nav
      await tester.tap(find.byIcon(Icons.home_outlined));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));
      expect(find.byType(HomeScreen), findsOneWidget);
    });
  });
}
