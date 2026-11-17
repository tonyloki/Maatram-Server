import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/achievement_model.dart';
import 'package:maatram_mobile/core/models/attendance_model.dart';
import 'package:maatram_mobile/core/models/consent_model.dart';
import 'package:maatram_mobile/core/models/event_model.dart';
import 'package:maatram_mobile/core/models/event_registration_model.dart';
import 'package:maatram_mobile/core/models/gamification_summary_model.dart';
import 'package:maatram_mobile/core/models/leaderboard_model.dart';
import 'package:maatram_mobile/core/models/notification_model.dart';
import 'package:maatram_mobile/core/models/point_ledger_model.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/core/models/volunteer_profile_model.dart';
import 'package:maatram_mobile/core/network/api_client.dart';
import 'package:maatram_mobile/features/auth/presentation/forgot_password_screen.dart';
import 'package:maatram_mobile/features/auth/presentation/login_screen.dart';
import 'package:maatram_mobile/features/auth/presentation/reset_password_screen.dart';
import 'package:maatram_mobile/features/auth/presentation/verify_email_screen.dart';
import 'package:maatram_mobile/features/events/data/events_repository.dart';
import 'package:maatram_mobile/features/events/presentation/activity_details_screen.dart';
import 'package:maatram_mobile/features/events/presentation/event_details_screen.dart';
import 'package:maatram_mobile/features/events/presentation/event_registration_screen.dart';
import 'package:maatram_mobile/features/events/presentation/events_screen.dart';
import 'package:maatram_mobile/features/events/presentation/my_activity_screen.dart';
import 'package:maatram_mobile/features/events/state/activity_controller.dart';
import 'package:maatram_mobile/features/events/state/events_controller.dart';
import 'package:maatram_mobile/features/gamification/data/gamification_repository.dart';
import 'package:maatram_mobile/features/gamification/presentation/achievement_details_modal.dart';
import 'package:maatram_mobile/features/gamification/presentation/achievements_screen.dart';
import 'package:maatram_mobile/features/gamification/presentation/points_history_screen.dart';
import 'package:maatram_mobile/features/gamification/presentation/points_overview_screen.dart';
import 'package:maatram_mobile/features/home/presentation/home_screen.dart';
import 'package:maatram_mobile/features/home/state/home_controller.dart';
import 'package:maatram_mobile/features/leaderboard/data/leaderboard_repository.dart';
import 'package:maatram_mobile/features/leaderboard/presentation/leaderboard_screen.dart';
import 'package:maatram_mobile/features/leaderboard/state/leaderboard_controller.dart';
import 'package:maatram_mobile/features/more/data/more_repository.dart';
import 'package:maatram_mobile/features/more/presentation/about_maatram_screen.dart';
import 'package:maatram_mobile/features/more/presentation/app_settings_screen.dart';
import 'package:maatram_mobile/features/more/presentation/edit_profile_screen.dart';
import 'package:maatram_mobile/features/more/presentation/help_support_screen.dart';
import 'package:maatram_mobile/features/more/presentation/logout_confirmation_dialog.dart';
import 'package:maatram_mobile/features/more/presentation/more_screen.dart';
import 'package:maatram_mobile/features/more/presentation/notification_details_screen.dart';
import 'package:maatram_mobile/features/more/presentation/notification_settings_screen.dart';
import 'package:maatram_mobile/features/more/presentation/notifications_screen.dart';
import 'package:maatram_mobile/features/more/presentation/privacy_screen.dart';
import 'package:maatram_mobile/features/more/presentation/profile_photo_screen.dart';
import 'package:maatram_mobile/features/more/presentation/profile_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/pending_approval_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/pending_verification_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/rejected_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/welcome_screen.dart';
import 'package:maatram_mobile/features/onboarding/presentation/welcome_splash_screen.dart';
import 'package:maatram_mobile/features/registration/presentation/registration_flow_screen.dart';
import 'package:maatram_mobile/features/registration/state/registration_state.dart';
import 'package:shared_preferences/shared_preferences.dart';

class CaptureMockEventsRepo extends EventsRepository {
  CaptureMockEventsRepo() : super(apiClient: ApiClient());

  @override
  Future<List<EventModel>> getEvents(
      {String? category, String? search, int page = 1, int limit = 20}) async {
    return [
      EventModel(
        id: 'evt-1',
        title: 'School Visit – Government High School',
        description: 'Career guidance and mentorship session.',
        category: 'STUDENT',
        status: 'PUBLISHED',
        mode: 'OFFLINE',
        startTime: DateTime(2026, 11, 26, 14, 30),
        endTime: DateTime(2026, 11, 26, 18, 30),
        locationName: 'Government High School',
        city: 'Chennai',
        maxVolunteers: 20,
        registeredCount: 14,
      ),
      EventModel(
        id: 'evt-2',
        title: 'Mock Interview Session',
        description: 'Practice interview for college seniors.',
        category: 'STUDENT',
        status: 'PUBLISHED',
        mode: 'ONLINE',
        startTime: DateTime(2026, 12, 5, 10, 0),
        endTime: DateTime(2026, 12, 5, 13, 0),
        locationName: 'Virtual Hall',
        city: 'Online',
        maxVolunteers: 15,
        registeredCount: 15,
      ),
    ];
  }

  @override
  Future<EventModel?> getEventById(String eventId) async {
    return EventModel(
      id: eventId,
      title: 'School Visit – Government High School',
      description:
          'Career guidance and mentorship session for 12th standard students.',
      category: 'STUDENT',
      status: 'PUBLISHED',
      mode: 'OFFLINE',
      startTime: DateTime(2026, 11, 26, 14, 30),
      endTime: DateTime(2026, 11, 26, 18, 30),
      locationName: 'Government High School',
      address: 'Ashok Nagar, Chennai',
      city: 'Chennai',
      maxVolunteers: 20,
      registeredCount: 14,
    );
  }

  @override
  Future<List<EventRegistrationModel>> getMyRegistrations() async {
    return const [
      EventRegistrationModel(
        id: 'reg-1',
        eventId: 'evt-1',
        status: 'SELECTED',
      ),
    ];
  }

  @override
  Future<List<AttendanceModel>> getMyAttendance() async {
    return [
      AttendanceModel(
        id: 'att-1',
        eventId: 'evt-101',
        eventTitle: 'School Visit - Government High School',
        checkInTime: DateTime(2026, 10, 26, 14, 30),
        checkOutTime: DateTime(2026, 10, 26, 18, 30),
        hoursCredited: 4.0,
        status: 'VERIFIED',
      ),
    ];
  }
}

class CaptureMockLeaderboardRepo extends LeaderboardRepository {
  CaptureMockLeaderboardRepo() : super(apiClient: ApiClient());

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
      LeaderboardItemModel(
          rank: 4,
          volunteerName: 'Karthik V.',
          category: 'CORPORATE',
          points: 890),
      LeaderboardItemModel(
          rank: 5, volunteerName: 'Divya S.', category: 'STUDENT', points: 860),
    ];
  }
}

class CaptureMockMoreRepo extends MoreRepository {
  CaptureMockMoreRepo() : super(apiClient: ApiClient());

  @override
  Future<NotificationListModel?> getNotifications(
      {bool unreadOnly = false, int page = 1, int limit = 20}) async {
    return NotificationListModel(
      items: [
        NotificationModel(
          id: 'n-1',
          userId: 'usr-1',
          title: 'Event Reminder: School Visit',
          message:
              'Your volunteer session begins tomorrow at 2:30 PM. Please arrive 15 minutes early.',
          type: 'EVENT_REMINDER',
          isRead: false,
          createdAt: DateTime(2026, 11, 25, 10, 0),
        ),
        NotificationModel(
          id: 'n-2',
          userId: 'usr-1',
          title: 'Points Awarded: +40 Karma Points',
          message:
              'Thank you for participating in the Government High School session! 4.0 hours verified.',
          type: 'POINTS_AWARDED',
          isRead: true,
          createdAt: DateTime(2026, 11, 20, 19, 0),
        ),
      ],
      total: 2,
      page: 1,
      limit: 20,
      totalPages: 1,
      unreadCount: 1,
    );
  }

  @override
  Future<ConsentModel?> getConsent() async {
    return ConsentModel(
      id: 'c-1',
      volunteerProfileId: 'prof-1',
      leaderboardVisible: true,
      nameVisible: true,
      thankYouEmails: true,
      linkedinContent: false,
      contactAvailable: false,
      mediaUsage: true,
      version: 1,
      updatedAt: DateTime(2026, 11, 20),
    );
  }
}

class CaptureMockGamificationRepo extends GamificationRepository {
  CaptureMockGamificationRepo() : super(apiClient: ApiClient());

  @override
  Future<GamificationSummaryModel?> getSummary() async {
    return const GamificationSummaryModel(
      volunteerProfileId: 'prof-1',
      cycleYear: 2026,
      totalPoints: 180.0,
      totalHours: 24.0,
      completedEventsCount: 5,
      badgesEarnedCount: 3,
      rank: 1,
    );
  }

  @override
  Future<PointLedgerModel?> getLedger({int page = 1, int pageSize = 50}) async {
    return PointLedgerModel(
      items: [
        PointTransactionModel(
          id: 'tx-1',
          volunteerProfileId: 'prof-1',
          totalPoints: 50.0,
          transactionType: 'EVENT_COMPLETION',
          reason: 'School Visit - Government High School',
          hoursCredited: 4.0,
          cycleYear: 2026,
          createdAt: DateTime(2026, 11, 20, 18, 30),
        ),
        PointTransactionModel(
          id: 'tx-2',
          volunteerProfileId: 'prof-1',
          totalPoints: 10.0,
          transactionType: 'REGISTRATION_BONUS',
          reason: 'Welcome Onboarding',
          hoursCredited: 0.0,
          cycleYear: 2026,
          createdAt: DateTime(2026, 11, 15, 10, 0),
        ),
      ],
      total: 2,
      page: 1,
      pageSize: 50,
      totalPages: 1,
      netPoints: 60.0,
    );
  }

  @override
  Future<VolunteerAchievementsModel?> getAchievements() async {
    return const VolunteerAchievementsModel(
      items: [
        AchievementModel(
          id: 'ach-1',
          code: 'FIRST_STEP',
          title: 'First Step',
          description:
              'Completed your very first volunteer event with Maatram.',
          iconUrl: '',
          category: 'GENERAL',
          criteriaType: 'EVENTS',
          criteriaThreshold: 1.0,
          isActive: true,
          isEarned: true,
          awardedAt: null,
        ),
        AchievementModel(
          id: 'ach-2',
          code: 'DEDICATED_MENTOR',
          title: 'Dedicated Mentor',
          description:
              'Completed 5 mentoring sessions for high school students.',
          iconUrl: '',
          category: 'EDUCATION',
          criteriaType: 'EVENTS',
          criteriaThreshold: 5.0,
          isActive: true,
          isEarned: true,
          awardedAt: null,
        ),
        AchievementModel(
          id: 'ach-3',
          code: 'CENTURY_CLUB',
          title: 'Century Club',
          description: 'Contribute 100 verified volunteering hours.',
          iconUrl: '',
          category: 'GENERAL',
          criteriaType: 'HOURS',
          criteriaThreshold: 100.0,
          isActive: true,
          isEarned: false,
        ),
      ],
      totalAvailable: 8,
      totalEarned: 2,
    );
  }
}

class CaptureAuthMock extends StateNotifier<AuthState>
    implements AuthController {
  CaptureAuthMock(UserSession session)
      : super(AuthState.authenticated(session));

  UserSession? get user => state.session;
  bool get isAuthenticated => true;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class CaptureHomeMock extends StateNotifier<HomeState>
    implements HomeController {
  CaptureHomeMock(VolunteerProfileModel profile,
      GamificationSummaryModel gamification, List<EventModel> events)
      : super(HomeState(
          profile: AsyncValue.data(profile),
          gamification: AsyncValue.data(gamification),
          events: AsyncValue.data(events),
        ));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({
    'pref_device_event_reminders': true,
    'pref_device_points_alerts': true,
    'pref_device_announcements': true,
    'pref_device_quiet_hours': false,
    'pref_biometrics_enabled': true,
  });

  const sampleSession = UserSession(
    userId: 'usr-1',
    email: 'priya.s@maatram.org',
    role: 'VOLUNTEER',
    status: 'APPROVED',
    accessToken: 'token-abc',
    refreshToken: 'refresh-xyz',
    firstName: 'Priya',
    lastName: 'S',
    category: 'STUDENT',
  );

  const sampleProfile = VolunteerProfileModel(
    id: 'prof-1',
    userId: 'usr-1',
    firstName: 'Priya',
    lastName: 'S',
    age: 20,
    gender: 'FEMALE',
    category: 'STUDENT',
    organizationOrCollege: 'Sathyabama Institute of Science and Technology',
    city: 'Chennai',
    mobileNumber: '+91 98401 23456',
  );

  const sampleGamification = GamificationSummaryModel(
    volunteerProfileId: 'prof-1',
    cycleYear: 2026,
    totalPoints: 180.0,
    totalHours: 24.0,
    completedEventsCount: 5,
    badgesEarnedCount: 3,
    rank: 1,
  );

  final mockEvents = CaptureMockEventsRepo();
  final mockLeaderboard = CaptureMockLeaderboardRepo();
  final mockMore = CaptureMockMoreRepo();
  final mockGamification = CaptureMockGamificationRepo();

  final baseOverrides = [
    authControllerProvider
        .overrideWith((ref) => CaptureAuthMock(sampleSession)),
    homeControllerProvider.overrideWith(
        (ref) => CaptureHomeMock(sampleProfile, sampleGamification, [])),
    eventsRepositoryProvider.overrideWithValue(mockEvents),
    leaderboardRepositoryProvider.overrideWithValue(mockLeaderboard),
    moreRepositoryProvider.overrideWithValue(mockMore),
    gamificationRepositoryProvider.overrideWithValue(mockGamification),
    activityControllerProvider.overrideWith((ref) =>
        ActivityController(eventsRepository: mockEvents, loadOnInit: false)),
    eventsControllerProvider.overrideWith((ref) =>
        EventsController(eventsRepository: mockEvents, loadOnInit: false)),
    leaderboardControllerProvider.overrideWith((ref) => LeaderboardController(
        leaderboardRepository: mockLeaderboard, loadOnInit: false)),
  ];

  Future<void> renderAndSave(
    WidgetTester tester, {
    required Widget widget,
    required String filename,
    double width = 390,
    double height = 844,
    List<dynamic> extraOverrides = const [],
  }) async {
    final boundaryKey = GlobalKey();

    tester.view.physicalSize = Size(width * 2.0, height * 2.0);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          ...baseOverrides,
          ...extraOverrides,
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
    await tester.pump(const Duration(milliseconds: 1000));
    await tester.pump(const Duration(milliseconds: 1000));

    await tester.runAsync(() async {
      final boundary = boundaryKey.currentContext?.findRenderObject()
          as RenderRepaintBoundary?;
      if (boundary == null) return;
      final image = await boundary.toImage(pixelRatio: 1.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      if (byteData == null) return;
      final file = File('../docs/audits/phase4_rendered_screens/$filename');
      file.writeAsBytesSync(byteData.buffer.asUint8List());
    });
  }

  group('Capture All 38 Screens at 390x844', () {
    // Group 1: Authentication
    testWidgets('01 Welcome Splash', (tester) async {
      await renderAndSave(tester,
          widget: const WelcomeSplashScreen(),
          filename: 'screen_01_welcome_splash.png');
    });

    testWidgets('02 Login', (tester) async {
      await renderAndSave(tester,
          widget: const LoginScreen(), filename: 'screen_02_login.png');
    });

    testWidgets('03 Forgot Password', (tester) async {
      await renderAndSave(tester,
          widget: const ForgotPasswordScreen(),
          filename: 'screen_03_forgot_password.png');
    });

    testWidgets('04 Reset Password', (tester) async {
      await renderAndSave(tester,
          widget: const ResetPasswordScreen(),
          filename: 'screen_04_reset_password.png');
    });

    // Group 2: Registration Steps 1-6
    for (int step = 0; step < 6; step++) {
      testWidgets('Registration Step ${step + 1}', (tester) async {
        final regNotifier = RegistrationNotifier();
        regNotifier.state = regNotifier.state.copyWith(
          currentStep: step,
          firstName: 'Priya',
          lastName: 'S',
          email: 'priya.s@maatram.org',
          mobileNumber: '+91 98401 23456',
          age: 20,
          gender: 'FEMALE',
          category: 'STUDENT',
          studentCollegeName: 'Sathyabama Institute of Science and Technology',
          studentDegree: 'B.Tech',
          studentDepartment: 'CSE',
          studentBatchYear: 2024,
          studentCurrentYear: 3,
          studentMaatramRegNo: 'MAT-24-301',
          selectedSkills: ['Mentoring', 'School Visits', 'Communication'],
          availability: 'Weekends',
          leaderboardVisible: true,
          nameVisible: true,
          thankYouEmails: true,
          linkedinContent: false,
          contactAvailable: false,
          mediaUsage: true,
          termsAccepted: true,
        );

        final stepPadded = (step + 5).toString().padLeft(2, '0');
        await renderAndSave(
          tester,
          widget: const RegistrationFlowScreen(),
          filename: 'screen_${stepPadded}_register_step${step + 1}.png',
          extraOverrides: [
            registrationProvider.overrideWith((ref) => regNotifier),
          ],
        );
      });
    }

    // Group 3: Verification & Status
    testWidgets('11 Verify Email', (tester) async {
      await renderAndSave(tester,
          widget: const VerifyEmailScreen(initialEmail: 'priya.s@maatram.org'),
          filename: 'screen_11_verify_email.png');
    });

    testWidgets('12 Pending Verification', (tester) async {
      await renderAndSave(tester,
          widget: const PendingVerificationScreen(),
          filename: 'screen_12_pending_verification.png');
    });

    testWidgets('13 Pending Approval', (tester) async {
      await renderAndSave(tester,
          widget: const PendingApprovalScreen(),
          filename: 'screen_13_pending_approval.png');
    });

    testWidgets('14 Rejected Status', (tester) async {
      await renderAndSave(tester,
          widget: const RejectedScreen(), filename: 'screen_14_rejected.png');
    });

    testWidgets('15 Post-Approval Welcome', (tester) async {
      await renderAndSave(tester,
          widget: const WelcomeScreen(),
          filename: 'screen_15_welcome_approved.png');
    });

    // Group 4: Main Application
    testWidgets('16 Volunteer Home', (tester) async {
      await renderAndSave(tester,
          widget: const HomeScreen(), filename: 'screen_16_home.png');
    });

    testWidgets('17 Events Catalog', (tester) async {
      await renderAndSave(tester,
          widget: const EventsScreen(), filename: 'screen_17_events.png');
    });

    testWidgets('18 Event Details', (tester) async {
      await renderAndSave(tester,
          widget: const EventDetailsScreen(eventId: 'evt-1'),
          filename: 'screen_18_event_details.png');
    });

    testWidgets('19 Event Registration', (tester) async {
      await renderAndSave(tester,
          widget: const EventRegistrationScreen(eventId: 'evt-1'),
          filename: 'screen_19_event_registration.png');
    });

    testWidgets('20 My Activity', (tester) async {
      await renderAndSave(tester,
          widget: const MyActivityScreen(),
          filename: 'screen_20_my_activity.png');
    });

    testWidgets('21 Activity Details', (tester) async {
      final sampleAtt = AttendanceModel(
        id: 'att-1',
        eventId: 'evt-101',
        eventTitle: 'School Visit - Government High School',
        checkInTime: DateTime(2026, 11, 26, 14, 30),
        checkOutTime: DateTime(2026, 11, 26, 18, 30),
        hoursCredited: 4.0,
        status: 'VERIFIED',
      );
      await renderAndSave(tester,
          widget:
              ActivityDetailsScreen(activityId: 'att-1', attendance: sampleAtt),
          filename: 'screen_21_activity_details.png');
    });

    testWidgets('22 Leaderboard', (tester) async {
      await renderAndSave(tester,
          widget: const LeaderboardScreen(),
          filename: 'screen_22_leaderboard.png');
    });

    // Group 5: Volunteer Account
    testWidgets('23 More Hub', (tester) async {
      await renderAndSave(tester,
          widget: const MoreScreen(), filename: 'screen_23_more.png');
    });

    testWidgets('24 Profile', (tester) async {
      await renderAndSave(tester,
          widget: const ProfileScreen(), filename: 'screen_24_profile.png');
    });

    testWidgets('25 Edit Profile', (tester) async {
      await renderAndSave(tester,
          widget: const EditProfileScreen(),
          filename: 'screen_25_edit_profile.png');
    });

    testWidgets('26 Profile Photo', (tester) async {
      await renderAndSave(tester,
          widget: const ProfilePhotoScreen(),
          filename: 'screen_26_profile_photo.png');
    });

    testWidgets('27 Points Overview', (tester) async {
      await renderAndSave(tester,
          widget: const PointsOverviewScreen(),
          filename: 'screen_27_points_overview.png');
    });

    testWidgets('28 Points History', (tester) async {
      await renderAndSave(tester,
          widget: const PointsHistoryScreen(),
          filename: 'screen_28_points_history.png');
    });

    testWidgets('29 Achievements', (tester) async {
      await renderAndSave(tester,
          widget: const AchievementsScreen(),
          filename: 'screen_29_achievements.png');
    });

    testWidgets('30 Achievement Details Modal', (tester) async {
      const sampleBadge = AchievementModel(
        id: 'ach-1',
        code: 'FIRST_STEP',
        title: 'First Step',
        description: 'Completed your very first volunteer event with Maatram.',
        iconUrl: '',
        category: 'GENERAL',
        criteriaType: 'EVENTS',
        criteriaThreshold: 1.0,
        isActive: true,
        isEarned: true,
        awardedAt: null,
      );
      await renderAndSave(
        tester,
        widget: const Scaffold(
          backgroundColor: Color(0xFFFAF8F5),
          body: Center(
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: 24),
              child: AchievementDetailsModal(achievement: sampleBadge),
            ),
          ),
        ),
        filename: 'screen_30_achievement_details.png',
      );
    });

    // Group 6: Notifications & Settings
    testWidgets('31 Notifications', (tester) async {
      await renderAndSave(tester,
          widget: const NotificationsScreen(),
          filename: 'screen_31_notifications.png');
    });

    testWidgets('32 Notification Details', (tester) async {
      final sampleNotif = NotificationModel(
        id: 'n-1',
        userId: 'usr-1',
        title: 'Event Reminder: School Visit',
        message:
            'Your volunteer session begins tomorrow at 2:30 PM. Please arrive 15 minutes early for orientation.',
        type: 'EVENT_REMINDER',
        isRead: false,
        createdAt: DateTime(2026, 11, 25, 10, 0),
      );
      await renderAndSave(tester,
          widget: NotificationDetailsScreen(
              notificationId: 'n-1', notification: sampleNotif),
          filename: 'screen_32_notification_details.png');
    });

    testWidgets('33 Notification Settings', (tester) async {
      await renderAndSave(tester,
          widget: const NotificationSettingsScreen(),
          filename: 'screen_33_notification_settings.png');
    });

    testWidgets('34 Privacy & Consents', (tester) async {
      await renderAndSave(tester,
          widget: const PrivacyScreen(),
          filename: 'screen_34_privacy_consent.png');
    });

    testWidgets('35 App Settings', (tester) async {
      await renderAndSave(tester,
          widget: const AppSettingsScreen(),
          filename: 'screen_35_app_settings.png');
    });

    testWidgets('36 Help & Support', (tester) async {
      await renderAndSave(tester,
          widget: const HelpSupportScreen(),
          filename: 'screen_36_help_support.png');
    });

    testWidgets('37 About Maatram', (tester) async {
      await renderAndSave(tester,
          widget: const AboutMaatramScreen(),
          filename: 'screen_37_about_maatram.png');
    });

    testWidgets('38 Logout Confirmation Dialog', (tester) async {
      await renderAndSave(
        tester,
        widget: Stack(
          children: [
            Container(color: const Color(0xFFFAF8F5)),
            Container(color: const Color(0x66000000)),
            const Align(
              alignment: Alignment.bottomCenter,
              child: LogoutConfirmationDialog(),
            ),
          ],
        ),
        filename: 'screen_38_logout_confirmation.png',
      );
    });
  });
}
