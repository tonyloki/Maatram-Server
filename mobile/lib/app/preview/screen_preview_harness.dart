import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Core imports
import '../../core/models/notification_model.dart';
import '../../core/widgets/navigation/bottom_nav_bar.dart';

// Group 1: Authentication
import '../../features/onboarding/presentation/welcome_splash_screen.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/presentation/forgot_password_screen.dart';
import '../../features/auth/presentation/reset_password_screen.dart';

// Group 2: Registration
import '../../features/registration/presentation/registration_flow_screen.dart';
import '../../features/registration/state/registration_state.dart';

// Group 3: Verification
import '../../features/auth/presentation/verify_email_screen.dart';
import '../../features/onboarding/presentation/pending_verification_screen.dart';
import '../../features/onboarding/presentation/pending_approval_screen.dart';
import '../../features/onboarding/presentation/rejected_screen.dart';
import '../../features/onboarding/presentation/welcome_screen.dart';

// Group 4: Main Application
import '../../features/home/presentation/home_screen.dart';
import '../../features/events/presentation/events_screen.dart';
import '../../features/events/presentation/event_details_screen.dart';
import '../../features/events/presentation/event_registration_screen.dart';
import '../../features/events/presentation/my_activity_screen.dart';
import '../../features/events/presentation/activity_details_screen.dart';
import '../../features/leaderboard/presentation/leaderboard_screen.dart';
import '../../features/more/presentation/more_screen.dart';

// Group 5: Volunteer Account
import '../../features/more/presentation/profile_screen.dart';
import '../../features/more/presentation/edit_profile_screen.dart';
import '../../features/more/presentation/profile_photo_screen.dart';
import '../../features/gamification/presentation/points_overview_screen.dart';
import '../../features/gamification/presentation/points_history_screen.dart';
import '../../features/gamification/presentation/achievements_screen.dart';

// Group 6: Notifications & Settings
import '../../features/more/presentation/notifications_screen.dart';
import '../../features/more/presentation/notification_details_screen.dart';
import '../../features/more/presentation/notification_settings_screen.dart';
import '../../features/more/presentation/privacy_screen.dart';
import '../../features/more/presentation/app_settings_screen.dart';
import '../../features/more/presentation/help_support_screen.dart';
import '../../features/more/presentation/about_maatram_screen.dart';

/// Screen Preview Harness rendering any of the 38 screens in an isolated,
/// authentic environment at 390x844 with populated sample data matching references.
class ScreenPreviewHarness extends StatelessWidget {
  final String screenId;

  const ScreenPreviewHarness({super.key, required this.screenId});

  @override
  Widget build(BuildContext context) {
    final normalized = screenId.toLowerCase().trim();

    return _buildScreen(normalized);
  }

  Widget _buildScreen(String id) {
    // Group 1: Authentication
    if (id.contains('welcome_splash') || id == '01') {
      return const WelcomeSplashScreen();
    }
    if (id.contains('login') || id == '02') {
      return const LoginScreen();
    }
    if (id.contains('forgot_password') || id == '03') {
      return const ForgotPasswordScreen();
    }
    if (id.contains('reset_password') || id == '04') {
      return const ResetPasswordScreen(initialEmail: 'volunteer@maatram.org');
    }

    // Group 2: Registration (Steps 1 to 6)
    if (id.contains('registration_basic_details') || id == '05') {
      return _buildRegistrationStep(0);
    }
    if (id.contains('registration_category_details') || id == '07') {
      return _buildRegistrationStep(2);
    }
    if (id.contains('registration_category') || id == '06') {
      return _buildRegistrationStep(1);
    }
    if (id.contains('registration_skills_availability') || id == '08') {
      return _buildRegistrationStep(3);
    }
    if (id.contains('registration_privacy_consent') || id == '09') {
      return _buildRegistrationStep(4);
    }
    if (id.contains('registration_review_submit') || id == '10') {
      return _buildRegistrationStep(5);
    }

    // Group 3: Verification
    if (id.contains('email_verification') || id == '11') {
      return const VerifyEmailScreen(initialEmail: 'volunteer@maatram.org');
    }
    if (id.contains('pending_verification') || id == '12') {
      return const PendingVerificationScreen();
    }
    if (id.contains('pending_approval') || id == '13') {
      return const PendingApprovalScreen();
    }
    if (id.contains('application_rejected') || id == '14') {
      return const RejectedScreen();
    }
    if (id.contains('post_approval_welcome') || id == '15') {
      return const WelcomeScreen();
    }

    // Group 4: Main Application
    if (id.contains('home') || id == '16') {
      return _wrapWithBottomNav(const HomeScreen(), 0);
    }
    if (id.contains('events') && !id.contains('details') && !id.contains('registration') || id == '17') {
      return _wrapWithBottomNav(const EventsScreen(), 1);
    }
    if (id.contains('event_details') || id == '18') {
      return const EventDetailsScreen(eventId: 'event-school-visit');
    }
    if (id.contains('event_registration') || id == '19') {
      return const EventRegistrationScreen(eventId: 'event-school-visit');
    }
    if (id.contains('my_activity') || id == '20') {
      return const MyActivityScreen();
    }
    if (id.contains('activity_details') || id == '21') {
      return const ActivityDetailsScreen(activityId: 'act-1');
    }
    if (id.contains('leaderboard') || id == '22') {
      return _wrapWithBottomNav(const LeaderboardScreen(), 2);
    }
    if (id.contains('more') || id == '23') {
      return _wrapWithBottomNav(const MoreScreen(), 3);
    }

    // Group 5: Volunteer Account
    if (id.contains('profile_photo') || id == '26') {
      return const ProfilePhotoScreen();
    }
    if (id.contains('edit_profile') || id == '25') {
      return const EditProfileScreen();
    }
    if (id.contains('profile') || id == '24') {
      return const ProfileScreen();
    }
    if (id.contains('points_history') || id == '28') {
      return const PointsHistoryScreen();
    }
    if (id.contains('points') || id == '27') {
      return const PointsOverviewScreen();
    }
    if (id.contains('achievement_details') || id == '30') {
      return _buildAchievementDetailsPreview();
    }
    if (id.contains('achievements') || id == '29') {
      return const AchievementsScreen();
    }

    // Group 6: Notifications & Settings
    if (id.contains('notification_details') || id == '32') {
      return NotificationDetailsScreen(
        notificationId: 'notif-1',
        notification: NotificationModel(
          id: 'notif-1',
          userId: 'user-1',
          title: 'Event Reminder: School Visit',
          message: 'Your registered volunteering event "School Visit – Government High School" is scheduled for tomorrow at 2:30 PM.',
          type: 'EVENT_REMINDER',
          isRead: false,
          createdAt: DateTime(2026, 11, 25, 10, 0),
        ),
      );
    }
    if (id.contains('notification_settings') || id == '33') {
      return const NotificationSettingsScreen();
    }
    if (id.contains('notifications') || id == '31') {
      return const NotificationsScreen();
    }
    if (id.contains('privacy_consent') || id == '34') {
      return const PrivacyScreen();
    }
    if (id.contains('settings') || id == '35') {
      return const AppSettingsScreen();
    }
    if (id.contains('help_support') || id == '36') {
      return const HelpSupportScreen();
    }
    if (id.contains('about_maatram') || id == '37') {
      return const AboutMaatramScreen();
    }
    if (id.contains('logout_confirmation') || id == '38') {
      return _buildLogoutConfirmationPreview();
    }

    return Scaffold(
      body: Center(
        child: Text('Screen not found: $id'),
      ),
    );
  }

  Widget _wrapWithBottomNav(Widget child, int index) {
    return Scaffold(
      body: child,
      bottomNavigationBar: MaatramBottomNavBar(
        currentIndex: index,
        onDestinationSelected: (_) {},
      ),
    );
  }

  Widget _buildRegistrationStep(int stepIndex) {
    return ProviderScope(
      overrides: [
        registrationProvider.overrideWith((ref) {
          final notifier = RegistrationNotifier();
          for (int i = 0; i < stepIndex; i++) {
            notifier.nextStep();
          }
          return notifier;
        }),
      ],
      child: const RegistrationFlowScreen(),
    );
  }

  Widget _buildAchievementDetailsPreview() {
    return Scaffold(
      backgroundColor: const Color(0xFFFAF8F5),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: const BackButton(color: Color(0xFF1B2B48)),
        title: const Text(
          'Achievement Details',
          style: TextStyle(
            fontFamily: 'Georgia',
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1B2B48),
          ),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: Container(
          margin: const EdgeInsets.all(24),
          padding: const EdgeInsets.all(28),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: const Color(0xFFEFECE6)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.06),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 96,
                height: 96,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: const Color(0xFFF5B817).withOpacity(0.15),
                  border: Border.all(color: const Color(0xFFF5B817), width: 2),
                ),
                child: const Icon(
                  Icons.emoji_events,
                  size: 52,
                  color: Color(0xFFD49504),
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'First Step Hero',
                style: TextStyle(
                  fontFamily: 'Georgia',
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1B2B48),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Completed your very first volunteer event with Maatram Foundation.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: Color(0xFF827D73),
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFF5B817).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Text(
                  '+50 Points Earned',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFB57E00),
                    fontSize: 14,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Unlocked on 15 Oct 2026',
                style: TextStyle(fontSize: 12, color: Color(0xFF827D73)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLogoutConfirmationPreview() {
    return Scaffold(
      backgroundColor: Colors.black.withOpacity(0.4),
      body: Align(
        alignment: Alignment.bottomCenter,
        child: Container(
          padding: const EdgeInsets.fromLTRB(24, 28, 24, 36),
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFECE6),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Center(
                child: Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    color: const Color(0xFFDC2626).withOpacity(0.12),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.logout_rounded,
                    color: Color(0xFFDC2626),
                    size: 32,
                  ),
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'Sign Out Confirmation',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'Georgia',
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1B2B48),
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Are you sure you want to sign out of your Maatram Volunteer account? You will need to sign in again to access your dashboard.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: Color(0xFF827D73),
                  height: 1.45,
                ),
              ),
              const SizedBox(height: 28),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        side: const BorderSide(color: Color(0xFFEFECE6)),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                      ),
                      onPressed: () {},
                      child: const Text(
                        'Cancel',
                        style: TextStyle(
                          color: Color(0xFF1B2B48),
                          fontWeight: FontWeight.w600,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFDC2626),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                      ),
                      onPressed: () {},
                      child: const Text(
                        'Sign Out',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
