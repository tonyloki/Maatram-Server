/// Type-safe route identifiers and path definitions for GoRouter.
abstract final class RouteNames {
  // Core Tabs
  static const String home = 'home';
  static const String homePath = '/home';

  static const String events = 'events';
  static const String eventsPath = '/events';

  static const String leaderboard = 'leaderboard';
  static const String leaderboardPath = '/leaderboard';

  static const String more = 'more';
  static const String morePath = '/more';

  // Secondary Feature Routes
  static const String activity = 'activity';
  static const String activityPath = '/activity';

  static const String activityDetails = 'activityDetails';
  static const String activityDetailsPath = '/activity/:id';

  static const String eventDetails = 'eventDetails';
  static const String eventDetailsPath = '/events/:id';

  static const String eventRegistration = 'eventRegistration';
  static const String eventRegistrationPath = '/events/:id/register';

  static const String profile = 'profile';
  static const String profilePath = '/profile';

  static const String editProfile = 'editProfile';
  static const String editProfilePath = '/profile/edit';

  static const String profilePhoto = 'profilePhoto';
  static const String profilePhotoPath = '/profile/photo';

  static const String pointsOverview = 'pointsOverview';
  static const String pointsOverviewPath = '/points';

  static const String pointsHistory = 'pointsHistory';
  static const String pointsHistoryPath = '/points/history';

  static const String achievements = 'achievements';
  static const String achievementsPath = '/achievements';

  static const String achievementDetails = 'achievementDetails';
  static const String achievementDetailsPath = '/achievements/:id';

  static const String privacy = 'privacy';
  static const String privacyPath = '/privacy';

  static const String notifications = 'notifications';
  static const String notificationsPath = '/notifications';

  static const String notificationDetails = 'notificationDetails';
  static const String notificationDetailsPath = '/notifications/:id';

  static const String notificationSettings = 'notificationSettings';
  static const String notificationSettingsPath = '/settings/notifications';

  static const String appSettings = 'appSettings';
  static const String appSettingsPath = '/settings';

  static const String helpSupport = 'helpSupport';
  static const String helpSupportPath = '/help';

  static const String aboutMaatram = 'aboutMaatram';
  static const String aboutMaatramPath = '/about';

  // Auth & Welcome Routes
  static const String welcomeSplash = 'welcomeSplash';
  static const String welcomeSplashPath = '/welcome';

  static const String login = 'login';
  static const String loginPath = '/login';

  static const String register = 'register';
  static const String registerPath = '/register';

  static const String verifyEmail = 'verifyEmail';
  static const String verifyEmailPath = '/verify-email';

  static const String forgotPassword = 'forgotPassword';
  static const String forgotPasswordPath = '/forgot-password';

  static const String resetPassword = 'resetPassword';
  static const String resetPasswordPath = '/reset-password';

  // Onboarding & Application Status
  static const String pendingVerification = 'pendingVerification';
  static const String pendingVerificationPath =
      '/onboarding/pending-verification';

  static const String pendingApproval = 'pendingApproval';
  static const String pendingApprovalPath = '/onboarding/pending-approval';

  static const String welcome = 'welcome';
  static const String welcomePath = '/onboarding/welcome';

  static const String rejected = 'rejected';
  static const String rejectedPath = '/onboarding/rejected';

  // Developer Design Showcase
  static const String devShowcase = 'devShowcase';
  static const String devShowcasePath = '/dev/showcase';
}
