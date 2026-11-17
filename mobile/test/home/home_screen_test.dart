import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/event_model.dart';
import 'package:maatram_mobile/core/models/event_registration_model.dart';
import 'package:maatram_mobile/core/models/gamification_summary_model.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/core/models/volunteer_profile_model.dart';
import 'package:maatram_mobile/features/home/presentation/home_screen.dart';
import 'package:maatram_mobile/features/home/presentation/widgets/home_header.dart';
import 'package:maatram_mobile/features/home/presentation/widgets/your_progress_section.dart';
import 'package:maatram_mobile/features/home/state/home_controller.dart';

class MockAuthController extends StateNotifier<AuthState>
    implements AuthController {
  MockAuthController(super.initial);

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class MockHomeController extends StateNotifier<HomeState>
    implements HomeController {
  MockHomeController(super.initial);

  bool refreshCalled = false;
  bool retryEventsCalled = false;

  @override
  Future<void> loadAll() async {}

  @override
  Future<void> refresh() async {
    refreshCalled = true;
  }

  @override
  Future<void> retryEvents() async {
    retryEventsCalled = true;
  }

  @override
  Future<void> retryGamification() async {}

  @override
  Future<void> retryProfile() async {}

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  Widget createSubject({
    required HomeState state,
    required UserSession session,
    HomeController? controller,
  }) {
    final mockController = controller ?? MockHomeController(state);
    return ProviderScope(
      overrides: [
        authControllerProvider.overrideWith(
          (ref) => MockAuthController(AuthState.authenticated(session)),
        ),
        homeControllerProvider.overrideWith((ref) => mockController),
      ],
      child: const MaterialApp(
        home: HomeScreen(),
      ),
    );
  }

  group('HomeScreen Data Integrity & Dynamic API Audit Tests', () {
    testWidgets(
        'User 1 (Karthik Raja) dynamically sees their own name, category, and points',
        (tester) async {
      const sessionUser1 = UserSession(
        userId: 'usr-karthik',
        email: 'karthik@example.com',
        role: 'VOLUNTEER',
        status: 'APPROVED',
        accessToken: 'tok-1',
        refreshToken: 'ref-1',
        firstName: 'Karthik',
        lastName: 'Raja',
        category: 'ALUMNI',
      );
      const profileUser1 = VolunteerProfileModel(
        id: 'prof-karthik',
        userId: 'usr-karthik',
        firstName: 'Karthik',
        lastName: 'Raja',
        age: 26,
        gender: 'MALE',
        category: 'ALUMNI',
        organizationOrCollege: 'Zoho Corporation',
        parentalConsentVerified: true,
      );
      const gamificationUser1 = GamificationSummaryModel(
        volunteerProfileId: 'prof-karthik',
        cycleYear: 2026,
        totalPoints: 350.0,
        totalHours: 42.0,
        completedEventsCount: 8,
        badgesEarnedCount: 5,
        rank: 2,
      );

      final stateUser1 = HomeState(
        profile: const AsyncValue.data(profileUser1),
        gamification: const AsyncValue.data(gamificationUser1),
        events: const AsyncValue.data([]),
        unreadNotifications: 4,
      );

      await tester
          .pumpWidget(createSubject(state: stateUser1, session: sessionUser1));
      await tester.pumpAndSettle();

      expect(find.textContaining('Karthik R.'), findsWidgets);
      expect(find.textContaining('Zoho Corporation'), findsOneWidget);
      expect(find.text('350'), findsOneWidget);
      expect(find.text('4'), findsOneWidget);
    });

    testWidgets(
        'User 2 (Ananya Iyer) dynamically sees their own name, category, and points',
        (tester) async {
      const sessionUser2 = UserSession(
        userId: 'usr-ananya',
        email: 'ananya@example.com',
        role: 'VOLUNTEER',
        status: 'APPROVED',
        accessToken: 'tok-2',
        refreshToken: 'ref-2',
        firstName: 'Ananya',
        lastName: 'Iyer',
        category: 'STUDENT',
      );
      const profileUser2 = VolunteerProfileModel(
        id: 'prof-ananya',
        userId: 'usr-ananya',
        firstName: 'Ananya',
        lastName: 'Iyer',
        age: 19,
        gender: 'FEMALE',
        category: 'STUDENT',
        organizationOrCollege: 'Anna University',
        parentalConsentVerified: true,
      );
      const gamificationUser2 = GamificationSummaryModel(
        volunteerProfileId: 'prof-ananya',
        cycleYear: 2026,
        totalPoints: 85.0,
        totalHours: 12.0,
        completedEventsCount: 3,
        badgesEarnedCount: 1,
        rank: null,
      );

      final stateUser2 = HomeState(
        profile: const AsyncValue.data(profileUser2),
        gamification: const AsyncValue.data(gamificationUser2),
        events: const AsyncValue.data([]),
        unreadNotifications: 0,
      );

      await tester
          .pumpWidget(createSubject(state: stateUser2, session: sessionUser2));
      await tester.pumpAndSettle();

      expect(find.textContaining('Ananya I.'), findsWidgets);
      expect(find.textContaining('Anna University'), findsOneWidget);
      expect(find.text('85'), findsOneWidget);
      expect(find.text('350'), findsNothing);
    });

    testWidgets(
        'Missing ranking does NOT show #1 or Top Volunteer (shows neutral dash)',
        (tester) async {
      const session = UserSession(
        userId: 'usr-newbie',
        email: 'newbie@example.com',
        role: 'VOLUNTEER',
        status: 'APPROVED',
        accessToken: 'tok',
        refreshToken: 'ref',
        firstName: 'New',
        lastName: 'Volunteer',
      );
      const profile = VolunteerProfileModel(
        id: 'prof-newbie',
        userId: 'usr-newbie',
        firstName: 'New',
        lastName: 'Volunteer',
        age: 21,
        gender: 'OTHER',
        category: 'STUDENT',
        parentalConsentVerified: true,
      );
      const unrankedGamification = GamificationSummaryModel(
        volunteerProfileId: 'prof-newbie',
        cycleYear: 2026,
        totalPoints: 0.0,
        totalHours: 0.0,
        completedEventsCount: 0,
        badgesEarnedCount: 0,
        rank: null,
      );

      final state = HomeState(
        profile: const AsyncValue.data(profile),
        gamification: const AsyncValue.data(unrankedGamification),
        events: const AsyncValue.data([]),
        unreadNotifications: 0,
      );

      await tester.pumpWidget(createSubject(state: state, session: session));
      await tester.pumpAndSettle();

      expect(find.text('#1'), findsNothing);
      expect(find.text('Top Volunteer'), findsNothing);
      expect(find.text('—'), findsOneWidget);
      expect(find.text('Leaderboard'), findsOneWidget);
    });

    testWidgets(
        'Missing/zero notification count does NOT show a fabricated badge',
        (tester) async {
      const session = UserSession(
        userId: 'usr-001',
        email: 'test@example.com',
        role: 'VOLUNTEER',
        status: 'APPROVED',
        accessToken: 'tok',
        refreshToken: 'ref',
      );

      final state = const HomeState(
        profile: AsyncValue.data(VolunteerProfileModel(
          id: 'p1',
          userId: 'u1',
          firstName: 'Ramesh',
          lastName: 'K',
          age: 22,
          gender: 'MALE',
          category: 'STUDENT',
        )),
        gamification: AsyncValue.data(GamificationSummaryModel(
          volunteerProfileId: 'p1',
          cycleYear: 2026,
          totalPoints: 10.0,
          totalHours: 2.0,
          completedEventsCount: 1,
          badgesEarnedCount: 0,
        )),
        events: AsyncValue.data([]),
        unreadNotifications: 0,
      );

      await tester.pumpWidget(createSubject(state: state, session: session));
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.notifications_none_rounded), findsOneWidget);
      final headerFinder = find.byType(HomeHeader);
      expect(find.descendant(of: headerFinder, matching: find.text('3')),
          findsNothing);
      expect(find.descendant(of: headerFinder, matching: find.text('0')),
          findsNothing);
    });

    testWidgets(
        'No numeric progress percentage or progress ring appears without backend target',
        (tester) async {
      const session = UserSession(
        userId: 'usr-001',
        email: 'test@example.com',
        role: 'VOLUNTEER',
        status: 'APPROVED',
        accessToken: 'tok',
        refreshToken: 'ref',
      );

      final state = const HomeState(
        profile: AsyncValue.data(VolunteerProfileModel(
          id: 'p1',
          userId: 'u1',
          firstName: 'Siddharth',
          lastName: 'M',
          age: 23,
          gender: 'MALE',
          category: 'STUDENT',
        )),
        gamification: AsyncValue.data(GamificationSummaryModel(
          volunteerProfileId: 'p1',
          cycleYear: 2026,
          totalPoints: 50.0,
          totalHours: 8.0,
          completedEventsCount: 2,
          badgesEarnedCount: 2,
        )),
        events: AsyncValue.data([]),
      );

      await tester.pumpWidget(createSubject(state: state, session: session));
      await tester.pumpAndSettle();

      expect(find.text('75%'), findsNothing);
      expect(find.textContaining('%'), findsNothing);
      expect(find.byType(YourProgressSection), findsOneWidget);
      expect(find.text('Your Progress'), findsOneWidget);
      expect(find.text('Keep going!'), findsOneWidget);
    });

    testWidgets(
        'Events reflect actual backend response with registration status badges',
        (tester) async {
      const session = UserSession(
        userId: 'usr-001',
        email: 'test@example.com',
        role: 'VOLUNTEER',
        status: 'APPROVED',
        accessToken: 'tok',
        refreshToken: 'ref',
      );

      final event1 = EventModel(
        id: 'evt-real-1',
        title: 'STEM Mentorship Workshop',
        description: 'Interactive STEM workshop for grade 9 students.',
        category: 'EDUCATION',
        mode: 'PHYSICAL',
        startTime: DateTime(2026, 11, 28, 10, 0),
        endTime: DateTime(2026, 11, 28, 13, 0),
        locationName: 'Govt Higher Secondary School',
        city: 'Coimbatore',
        maxVolunteers: 15,
        status: 'PUBLISHED',
      );

      final reg1 = const EventRegistrationModel(
        id: 'reg-1',
        eventId: 'evt-real-1',
        status: 'SELECTED',
      );

      final state = HomeState(
        profile: const AsyncValue.data(VolunteerProfileModel(
          id: 'p1',
          userId: 'u1',
          firstName: 'Preethi',
          lastName: 'S',
          age: 24,
          gender: 'FEMALE',
          category: 'STUDENT',
        )),
        gamification: const AsyncValue.data(GamificationSummaryModel(
          volunteerProfileId: 'p1',
          cycleYear: 2026,
          totalPoints: 20.0,
          totalHours: 4.0,
          completedEventsCount: 1,
          badgesEarnedCount: 1,
        )),
        events: AsyncValue.data([event1]),
        registrations: {'evt-real-1': reg1},
      );

      await tester.pumpWidget(createSubject(state: state, session: session));
      await tester.pumpAndSettle();

      expect(find.text('STEM Mentorship Workshop'), findsOneWidget);
      expect(find.textContaining('Coimbatore'), findsOneWidget);
      expect(find.text('Confirmed'), findsOneWidget);
    });

    testWidgets('Empty events response renders polished empty state card',
        (tester) async {
      const session = UserSession(
        userId: 'usr-001',
        email: 'test@example.com',
        role: 'VOLUNTEER',
        status: 'APPROVED',
        accessToken: 'tok',
        refreshToken: 'ref',
      );

      final state = const HomeState(
        profile: AsyncValue.data(VolunteerProfileModel(
          id: 'p1',
          userId: 'u1',
          firstName: 'Preethi',
          lastName: 'S',
          age: 24,
          gender: 'FEMALE',
          category: 'STUDENT',
        )),
        gamification: AsyncValue.data(GamificationSummaryModel(
          volunteerProfileId: 'p1',
          cycleYear: 2026,
          totalPoints: 0.0,
          totalHours: 0.0,
          completedEventsCount: 0,
          badgesEarnedCount: 0,
        )),
        events: AsyncValue.data([]),
      );

      await tester.pumpWidget(createSubject(state: state, session: session));
      await tester.pumpAndSettle();

      expect(
          find.text('No upcoming events scheduled right now'), findsOneWidget);
      expect(find.text('Explore All Events'), findsOneWidget);
    });

    testWidgets(
        'Partial API failure does not blank the screen and allows independent retry',
        (tester) async {
      const session = UserSession(
        userId: 'usr-001',
        email: 'test@example.com',
        role: 'VOLUNTEER',
        status: 'APPROVED',
        accessToken: 'tok',
        refreshToken: 'ref',
      );

      final state = HomeState(
        profile: const AsyncValue.data(VolunteerProfileModel(
          id: 'p1',
          userId: 'u1',
          firstName: 'Preethi',
          lastName: 'S',
          age: 24,
          gender: 'FEMALE',
          category: 'STUDENT',
        )),
        gamification: const AsyncValue.data(GamificationSummaryModel(
          volunteerProfileId: 'p1',
          cycleYear: 2026,
          totalPoints: 100.0,
          totalHours: 15.0,
          completedEventsCount: 3,
          badgesEarnedCount: 1,
        )),
        events:
            AsyncValue.error(Exception('Gateway timeout'), StackTrace.empty),
      );

      final controller = MockHomeController(state);
      await tester.pumpWidget(createSubject(
          state: state, session: session, controller: controller));
      await tester.pumpAndSettle();

      expect(find.textContaining('Preethi S.'), findsWidgets);
      expect(find.text('100'), findsOneWidget);
      expect(find.text('15'), findsOneWidget);

      expect(find.text('Could not load upcoming events.'), findsOneWidget);
      await tester.tap(find.text('Retry'));
      await tester.pump();
      expect(controller.retryEventsCalled, isTrue);
    });
  });
}
