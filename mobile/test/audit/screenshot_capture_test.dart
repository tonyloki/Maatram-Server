import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
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
import 'package:maatram_mobile/features/auth/presentation/forgot_password_screen.dart';
import 'package:maatram_mobile/features/auth/presentation/login_screen.dart';
import 'package:maatram_mobile/features/auth/presentation/reset_password_screen.dart';
import 'package:maatram_mobile/features/auth/presentation/verify_email_screen.dart';
import 'package:maatram_mobile/features/dev_showcase/presentation/dev_showcase_screen.dart';
import 'package:maatram_mobile/features/events/data/events_repository.dart';
import 'package:maatram_mobile/features/events/presentation/events_screen.dart';
import 'package:maatram_mobile/features/events/presentation/my_activity_screen.dart';
import 'package:maatram_mobile/features/events/state/activity_controller.dart';
import 'package:maatram_mobile/features/events/state/events_controller.dart';
import 'package:maatram_mobile/features/home/presentation/home_screen.dart';
import 'package:maatram_mobile/features/home/state/home_controller.dart';
import 'package:maatram_mobile/features/leaderboard/data/leaderboard_repository.dart';
import 'package:maatram_mobile/features/leaderboard/presentation/leaderboard_screen.dart';
import 'package:maatram_mobile/features/leaderboard/state/leaderboard_controller.dart';
import 'package:maatram_mobile/features/more/presentation/more_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/pending_approval_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/pending_verification_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/rejected_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/welcome_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/welcome_splash_screen.dart';
import 'package:maatram_mobile/features/registration/presentation/registration_flow_screen.dart';

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
  final outDir = Directory('../docs/audits/ui-ux/screenshots');
  if (!outDir.existsSync()) {
    outDir.createSync(recursive: true);
  }

  const testSession = UserSession(
    userId: 'usr-1',
    email: 'priya.s@maatram.org',
    role: 'VOLUNTEER',
    status: 'APPROVED',
    accessToken: 'test-token',
    refreshToken: 'test-refresh',
    firstName: 'Priya',
    lastName: 'S',
    category: 'STUDENT',
  );

  const testProfile = VolunteerProfileModel(
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

  const testGamification = GamificationSummaryModel(
    volunteerProfileId: 'prof-1',
    totalPoints: 180,
    totalHours: 24,
    completedEventsCount: 5,
    badgesEarnedCount: 3,
    rank: 1,
    cycleYear: 2026,
  );

  final List<EventModel> testEvents = [
    EventModel(
      id: 'evt-1',
      title: 'School Visit – Government High School',
      description: 'Career guidance and mentorship session.',
      category: 'School Visit',
      status: 'PUBLISHED',
      mode: 'PHYSICAL',
      startTime: DateTime(2026, 11, 26, 14, 30),
      endTime: DateTime(2026, 11, 26, 18, 30),
      locationName: 'Government High School',
      city: 'Chennai',
      maxVolunteers: 20,
    ),
    EventModel(
      id: 'evt-2',
      title: 'Mock Interview Session',
      description: 'Practice interview for college seniors.',
      category: 'Mock Interview',
      status: 'PUBLISHED',
      mode: 'ONLINE',
      startTime: DateTime(2026, 12, 5, 10, 0),
      endTime: DateTime(2026, 12, 5, 13, 0),
      locationName: 'Virtual Session',
      city: 'Online',
      maxVolunteers: 10,
    ),
  ];

  final testRegistrations = <String, EventRegistrationModel>{
    'evt-1': const EventRegistrationModel(
      id: 'reg-1',
      eventId: 'evt-1',
      status: 'CONFIRMED',
    ),
  };

  final readyHomeState = HomeState(
    profile: const AsyncValue.data(testProfile),
    gamification: const AsyncValue.data(testGamification),
    events: AsyncValue.data(testEvents),
    registrations: testRegistrations,
    unreadNotifications: 3,
  );

  Future<void> captureWidget({
    required WidgetTester tester,
    required Widget widget,
    required String filename,
    double width = 390,
    double height = 844,
    List<dynamic> overrides = const [],
  }) async {
    final boundaryKey = GlobalKey();

    tester.view.physicalSize = Size(width * 2.0, height * 2.0);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    final mockEventsRepo = MockEventsRepository();
    final mockLeaderboardRepo = MockLeaderboardRepository();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith(
            (ref) =>
                MockAuthController(const AuthState.authenticated(testSession)),
          ),
          homeControllerProvider.overrideWith(
            (ref) => MockHomeController(readyHomeState),
          ),
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
          ...overrides,
        ],
        child: MaterialApp(
          debugShowCheckedModeBanner: false,
          home: RepaintBoundary(
            key: boundaryKey,
            child: widget,
          ),
        ),
      ),
    );

    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));

    await tester.runAsync(() async {
      final boundary = boundaryKey.currentContext?.findRenderObject()
          as RenderRepaintBoundary?;
      if (boundary == null) return;
      final image = await boundary.toImage(pixelRatio: 1.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      if (byteData == null) return;
      final file = File('../docs/audits/ui-ux/screenshots/$filename');
      file.writeAsBytesSync(byteData.buffer.asUint8List());
    });
  }

  testWidgets('Capture Welcome Splash Screen WP1', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const WelcomeSplashScreen(),
      filename: 'wp1_welcome_splash_runtime.png',
      width: 390,
      height: 844,
      overrides: [
        authControllerProvider.overrideWith(
          (ref) => MockAuthController(const AuthState.unauthenticated()),
        ),
      ],
    );
  });

  testWidgets('Capture Login Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const LoginScreen(),
      filename: '01_login_screen.png',
      overrides: [
        authControllerProvider.overrideWith(
          (ref) => MockAuthController(const AuthState.unauthenticated()),
        ),
      ],
    );
  });

  testWidgets('Capture Welcome / Post-Approval Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const WelcomeScreen(),
      filename: '02_post_approval_welcome.png',
    );
  });

  testWidgets('Capture Home Screen 390dp', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const HomeScreen(),
      filename: '03_home_screen_390dp.png',
      width: 390,
      height: 1200,
    );
  });

  testWidgets('Capture Home Screen 320dp Compact', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const HomeScreen(),
      filename: '03_home_screen_320dp.png',
      width: 320,
      height: 1200,
    );
  });

  testWidgets('Capture Home Screen 430dp Large', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const HomeScreen(),
      filename: '03_home_screen_430dp.png',
      width: 430,
      height: 1200,
    );
  });

  testWidgets('Capture Home Screen 800dp Tablet', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const HomeScreen(),
      filename: '03_home_screen_800dp.png',
      width: 800,
      height: 1200,
    );
  });

  testWidgets('Capture Registration Step 1 Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const RegistrationFlowScreen(),
      filename: '04_registration_step1.png',
    );
  });

  testWidgets('Capture Verify Email Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const VerifyEmailScreen(initialEmail: 'priya.s@example.com'),
      filename: '05_verify_email.png',
    );
  });

  testWidgets('Capture Forgot Password Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const ForgotPasswordScreen(),
      filename: '06_forgot_password.png',
    );
  });

  testWidgets('Capture Reset Password Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const ResetPasswordScreen(initialEmail: 'priya.s@example.com'),
      filename: '07_reset_password.png',
    );
  });

  testWidgets('Capture Pending Verification Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const PendingVerificationScreen(),
      filename: '08_pending_verification.png',
    );
  });

  testWidgets('Capture Pending Approval Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const PendingApprovalScreen(),
      filename: '09_pending_approval.png',
    );
  });

  testWidgets('Capture Rejected Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const RejectedScreen(),
      filename: '10_rejected.png',
    );
  });

  testWidgets('Capture Events Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const EventsScreen(),
      filename: '11_events_tab.png',
    );
  });

  testWidgets('Capture Leaderboard Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const LeaderboardScreen(),
      filename: '12_leaderboard_tab.png',
    );
  });

  testWidgets('Capture More Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const MoreScreen(),
      filename: '13_more_tab.png',
    );
  });

  testWidgets('Capture My Activity Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const MyActivityScreen(),
      filename: '15_my_activity.png',
    );
    await captureWidget(
      tester: tester,
      widget: const MyActivityScreen(),
      filename: '07_my_activity_runtime.png',
    );
    await captureWidget(
      tester: tester,
      widget: const MyActivityScreen(),
      filename: '07_my_activity_320dp.png',
      width: 320,
    );
    await captureWidget(
      tester: tester,
      widget: const MyActivityScreen(),
      filename: '07_my_activity_430dp.png',
      width: 430,
      height: 932,
    );
  });

  testWidgets('Capture Dev Showcase Screen', (tester) async {
    await captureWidget(
      tester: tester,
      widget: const DevShowcaseScreen(),
      filename: '14_dev_showcase.png',
      height: 1600,
    );
  });
}
