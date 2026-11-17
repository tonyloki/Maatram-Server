import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/consent_model.dart';
import 'package:maatram_mobile/core/models/event_model.dart';
import 'package:maatram_mobile/core/models/gamification_summary_model.dart';
import 'package:maatram_mobile/core/models/notification_model.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/core/models/volunteer_profile_model.dart';
import 'package:maatram_mobile/core/network/api_client.dart';
import 'package:maatram_mobile/features/events/data/events_repository.dart';
import 'package:maatram_mobile/features/events/presentation/activity_details_screen.dart';
import 'package:maatram_mobile/features/events/presentation/event_details_screen.dart';
import 'package:maatram_mobile/features/events/presentation/event_registration_screen.dart';
import 'package:maatram_mobile/features/gamification/data/gamification_repository.dart';
import 'package:maatram_mobile/features/gamification/presentation/achievements_screen.dart';
import 'package:maatram_mobile/features/gamification/presentation/points_history_screen.dart';
import 'package:maatram_mobile/features/gamification/presentation/points_overview_screen.dart';
import 'package:maatram_mobile/features/home/state/home_controller.dart';
import 'package:maatram_mobile/features/more/data/more_repository.dart';
import 'package:maatram_mobile/features/more/presentation/about_maatram_screen.dart';
import 'package:maatram_mobile/features/more/presentation/app_settings_screen.dart';
import 'package:maatram_mobile/features/more/presentation/edit_profile_screen.dart';
import 'package:maatram_mobile/features/more/presentation/help_support_screen.dart';
import 'package:maatram_mobile/features/more/presentation/notification_details_screen.dart';
import 'package:maatram_mobile/features/more/presentation/notification_settings_screen.dart';
import 'package:maatram_mobile/features/more/presentation/notifications_screen.dart';
import 'package:maatram_mobile/features/more/presentation/privacy_screen.dart';
import 'package:maatram_mobile/features/more/presentation/profile_photo_screen.dart';
import 'package:maatram_mobile/features/more/presentation/profile_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ResponsiveMockMoreRepo extends MoreRepository {
  ResponsiveMockMoreRepo() : super(apiClient: ApiClient());

  @override
  Future<NotificationListModel?> getNotifications(
      {bool unreadOnly = false, int page = 1, int limit = 20}) async {
    return NotificationListModel(
      items: [
        NotificationModel(
          id: 'n-1',
          userId: 'u-1',
          title: 'Special Announcement',
          message: 'Volunteer briefing at 10 AM.',
          type: 'ANNOUNCEMENT',
          isRead: false,
          createdAt: DateTime(2026, 11, 20),
        ),
      ],
      total: 1,
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
      volunteerProfileId: 'vol-1',
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

  @override
  Future<ConsentModel?> updateConsent(ConsentModel update) async => update;
}

class ResponsiveMockGamificationRepo extends GamificationRepository {
  ResponsiveMockGamificationRepo() : super(apiClient: ApiClient());

  Future<List<Map<String, dynamic>>> getLedgerTransactions(
      {int page = 1, int limit = 50}) async {
    return [
      {
        'id': 'tx-1',
        'points_awarded': 50.0,
        'points_type': 'EVENT_ATTENDANCE',
        'created_at': '2026-11-20T10:00:00Z',
      },
    ];
  }

  Future<List<Map<String, dynamic>>> getBadges() async {
    return [
      {
        'id': 'b-1',
        'title': 'First Step',
        'description': 'Completed first event',
        'unlocked': true,
      },
    ];
  }
}

class ResponsiveMockEventsRepo extends EventsRepository {
  ResponsiveMockEventsRepo() : super(apiClient: ApiClient());

  Future<EventModel?> getEvent(String id) async {
    return EventModel(
      id: id,
      title: 'School Visit - Government High School',
      description: 'Career guidance and mentorship session.',
      category: 'STUDENT',
      mode: 'OFFLINE',
      locationName: 'Government High School',
      address: 'Ashok Nagar, Chennai',
      city: 'Chennai',
      startTime: DateTime(2026, 11, 26, 9, 30),
      endTime: DateTime(2026, 11, 26, 14, 30),
      maxVolunteers: 30,
      registeredCount: 12,
      status: 'PUBLISHED',
    );
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});

  const sampleSession = UserSession(
    userId: 'u-1',
    email: 'karthik@maatram.org',
    role: 'VOLUNTEER',
    status: 'APPROVED',
    accessToken: 'token',
    refreshToken: 'refresh',
    firstName: 'Karthik',
    lastName: 'Raja',
    category: 'STUDENT',
  );

  const sampleProfile = VolunteerProfileModel(
    id: 'vol-1',
    userId: 'u-1',
    firstName: 'Karthik',
    lastName: 'Raja',
    age: 21,
    gender: 'MALE',
    category: 'STUDENT',
    city: 'Chennai',
    mobileNumber: '+91 98401 23456',
    organizationOrCollege: 'Anna University',
  );

  const sampleGamification = GamificationSummaryModel(
    volunteerProfileId: 'vol-1',
    cycleYear: 2026,
    totalPoints: 180.0,
    totalHours: 24.0,
    completedEventsCount: 5,
    badgesEarnedCount: 4,
    rank: 1,
  );

  final mockMoreRepo = ResponsiveMockMoreRepo();
  final mockGamificationRepo = ResponsiveMockGamificationRepo();
  final mockEventsRepo = ResponsiveMockEventsRepo();

  final testOverrides = [
    moreRepositoryProvider.overrideWithValue(mockMoreRepo),
    gamificationRepositoryProvider.overrideWithValue(mockGamificationRepo),
    eventsRepositoryProvider.overrideWithValue(mockEventsRepo),
    authControllerProvider
        .overrideWith((ref) => ResponsiveAuthMock(sampleSession)),
    homeControllerProvider.overrideWith(
        (ref) => ResponsiveHomeMock(sampleProfile, sampleGamification)),
  ];

  const viewports = <String, Size>{
    '320dp (Compact / SE)': Size(320, 568),
    '360dp (Standard Android)': Size(360, 800),
    '390dp (Standard iPhone)': Size(390, 844),
    '430dp (Pro Max / Plus)': Size(430, 932),
  };

  group('Phase 4 Multi-Viewport Zero-Overflow Verification', () {
    for (final vp in viewports.entries) {
      final name = vp.key;
      final size = vp.value;

      void setViewport(WidgetTester tester) {
        tester.view.physicalSize = Size(size.width * 2, size.height * 2);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });
      }

      Widget wrap(Widget child) {
        return ProviderScope(
          overrides: testOverrides,
          child: MaterialApp(
            home: child,
          ),
        );
      }

      testWidgets('Event screens render with 0 overflow at $name',
          (tester) async {
        setViewport(tester);

        await tester
            .pumpWidget(wrap(const EventDetailsScreen(eventId: 'ev-1')));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester
            .pumpWidget(wrap(const EventRegistrationScreen(eventId: 'ev-1')));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester
            .pumpWidget(wrap(const ActivityDetailsScreen(activityId: 'act-1')));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);
      });

      testWidgets('Gamification screens render with 0 overflow at $name',
          (tester) async {
        setViewport(tester);

        await tester.pumpWidget(wrap(const PointsOverviewScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(wrap(const PointsHistoryScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(wrap(const AchievementsScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);
      });

      testWidgets(
          'Profile and Settings screens render with 0 overflow at $name',
          (tester) async {
        setViewport(tester);

        await tester.pumpWidget(wrap(const ProfileScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(wrap(const EditProfileScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(wrap(const ProfilePhotoScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(wrap(const NotificationsScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(
            wrap(const NotificationDetailsScreen(notificationId: 'notif-1')));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(wrap(const NotificationSettingsScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(wrap(const PrivacyScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(wrap(const AppSettingsScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(wrap(const HelpSupportScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);

        await tester.pumpWidget(wrap(const AboutMaatramScreen()));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 300));
        expect(tester.takeException(), isNull);
      });
    }
  });
}

class ResponsiveAuthMock extends StateNotifier<AuthState>
    implements AuthController {
  ResponsiveAuthMock(UserSession session)
      : super(AuthState.authenticated(session));

  UserSession? get user => state.session;

  bool get isAuthenticated => true;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class ResponsiveHomeMock extends StateNotifier<HomeState>
    implements HomeController {
  ResponsiveHomeMock(
      VolunteerProfileModel profile, GamificationSummaryModel gamification)
      : super(HomeState(
          profile: AsyncValue.data(profile),
          gamification: AsyncValue.data(gamification),
          events: const AsyncValue.data([]),
        ));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
