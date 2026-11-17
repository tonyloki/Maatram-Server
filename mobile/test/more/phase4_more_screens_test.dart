import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/auth/auth_controller.dart';
import 'package:maatram_mobile/core/auth/auth_state.dart';
import 'package:maatram_mobile/core/models/consent_model.dart';
import 'package:maatram_mobile/core/models/gamification_summary_model.dart';
import 'package:maatram_mobile/core/models/notification_model.dart';
import 'package:maatram_mobile/core/models/user_session.dart';
import 'package:maatram_mobile/core/models/volunteer_profile_model.dart';
import 'package:maatram_mobile/core/network/api_client.dart';
import 'package:maatram_mobile/features/home/state/home_controller.dart';
import 'package:maatram_mobile/features/more/data/more_repository.dart';
import 'package:maatram_mobile/features/more/presentation/about_maatram_screen.dart';
import 'package:maatram_mobile/features/more/presentation/app_settings_screen.dart';
import 'package:maatram_mobile/features/more/presentation/edit_profile_screen.dart';
import 'package:maatram_mobile/features/more/presentation/help_support_screen.dart';
import 'package:maatram_mobile/features/more/presentation/logout_confirmation_dialog.dart';
import 'package:maatram_mobile/features/more/presentation/notification_details_screen.dart';
import 'package:maatram_mobile/features/more/presentation/notification_settings_screen.dart';
import 'package:maatram_mobile/features/more/presentation/notifications_screen.dart';
import 'package:maatram_mobile/features/more/presentation/privacy_screen.dart';
import 'package:maatram_mobile/features/more/presentation/profile_photo_screen.dart';
import 'package:maatram_mobile/features/more/presentation/profile_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

class MockMoreRepository extends MoreRepository {
  MockMoreRepository() : super(apiClient: ApiClient());

  @override
  Future<NotificationListModel?> getNotifications(
      {bool unreadOnly = false, int page = 1, int limit = 20}) async {
    return NotificationListModel(
      items: [
        NotificationModel(
          id: 'notif-1',
          userId: 'user-1',
          title: 'Event Reminder: School Visit',
          message: 'Your scheduled session begins tomorrow at 9:30 AM.',
          type: 'EVENT_REMINDER',
          isRead: false,
          createdAt: DateTime(2026, 11, 25, 10, 0),
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
  Future<bool> markNotificationAsRead(String id) async => true;

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

  @override
  Future<VolunteerProfileModel?> updateProfile(
      Map<String, dynamic> updateData) async {
    return const VolunteerProfileModel(
      id: 'vol-1',
      userId: 'user-1',
      firstName: 'Karthik',
      lastName: 'Raja',
      age: 21,
      gender: 'MALE',
      category: 'STUDENT',
    );
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({
    'pref_device_event_reminders': true,
    'pref_device_quiet_hours': false,
    'pref_biometrics_enabled': true,
  });

  const sampleSession = UserSession(
    userId: 'user-1',
    email: 'karthik.raja@maatram.org',
    role: 'VOLUNTEER',
    status: 'APPROVED',
    accessToken: 'test-token',
    refreshToken: 'test-refresh',
    firstName: 'Karthik',
    lastName: 'Raja',
    category: 'STUDENT',
  );

  const sampleProfile = VolunteerProfileModel(
    id: 'vol-1',
    userId: 'user-1',
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

  final mockRepo = MockMoreRepository();

  Widget buildTestableWidget(Widget child) {
    return ProviderScope(
      overrides: [
        moreRepositoryProvider.overrideWithValue(mockRepo),
        authControllerProvider
            .overrideWith((ref) => AuthNotifierMock(sampleSession)),
        homeControllerProvider.overrideWith(
            (ref) => HomeControllerMock(sampleProfile, sampleGamification)),
      ],
      child: MaterialApp(
        home: child,
      ),
    );
  }

  group('Phase 4 Volunteer Account & Settings Tests', () {
    testWidgets('ProfileScreen displays dynamic user profile and stats',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(buildTestableWidget(const ProfileScreen()));
      await tester.pumpAndSettle();

      expect(find.text('Karthik Raja'), findsNWidgets(2));
      expect(find.text('180'), findsOneWidget);
      expect(find.text('24'), findsOneWidget);
      expect(find.text('Edit Profile Information'), findsOneWidget);
    });

    testWidgets(
        'EditProfileScreen displays identity fields and allows updating contacts',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(buildTestableWidget(const EditProfileScreen()));
      await tester.pumpAndSettle();

      expect(find.text('Edit Profile'), findsOneWidget);
      expect(find.text('Karthik Raja'), findsOneWidget);
      expect(find.text('karthik.raja@maatram.org'), findsOneWidget);
      expect(find.text('Save Changes'), findsOneWidget);
    });

    testWidgets(
        'ProfilePhotoScreen displays photo guidelines and upload button',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(buildTestableWidget(const ProfilePhotoScreen()));
      await tester.pumpAndSettle();

      expect(find.text('Profile Photo'), findsOneWidget);
      expect(find.text('Photo Guidelines'), findsOneWidget);
      expect(find.text('Upload New Photo'), findsOneWidget);
    });

    testWidgets('NotificationsScreen displays unread notifications list',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(buildTestableWidget(const NotificationsScreen()));
      await tester.pumpAndSettle();

      expect(find.text('Notifications'), findsOneWidget);
      expect(find.text('Event Reminder: School Visit'), findsOneWidget);
    });

    testWidgets('NotificationDetailsScreen displays full notification content',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final notification = NotificationModel(
        id: 'notif-1',
        userId: 'user-1',
        title: 'Event Reminder: School Visit',
        message: 'Your scheduled session begins tomorrow at 9:30 AM.',
        type: 'EVENT_REMINDER',
        isRead: false,
        createdAt: DateTime(2026, 11, 25, 10, 0),
      );

      await tester.pumpWidget(buildTestableWidget(NotificationDetailsScreen(
        notificationId: 'notif-1',
        notification: notification,
      )));
      await tester.pumpAndSettle();

      expect(find.text('Event Reminder: School Visit'), findsOneWidget);
      expect(find.text('Your scheduled session begins tomorrow at 9:30 AM.'),
          findsOneWidget);
    });

    testWidgets('NotificationSettingsScreen displays local preference switches',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester
          .pumpWidget(buildTestableWidget(const NotificationSettingsScreen()));
      await tester.pumpAndSettle();

      expect(find.text('Notification Settings'), findsOneWidget);
      expect(find.text('Event Reminders'), findsOneWidget);
      expect(find.text('Quiet Hours (10 PM – 7 AM)'), findsOneWidget);
    });

    testWidgets(
        'PrivacyScreen displays statutory consent dimensions and persistence notice',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(buildTestableWidget(const PrivacyScreen()));
      await tester.pumpAndSettle();

      expect(find.text('Privacy & Consents'), findsOneWidget);
      expect(find.text('Public Leaderboard Visibility'), findsOneWidget);
      expect(find.text('Event Impact & Thank-You Emails'), findsOneWidget);
      expect(find.text('Event Photography & Media Usage'), findsOneWidget);
    });

    testWidgets(
        'AppSettingsScreen displays app info and biometric security switch',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(buildTestableWidget(const AppSettingsScreen()));
      await tester.pumpAndSettle();

      expect(find.text('Settings'), findsOneWidget);
      expect(find.text('Biometric Authentication'), findsOneWidget);
      expect(find.text('Application Version'), findsOneWidget);
    });

    testWidgets(
        'HelpSupportScreen displays verified FAQ and configurable contact intent',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(buildTestableWidget(const HelpSupportScreen()));
      await tester.pumpAndSettle();

      expect(find.text('Help & Support'), findsOneWidget);
      expect(find.text('Frequently Asked Questions'), findsOneWidget);
      expect(find.text('How are Karma Points calculated?'), findsOneWidget);
      expect(find.text('Email Support Team'), findsOneWidget);

      // Verify ZERO unverified WhatsApp numbers are displayed
      expect(find.text('+91 9876543210'), findsNothing);
      expect(find.text('+91 98765 43210'), findsNothing);
    });

    testWidgets('AboutMaatramScreen displays mission and impact statistics',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(buildTestableWidget(const AboutMaatramScreen()));
      await tester.pumpAndSettle();

      expect(find.text('About Maatram'), findsOneWidget);
      expect(find.text('Our Mission'), findsOneWidget);
      expect(find.text('3,500+'), findsOneWidget);
      expect(find.text('1,200+'), findsOneWidget);
      expect(find.text('50,000+'), findsOneWidget);
    });

    testWidgets(
        'LogoutConfirmationDialog displays sign out confirmation and session termination copy',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: const LogoutConfirmationDialog(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Sign Out of Maatram?'), findsOneWidget);
      expect(find.text('Sign Out'), findsOneWidget);
      expect(find.text('Cancel'), findsOneWidget);
    });
  });
}

class AuthNotifierMock extends StateNotifier<AuthState>
    implements AuthController {
  AuthNotifierMock(UserSession session)
      : super(AuthState.authenticated(session));

  UserSession? get user => state.session;

  bool get isAuthenticated => true;

  Future<void> checkAuthStatus() async {}

  @override
  Future<void> logout() async {
    state = const AuthState.unauthenticated();
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class HomeControllerMock extends StateNotifier<HomeState>
    implements HomeController {
  HomeControllerMock(
      VolunteerProfileModel profile, GamificationSummaryModel gamification)
      : super(HomeState(
          profile: AsyncValue.data(profile),
          gamification: AsyncValue.data(gamification),
          events: const AsyncValue.data([]),
        ));

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
