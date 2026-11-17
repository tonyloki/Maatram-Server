import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/auth/auth_controller.dart';
import '../../core/models/attendance_model.dart';
import '../../core/models/event_model.dart';
import '../../core/models/notification_model.dart';
import '../../core/widgets/navigation/bottom_nav_bar.dart';
import '../../features/auth/presentation/forgot_password_screen.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/presentation/reset_password_screen.dart';
import '../../features/auth/presentation/verify_email_screen.dart';
import '../../features/dev_showcase/presentation/dev_showcase_screen.dart';
import '../../features/events/presentation/activity_details_screen.dart';
import '../../features/events/presentation/event_details_screen.dart';
import '../../features/events/presentation/event_registration_screen.dart';
import '../../features/events/presentation/events_screen.dart';
import '../../features/events/presentation/my_activity_screen.dart';
import '../../features/gamification/presentation/achievements_screen.dart';
import '../../features/gamification/presentation/points_history_screen.dart';
import '../../features/gamification/presentation/points_overview_screen.dart';
import '../../features/home/presentation/home_screen.dart';
import '../../features/leaderboard/presentation/leaderboard_screen.dart';
import '../../features/more/presentation/about_maatram_screen.dart';
import '../../features/more/presentation/app_settings_screen.dart';
import '../../features/more/presentation/edit_profile_screen.dart';
import '../../features/more/presentation/help_support_screen.dart';
import '../../features/more/presentation/more_screen.dart';
import '../../features/more/presentation/notification_details_screen.dart';
import '../../features/more/presentation/notification_settings_screen.dart';
import '../../features/more/presentation/notifications_screen.dart';
import '../../features/more/presentation/privacy_screen.dart';
import '../../features/more/presentation/profile_photo_screen.dart';
import '../../features/more/presentation/profile_screen.dart';
import '../../features/onboarding/presentation/pending_approval_screen.dart';
import '../../features/onboarding/presentation/pending_verification_screen.dart';
import '../../features/onboarding/presentation/rejected_screen.dart';
import '../../features/onboarding/presentation/welcome_screen.dart';
import '../../features/onboarding/presentation/welcome_splash_screen.dart';
import '../../features/registration/presentation/registration_flow_screen.dart';
import '../preview/screen_preview_harness.dart';
import 'route_names.dart';

final rootNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'rootNav');

class RouterNotifier extends ChangeNotifier {
  final Ref _ref;

  RouterNotifier(this._ref) {
    _ref.listen(authControllerProvider, (_, __) => notifyListeners());
  }
}

final routerNotifierProvider = Provider<RouterNotifier>((ref) {
  return RouterNotifier(ref);
});

final appRouterProvider = Provider<GoRouter>((ref) {
  final notifier = ref.watch(routerNotifierProvider);

  return GoRouter(
    navigatorKey: rootNavigatorKey,
    initialLocation: RouteNames.welcomeSplashPath,
    refreshListenable: notifier,
    debugLogDiagnostics: false,
    redirect: (context, state) {
      final authState = ref.read(authControllerProvider);
      final location = state.uri.path;

      // Allow dev showcase and screen preview without auth constraints for testing & visual verification
      if (location == RouteNames.devShowcasePath || location == '/preview') return null;

      final isPublicAuthRoute = location == RouteNames.welcomeSplashPath ||
          location == RouteNames.loginPath ||
          location == RouteNames.registerPath ||
          location == RouteNames.verifyEmailPath ||
          location == RouteNames.forgotPasswordPath ||
          location == RouteNames.resetPasswordPath;

      final isOnboardingRoute =
          location == RouteNames.pendingVerificationPath ||
              location == RouteNames.pendingApprovalPath ||
              location == RouteNames.welcomePath ||
              location == RouteNames.rejectedPath;

      // 1. Unauthenticated users
      if (!authState.isAuthenticated) {
        // If loading, let it proceed to avoid flashing
        if (authState.isLoading) return null;
        if (isPublicAuthRoute) return null;
        return RouteNames.welcomeSplashPath;
      }

      // 2. Authenticated users
      final user = authState.user;
      final status = user?.status ?? '';

      // Post-auth routing based on account verification & approval
      if (status == 'PENDING_VERIFICATION') {
        if (location == RouteNames.verifyEmailPath) return null;
        if (location != RouteNames.pendingVerificationPath) {
          return RouteNames.pendingVerificationPath;
        }
        return null;
      }

      if (status == 'PENDING_ADMIN_APPROVAL' ||
          status == 'PENDING_APPROVAL' ||
          status == 'PENDING') {
        if (location != RouteNames.pendingApprovalPath) {
          return RouteNames.pendingApprovalPath;
        }
        return null;
      }

      if (status == 'REJECTED') {
        if (location != RouteNames.rejectedPath) {
          return RouteNames.rejectedPath;
        }
        return null;
      }

      // Approved user
      if (authState.isFirstLaunch && location == RouteNames.welcomeSplashPath) {
        return RouteNames.welcomePath;
      }

      // If approved user is trying to access auth or onboarding pages, send to home
      if (isPublicAuthRoute ||
          (isOnboardingRoute && !authState.isFirstLaunch)) {
        return RouteNames.homePath;
      }

      return null;
    },
    routes: [
      // Welcome & Splash (Public Entry Screen)
      GoRoute(
        path: RouteNames.welcomeSplashPath,
        name: RouteNames.welcomeSplash,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const WelcomeSplashScreen(),
      ),

      // Authentication Routes
      GoRoute(
        path: RouteNames.loginPath,
        name: RouteNames.login,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: RouteNames.registerPath,
        name: RouteNames.register,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const RegistrationFlowScreen(),
      ),
      GoRoute(
        path: RouteNames.verifyEmailPath,
        name: RouteNames.verifyEmail,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) {
          final email = state.uri.queryParameters['email'];
          final token = state.uri.queryParameters['token'];
          return VerifyEmailScreen(initialEmail: email, initialToken: token);
        },
      ),
      GoRoute(
        path: RouteNames.forgotPasswordPath,
        name: RouteNames.forgotPassword,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const ForgotPasswordScreen(),
      ),
      GoRoute(
        path: RouteNames.resetPasswordPath,
        name: RouteNames.resetPassword,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) {
          final email = state.uri.queryParameters['email'];
          return ResetPasswordScreen(initialEmail: email);
        },
      ),

      // Onboarding & Status Screens
      GoRoute(
        path: RouteNames.pendingVerificationPath,
        name: RouteNames.pendingVerification,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const PendingVerificationScreen(),
      ),
      GoRoute(
        path: RouteNames.pendingApprovalPath,
        name: RouteNames.pendingApproval,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const PendingApprovalScreen(),
      ),
      GoRoute(
        path: RouteNames.welcomePath,
        name: RouteNames.welcome,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const WelcomeScreen(),
      ),
      GoRoute(
        path: RouteNames.rejectedPath,
        name: RouteNames.rejected,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const RejectedScreen(),
      ),

      // 4-Destination Persistent Navigation Shell using StatefulShellRoute
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return Scaffold(
            body: navigationShell,
            bottomNavigationBar: MaatramBottomNavBar(
              currentIndex: navigationShell.currentIndex,
              onDestinationSelected: (index) {
                navigationShell.goBranch(
                  index,
                  initialLocation: index == navigationShell.currentIndex,
                );
              },
            ),
          );
        },
        branches: [
          // 1. Home
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteNames.homePath,
                name: RouteNames.home,
                builder: (context, state) => const HomeScreen(),
              ),
            ],
          ),
          // 2. Events
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteNames.eventsPath,
                name: RouteNames.events,
                builder: (context, state) => const EventsScreen(),
              ),
            ],
          ),
          // 3. Leaderboard
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteNames.leaderboardPath,
                name: RouteNames.leaderboard,
                builder: (context, state) => const LeaderboardScreen(),
              ),
            ],
          ),
          // 4. More
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteNames.morePath,
                name: RouteNames.more,
                builder: (context, state) => const MoreScreen(),
              ),
            ],
          ),
        ],
      ),

      // Secondary Feature Routes
      GoRoute(
        path: RouteNames.activityPath,
        name: RouteNames.activity,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const MyActivityScreen(),
      ),
      GoRoute(
        path: RouteNames.activityDetailsPath,
        name: RouteNames.activityDetails,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          final attendance = state.extra as AttendanceModel?;
          return ActivityDetailsScreen(activityId: id, attendance: attendance);
        },
      ),
      GoRoute(
        path: RouteNames.eventDetailsPath,
        name: RouteNames.eventDetails,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return EventDetailsScreen(eventId: id);
        },
      ),
      GoRoute(
        path: RouteNames.eventRegistrationPath,
        name: RouteNames.eventRegistration,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          final event = state.extra as EventModel?;
          return EventRegistrationScreen(eventId: id, event: event);
        },
      ),
      GoRoute(
        path: RouteNames.profilePath,
        name: RouteNames.profile,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: RouteNames.editProfilePath,
        name: RouteNames.editProfile,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const EditProfileScreen(),
      ),
      GoRoute(
        path: RouteNames.profilePhotoPath,
        name: RouteNames.profilePhoto,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const ProfilePhotoScreen(),
      ),
      GoRoute(
        path: RouteNames.pointsOverviewPath,
        name: RouteNames.pointsOverview,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const PointsOverviewScreen(),
      ),
      GoRoute(
        path: RouteNames.pointsHistoryPath,
        name: RouteNames.pointsHistory,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const PointsHistoryScreen(),
      ),
      GoRoute(
        path: RouteNames.achievementsPath,
        name: RouteNames.achievements,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const AchievementsScreen(),
      ),
      GoRoute(
        path: RouteNames.privacyPath,
        name: RouteNames.privacy,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const PrivacyScreen(),
      ),
      GoRoute(
        path: RouteNames.notificationsPath,
        name: RouteNames.notifications,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const NotificationsScreen(),
      ),
      GoRoute(
        path: RouteNames.notificationDetailsPath,
        name: RouteNames.notificationDetails,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          final notification = state.extra as NotificationModel?;
          return NotificationDetailsScreen(
              notificationId: id, notification: notification);
        },
      ),
      GoRoute(
        path: RouteNames.notificationSettingsPath,
        name: RouteNames.notificationSettings,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const NotificationSettingsScreen(),
      ),
      GoRoute(
        path: RouteNames.appSettingsPath,
        name: RouteNames.appSettings,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const AppSettingsScreen(),
      ),
      GoRoute(
        path: RouteNames.helpSupportPath,
        name: RouteNames.helpSupport,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const HelpSupportScreen(),
      ),
      GoRoute(
        path: RouteNames.aboutMaatramPath,
        name: RouteNames.aboutMaatram,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const AboutMaatramScreen(),
      ),

      // Screen Preview Route for Phase 5 Visual Verification
      GoRoute(
        path: '/preview',
        name: 'screenPreview',
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) {
          final screen = state.uri.queryParameters['screen'] ?? '01_welcome_splash';
          return ScreenPreviewHarness(screenId: screen);
        },
      ),

      // Developer Design Showcase Route
      GoRoute(
        path: RouteNames.devShowcasePath,
        name: RouteNames.devShowcase,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const DevShowcaseScreen(),
      ),
    ],
  );
});
