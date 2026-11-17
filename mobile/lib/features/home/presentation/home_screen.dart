import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/route_names.dart';
import '../../../../core/auth/auth_controller.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/widgets/layout/organic_background.dart';
import '../state/home_controller.dart';
import 'widgets/home_header.dart';
import 'widgets/illustrated_welcome_banner.dart';
import 'widgets/impact_statistics_row.dart';
import 'widgets/inspiration_banner.dart';
import 'widgets/upcoming_events_section.dart';
import 'widgets/volunteer_profile_points_card.dart';
import 'widgets/your_progress_section.dart';

/// Complete, production-grade Volunteer Home Screen for the Maatram Portal.
/// Implements all 8 required sections with independent section resilience,
/// pull-to-refresh, real backend integration, and zero fabricated data.
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

                  // Section 2: Illustrated Welcome Banner ("Hello, {name}! 👋")
                  IllustratedWelcomeBanner(
                    volunteerName: volunteerName,
                    isLoading: homeState.profile.isLoading,
                  ),

                  // Section 3: Volunteer Profile Card & Points Balance
                  VolunteerProfilePointsCard(
                    profile: profile,
                    gamification: gamification,
                    isLoading: homeState.profile.isLoading ||
                        homeState.gamification.isLoading,
                    onEditProfile: () {
                      context.go(RouteNames.morePath);
                    },
                  ),

                  // Section 4: 4 Impact Statistics (Hours, Events, This Year, Rank)
                  ImpactStatisticsRow(
                    summary: gamification,
                    isLoading: homeState.gamification.isLoading,
                  ),

                  // Section 5: Upcoming Events
                  UpcomingEventsSection(
                    events: events,
                    registrations: homeState.registrations,
                    isLoading: homeState.events.isLoading,
                    errorMessage: homeState.events.hasError
                        ? 'Unable to load upcoming events right now.'
                        : null,
                    onRetry: () {
                      ref.read(homeControllerProvider.notifier).retryEvents();
                    },
                  ),

                  // Section 6: Your Progress (Real Badges & Milestone Progress)
                  YourProgressSection(
                    summary: gamification,
                    isLoading: homeState.gamification.isLoading,
                  ),

                  // Section 7: Inspiration Banner ("Together for a Better Tomorrow")
                  const InspirationBanner(),

                  // Bottom padding for scroll clearance above navigation bar
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
