import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/route_names.dart';
import '../../../../core/auth/auth_controller.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/widgets/layout/organic_background.dart';
import '../state/home_controller.dart';
import 'widgets/home_header.dart';
import 'widgets/motivational_banner.dart';
import 'widgets/upcoming_events_section.dart';
import 'widgets/volunteer_progress_card.dart';
import 'widgets/volunteer_statistics.dart';
import 'widgets/volunteer_summary_card.dart';
import 'widgets/welcome_banner.dart';

/// Complete, production-grade Volunteer Home Screen for the Maatram Portal.
/// Reconstructed to achieve high visual fidelity to the approved reference design.
/// Composes all 7 content sections with real backend API integration,
/// responsive layout, zero hardcoded volunteer data, and clean component isolation.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);
    final homeState = ref.watch(homeControllerProvider);

    final profile = homeState.profile.valueOrNull;
    final gamification = homeState.gamification.valueOrNull;
    final events = homeState.events.valueOrNull ?? [];

    // Determine volunteer display name with graceful fallback hierarchy
    final volunteerName = profile?.shortName ??
        (authState.session?.firstName != null &&
                authState.session!.firstName!.isNotEmpty
            ? authState.session!.firstName!
            : 'Volunteer');

    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          bottom: false,
          child: RefreshIndicator(
            color: MaatramColors.primaryGold,
            backgroundColor: Colors.white,
            onRefresh: () async {
              await ref.read(homeControllerProvider.notifier).refresh();
            },
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(
                parent: BouncingScrollPhysics(),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Section 1: Header (Logo, Notifications with Unread Badge, Avatar)
                  HomeHeader(
                    unreadCount: homeState.unreadNotifications,
                    volunteerName: volunteerName,
                    avatarUrl: profile?.avatarUrl,
                  ),

                  // Section 2: Welcome Banner ("Hello, {name}! 👋")
                  WelcomeBanner(
                    volunteerName: volunteerName,
                    isLoading: homeState.profile.isLoading,
                  ),

                  // Section 3: Volunteer Profile Summary Card & Points Balance
                  VolunteerSummaryCard(
                    profile: profile,
                    gamification: gamification,
                    isLoading: homeState.profile.isLoading ||
                        homeState.gamification.isLoading,
                    onEditProfile: () {
                      context.push(RouteNames.profilePath);
                    },
                  ),

                  // Section 4: 4 Impact Statistics (Hours, Events, This Year, Rank)
                  VolunteerStatistics(
                    summary: gamification,
                    isLoading: homeState.gamification.isLoading,
                  ),

                  // Section 5: Upcoming Events
                  UpcomingEventsSection(
                    events: events,
                    registrations: homeState.registrations,
                    isLoading: homeState.events.isLoading,
                    errorMessage: homeState.events.hasError
                        ? 'Could not load upcoming events.'
                        : null,
                    onRetry: () {
                      ref.read(homeControllerProvider.notifier).retryEvents();
                    },
                  ),

                  // Section 6: Your Progress (Real Badges & Milestone Progress)
                  VolunteerProgressCard(
                    summary: gamification,
                    isLoading: homeState.gamification.isLoading,
                  ),

                  // Section 7: Motivational Banner ("Together for a Better Tomorrow")
                  const MotivationalBanner(),

                  // Bottom padding for scroll clearance above bottom navigation bar
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
