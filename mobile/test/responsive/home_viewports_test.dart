import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/event_model.dart';
import 'package:maatram_mobile/core/models/gamification_summary_model.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/core/models/volunteer_profile_model.dart';
import 'package:maatram_mobile/features/home/presentation/home_screen.dart';
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

  @override
  Future<void> loadAll() async {}

  @override
  Future<void> refresh() async {}

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  final testSession = const UserSession(
    userId: 'usr-1',
    email: 'priya@example.com',
    role: 'VOLUNTEER',
    status: 'APPROVED',
    accessToken: 'test-token',
    refreshToken: 'test-refresh',
    firstName: 'Priya',
    lastName: 'S',
    category: 'STUDENT',
  );

  final testProfile = const VolunteerProfileModel(
    id: 'prof-1',
    userId: 'usr-1',
    firstName: 'Priya',
    lastName: 'S',
    age: 20,
    gender: 'FEMALE',
    category: 'STUDENT',
    organizationOrCollege: 'Sathyabama Institute of Science and Technology',
    parentalConsentVerified: true,
  );

  final testGamification = const GamificationSummaryModel(
    volunteerProfileId: 'prof-1',
    cycleYear: 2026,
    totalPoints: 180.0,
    totalHours: 24.0,
    completedEventsCount: 5,
    badgesEarnedCount: 3,
    rank: 1,
    eventsThisYear: 2,
  );

  final testEvent = EventModel(
    id: 'evt-1',
    title: 'School Visit – Government High School',
    description: 'School mentoring drive for high school students.',
    category: 'EDUCATION',
    mode: 'PHYSICAL',
    startTime: DateTime(2026, 11, 26, 14, 30),
    endTime: DateTime(2026, 11, 26, 18, 30),
    locationName: 'Government High School',
    city: 'Chennai',
    maxVolunteers: 20,
    status: 'PUBLISHED',
  );

  final homeState = HomeState(
    profile: AsyncValue.data(testProfile),
    gamification: AsyncValue.data(testGamification),
    events: AsyncValue.data([testEvent]),
    unreadNotifications: 3,
  );

  Widget createSubject() {
    return ProviderScope(
      overrides: [
        authControllerProvider.overrideWith(
          (ref) => MockAuthController(AuthState.authenticated(testSession)),
        ),
        homeControllerProvider
            .overrideWith((ref) => MockHomeController(homeState)),
      ],
      child: const MaterialApp(
        home: HomeScreen(),
      ),
    );
  }

  group('HomeScreen Responsive Viewport Tests', () {
    final viewports = [
      {'name': '320dp (Compact / SE)', 'width': 320.0, 'height': 568.0},
      {'name': '360dp (Standard Android)', 'width': 360.0, 'height': 800.0},
      {'name': '390dp (Standard iPhone 14)', 'width': 390.0, 'height': 844.0},
      {'name': '430dp (Large iPhone Pro Max)', 'width': 430.0, 'height': 932.0},
      {'name': '800dp (Tablet / iPad Mini)', 'width': 800.0, 'height': 1280.0},
    ];

    for (final vp in viewports) {
      testWidgets(
          'Renders cleanly on ${vp['name']} without RenderFlex overflow',
          (tester) async {
        final w = vp['width']! as double;
        final h = vp['height']! as double;

        tester.view.physicalSize = Size(w * 2.0, h * 2.0);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(tester.view.resetPhysicalSize);

        await tester.pumpWidget(createSubject());
        await tester.pumpAndSettle();

        expect(find.byType(HomeScreen), findsOneWidget);
        expect(tester.takeException(), isNull,
            reason: 'Zero RenderFlex overflow allowed on ${vp['name']}');
      });
    }
  });
}
