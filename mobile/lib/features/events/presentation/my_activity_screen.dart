import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/animations/fade_slide_in.dart';
import '../../../core/models/attendance_model.dart';
import '../../../core/models/event_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/shadows.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/layout/avatar.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../../../core/widgets/navigation/bottom_nav_bar.dart';
import '../../home/state/home_controller.dart';
import '../state/activity_controller.dart';

/// Complete, production-grade My Activity Screen faithful to mentor reference `ref_03_my_activity.jpg`.
/// Features segmented tab switching (Upcoming, Completed, Cancelled), dynamic horizontal event cards,
/// past activity cards with status pills, cupped-heart illustration header, motivational banner,
/// and persistent bottom navigation bar.
class MyActivityScreen extends ConsumerWidget {
  const MyActivityScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activityState = ref.watch(activityControllerProvider);
    final homeState = ref.watch(homeControllerProvider);
    final profile = homeState.profile.valueOrNull;

    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        bottomNavigationBar: MaatramBottomNavBar(
          currentIndex:
              3, // More / Activity is within the More destination cluster
          onDestinationSelected: (index) {
            final destinations = [
              RouteNames.homePath,
              RouteNames.eventsPath,
              RouteNames.leaderboardPath,
              RouteNames.morePath,
            ];
            if (index >= 0 && index < destinations.length) {
              context.go(destinations[index]);
            }
          },
        ),
        body: SafeArea(
          bottom: false,
          child: RefreshIndicator(
            color: MaatramColors.primaryGold,
            backgroundColor: Colors.white,
            onRefresh: () async {
              await ref.read(activityControllerProvider.notifier).refresh();
            },
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(
                parent: BouncingScrollPhysics(),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // 1. Top Bar: Logo, Notification Bell, User Avatar
                  _buildTopBar(context, homeState.unreadNotifications,
                      profile?.avatarUrl, profile?.shortName),

                  // 2. Header: Title, Subtitle, and Cupped-Heart Illustration
                  _buildHeaderSection(),

                  const SizedBox(height: MaatramSpacing.md),

                  // 3. Segmented Pill Tabs: Upcoming | Completed | Cancelled
                  _buildSegmentedTabs(context, ref, activityState.selectedTab),

                  const SizedBox(height: MaatramSpacing.md),

                  // 4. Content Based on Tab Selection
                  if (activityState.isLoading)
                    _buildLoadingState()
                  else if (activityState.errorMessage != null)
                    _buildErrorState(ref)
                  else
                    _buildTabContent(context, ref, activityState),

                  // 5. Motivational Banner: "Keep volunteering! Your efforts create a lasting impact."
                  const Padding(
                    padding: EdgeInsets.symmetric(
                        horizontal: MaatramSpacing.md,
                        vertical: MaatramSpacing.md),
                    child: _MotivationalActivityBanner(),
                  ),

                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTopBar(
      BuildContext context, int unreadCount, String? avatarUrl, String? name) {
    return Padding(
      padding: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.md, vertical: MaatramSpacing.xs),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Maatram Official Logo (proportional to mentor reference)
          Image.asset(
            'assets/images/logo.png',
            height: 44,
            fit: BoxFit.contain,
            errorBuilder: (_, __, ___) => const Text(
              'MAATRAM',
              style: TextStyle(
                  fontFamily: 'Georgia',
                  fontWeight: FontWeight.bold,
                  fontSize: 20),
            ),
          ),
          // Actions: Bell with badge + Profile Avatar
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Stack(
                clipBehavior: Clip.none,
                children: [
                  IconButton(
                    icon: const Icon(Icons.notifications_outlined,
                        size: 24, color: MaatramColors.deepNavy),
                    onPressed: () => context.push(RouteNames.notificationsPath),
                  ),
                  if (unreadCount > 0)
                    Positioned(
                      top: 6,
                      right: 6,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: const BoxDecoration(
                          color: Color(0xFFEF4444),
                          shape: BoxShape.circle,
                        ),
                        constraints:
                            const BoxConstraints(minWidth: 16, minHeight: 16),
                        child: Text(
                          unreadCount > 9 ? '9+' : '$unreadCount',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 9,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(width: 4),
              GestureDetector(
                onTap: () => context.push(RouteNames.profilePath),
                child: MaatramAvatar(
                  imageUrl: avatarUrl,
                  name: name ?? 'Volunteer',
                  size: 38,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHeaderSection() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(
          MaatramSpacing.md, MaatramSpacing.xs, MaatramSpacing.md, 0),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // Subtle botanical wheat-stalks decor in background
          Positioned(
            right: 12,
            top: -15,
            child: Opacity(
              opacity: 0.12,
              child: SvgPicture.asset(
                'assets/decorations/wheat-stalks.svg',
                height: 110,
                colorFilter: const ColorFilter.mode(
                  MaatramColors.primaryGold,
                  BlendMode.srcIn,
                ),
              ),
            ),
          ),
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Header Text: My Activity + Subtitle
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'My Activity',
                      style: MaatramTypography.headlineLarge.copyWith(
                        fontFamily: 'Georgia',
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: MaatramColors.deepNavy,
                        letterSpacing: -0.3,
                      ),
                    ),
                    const SizedBox(height: 5),
                    const Text(
                      'Track your volunteering journey\nand stay updated!',
                      style: TextStyle(
                        fontFamily: 'Roboto',
                        fontSize: 13,
                        color: MaatramColors.secondaryText,
                        height: 1.35,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              // Golden heart in cupped hands illustration
              SvgPicture.asset(
                'assets/illustrations/together-heart.svg',
                height: 82,
                fit: BoxFit.contain,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSegmentedTabs(
      BuildContext context, WidgetRef ref, String currentTab) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: MaatramSpacing.md),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(30),
          border: Border.all(color: const Color(0xFFEFECE6), width: 1.0),
          boxShadow: const [
            BoxShadow(
              color: Color(0x08000000),
              blurRadius: 6,
              offset: Offset(0, 2),
            ),
          ],
        ),
        padding: const EdgeInsets.all(3.5),
        child: Row(
          children: [
            _TabPill(
              label: 'Upcoming',
              icon: Icons.calendar_today_rounded,
              isSelected: currentTab == 'UPCOMING',
              onTap: () => ref
                  .read(activityControllerProvider.notifier)
                  .selectTab('UPCOMING'),
            ),
            _TabPill(
              label: 'Completed',
              icon: Icons.check_circle_outline_rounded,
              isSelected: currentTab == 'COMPLETED',
              onTap: () => ref
                  .read(activityControllerProvider.notifier)
                  .selectTab('COMPLETED'),
            ),
            _TabPill(
              label: 'Cancelled',
              icon: Icons.cancel_outlined,
              isSelected: currentTab == 'CANCELLED',
              onTap: () => ref
                  .read(activityControllerProvider.notifier)
                  .selectTab('CANCELLED'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTabContent(
      BuildContext context, WidgetRef ref, ActivityState state) {
    switch (state.selectedTab) {
      case 'COMPLETED':
        return _buildCompletedTab(context, state.completedActivities);
      case 'CANCELLED':
        return _buildCancelledTab(context, state.cancelledRegistrations);
      case 'UPCOMING':
      default:
        return _buildUpcomingTab(
            context, ref, state.upcomingEvents, state.completedActivities);
    }
  }

  Widget _buildUpcomingTab(
    BuildContext context,
    WidgetRef ref,
    List<EventModel> upcomingEvents,
    List<AttendanceModel> pastActivities,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 1. Upcoming Events Section Header
        _buildSectionHeader(
          title: 'Upcoming Events',
          actionText: 'View All →',
          onAction: () => context.go(RouteNames.eventsPath),
        ),

        // Upcoming Cards
        if (upcomingEvents.isEmpty)
          _buildEmptyActivitiesCard(
            title: 'No upcoming registrations',
            description: 'Explore upcoming drives and register to make a difference.',
          )
        else
          ...upcomingEvents.map((event) => Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: MaatramSpacing.md, vertical: 5),
                child: _UpcomingActivityCard(event: event),
              )),

        const SizedBox(height: MaatramSpacing.md),

        // 2. Past Activities Section Header
        _buildSectionHeader(
          title: 'Past Activities',
          actionText: 'View All →',
          onAction: () => ref
              .read(activityControllerProvider.notifier)
              .selectTab('COMPLETED'),
        ),

        // Past Activity Cards
        if (pastActivities.isEmpty)
          _buildEmptyActivitiesCard(
            title: 'No past activities yet',
            description:
                'Your completed volunteering sessions will appear here after attendance verification.',
            icon: Icons.history_rounded,
          )
        else
          ...pastActivities.map((a) => Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: MaatramSpacing.md, vertical: 5),
                child: _PastActivityCard(
                  title: a.eventTitle ?? 'Volunteering Session',
                  categoryDisplay: 'Volunteering',
                  categoryIcon: Icons.volunteer_activism_rounded,
                  assetImage: 'assets/images/community-engagement.jpg',
                  dateText: a.formattedDate,
                  timeText: a.formattedTimeRange,
                ),
              )),
      ],
    );
  }

  Widget _buildCompletedTab(
      BuildContext context, List<AttendanceModel> activities) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader(title: 'Completed Activities'),
        if (activities.isEmpty)
          _buildEmptyActivitiesCard(
            title: 'No completed activities yet',
            description:
                'Completed events and verified service hours will be recorded here.',
            icon: Icons.check_circle_outline_rounded,
          )
        else
          ...activities.map((a) => Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: MaatramSpacing.md, vertical: 5),
                child: _PastActivityCard(
                  title: a.eventTitle ?? 'Volunteering Session',
                  categoryDisplay: 'Volunteering',
                  categoryIcon: Icons.volunteer_activism_rounded,
                  assetImage: 'assets/images/community-engagement.jpg',
                  dateText: a.formattedDate,
                  timeText: a.formattedTimeRange,
                ),
              )),
      ],
    );
  }

  Widget _buildEmptyActivitiesCard({
    required String title,
    required String description,
    IconData icon = Icons.event_available_outlined,
  }) {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: MaatramSpacing.md,
        vertical: MaatramSpacing.xs,
      ),
      padding: const EdgeInsets.all(MaatramSpacing.lg),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: MaatramRadii.cardRadius,
        border: Border.all(color: MaatramColors.warmBorder),
      ),
      child: Center(
        child: Column(
          children: [
            Icon(icon, size: 36, color: MaatramColors.charcoal400),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(
                fontFamily: 'Georgia',
                fontSize: 15,
                fontWeight: FontWeight.bold,
                color: MaatramColors.deepNavy,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              description,
              style: const TextStyle(
                fontFamily: 'Roboto',
                fontSize: 12,
                color: MaatramColors.secondaryText,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCancelledTab(BuildContext context, List<dynamic> cancelled) {
    return Container(
      margin: const EdgeInsets.all(MaatramSpacing.md),
      padding: const EdgeInsets.all(MaatramSpacing.xl),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: MaatramRadii.cardRadius,
        border: Border.all(color: MaatramColors.warmBorder),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: const BoxDecoration(
              color: Color(0xFFF3F4F6),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.event_busy_rounded,
                color: MaatramColors.charcoal500, size: 28),
          ),
          const SizedBox(height: 12),
          const Text(
            'No Cancelled Activities',
            style: TextStyle(
                fontFamily: 'Georgia',
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: MaatramColors.deepNavy),
          ),
          const SizedBox(height: 4),
          const Text(
            'You do not have any cancelled or withdrawn registrations.',
            style: TextStyle(
                fontFamily: 'Roboto',
                fontSize: 12,
                color: MaatramColors.secondaryText),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(
      {required String title, String? actionText, VoidCallback? onAction}) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(MaatramSpacing.md, MaatramSpacing.sm,
          MaatramSpacing.md, MaatramSpacing.xs),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 3.5,
                  height: 16,
                  decoration: BoxDecoration(
                    color: MaatramColors.primaryGold,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(width: 8),
                Flexible(
                  child: Text(
                    title,
                    style: const TextStyle(
                      fontFamily: 'Georgia',
                      fontSize: 17,
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
          if (actionText != null)
            GestureDetector(
              onTap: onAction,
              child: Text(
                actionText,
                style: const TextStyle(
                  fontFamily: 'Roboto',
                  fontSize: 12.5,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFFD97706),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return const Padding(
      padding: EdgeInsets.all(40),
      child: Center(
        child: CircularProgressIndicator(
            color: MaatramColors.primaryGold, strokeWidth: 2.5),
      ),
    );
  }

  Widget _buildErrorState(WidgetRef ref) {
    return Container(
      margin: const EdgeInsets.all(MaatramSpacing.md),
      padding: const EdgeInsets.all(MaatramSpacing.md),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: MaatramRadii.cardRadius,
        border: Border.all(color: MaatramColors.warmBorder),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded,
              color: MaatramColors.error, size: 24),
          const SizedBox(width: 12),
          const Expanded(
            child: Text(
              'Could not load activity records.',
              style: TextStyle(
                  fontFamily: 'Roboto',
                  fontSize: 13,
                  color: MaatramColors.secondaryText),
            ),
          ),
          TextButton(
            onPressed: () =>
                ref.read(activityControllerProvider.notifier).loadData(),
            child: const Text('Retry',
                style: TextStyle(
                    color: Color(0xFFD97706), fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

/// Segmented Pill Tab Widget
class _TabPill extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;

  const _TabPill({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeInOut,
          padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
          decoration: BoxDecoration(
            color: isSelected ? MaatramColors.primaryGold : Colors.transparent,
            borderRadius: BorderRadius.circular(26),
            boxShadow: isSelected
                ? const [
                    BoxShadow(
                      color: Color(0x20F5B817),
                      blurRadius: 4,
                      offset: Offset(0, 1),
                    )
                  ]
                : null,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 14.5,
                color: isSelected
                    ? MaatramColors.deepNavy
                    : const Color(0xFF6B7280),
              ),
              const SizedBox(width: 5),
              Flexible(
                child: Text(
                  label,
                  style: TextStyle(
                    fontFamily: 'Roboto',
                    fontSize: 12,
                    fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                    color: isSelected
                        ? MaatramColors.deepNavy
                        : const Color(0xFF374151),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Card representation for Upcoming Activities faithful to `ref_03_my_activity.jpg`
class _UpcomingActivityCard extends StatelessWidget {
  final EventModel event;

  const _UpcomingActivityCard({required this.event});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 350;
        final thumbSize = isCompact ? 72.0 : 92.0;

        return MaatramFadeSlideIn(
          direction: SlideDirection.fromBottom,
          child: GestureDetector(
            onTap: () {
              context.push(
                RouteNames.activityDetailsPath
                    .replaceAll(':id', 'activity-record'),
              );
            },
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
                boxShadow: MaatramShadows.card,
              ),
              padding: EdgeInsets.all(isCompact ? 8.0 : MaatramSpacing.md),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Left: Event Thumbnail Image with rounded corners
                  ClipRRect(
                    borderRadius: BorderRadius.circular(10),
                    child: SizedBox(
                      width: thumbSize,
                      height: thumbSize,
                      child: Image.asset(
                        event.assetFallback,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => Image.asset(
                          'assets/images/school-visit.jpg',
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: isCompact ? 8.0 : 12.0),

                  // Right: Event Details
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Row: Category Badge on left, Chevron button on right
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Flexible(
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 7, vertical: 2.5),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFFFFBEB),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(
                                      color: const Color(0xFFFDE68A),
                                      width: 0.8),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(Icons.school_rounded,
                                        size: 11, color: Color(0xFFB45309)),
                                    const SizedBox(width: 3),
                                    Flexible(
                                      child: Text(
                                        event.categoryDisplay,
                                        style: const TextStyle(
                                          fontFamily: 'Roboto',
                                          fontSize: 10,
                                          fontWeight: FontWeight.w700,
                                          color: Color(0xFFB45309),
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            const SizedBox(width: 4),
                            Container(
                              width: 22,
                              height: 22,
                              decoration: const BoxDecoration(
                                color: Color(0xFFFFFBEB),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.chevron_right_rounded,
                                  size: 15, color: Color(0xFFB45309)),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),

                        // Title
                        Text(
                          event.title,
                          style: TextStyle(
                            fontFamily: 'Georgia',
                            fontSize: isCompact ? 13.5 : 14.5,
                            fontWeight: FontWeight.bold,
                            color: MaatramColors.deepNavy,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 3),

                        // Location
                        Row(
                          children: [
                            const Icon(Icons.location_on_outlined,
                                size: 11, color: MaatramColors.secondaryText),
                            const SizedBox(width: 2),
                            Expanded(
                              child: Text(
                                event.locationDisplay,
                                style: const TextStyle(
                                  fontFamily: 'Roboto',
                                  fontSize: 10.5,
                                  color: MaatramColors.secondaryText,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),

                        // Bottom: Upcoming Status Badge + Date & Time
                        Wrap(
                          spacing: 6,
                          runSpacing: 3,
                          crossAxisAlignment: WrapCrossAlignment.center,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFFFEF3C7),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.circle,
                                      size: 5, color: Color(0xFFD97706)),
                                  SizedBox(width: 3),
                                  Text(
                                    'Upcoming',
                                    style: TextStyle(
                                      fontFamily: 'Roboto',
                                      fontSize: 9.5,
                                      fontWeight: FontWeight.w700,
                                      color: Color(0xFFB45309),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            ConstrainedBox(
                              constraints: BoxConstraints(
                                  maxWidth: constraints.maxWidth),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.calendar_today_outlined,
                                      size: 10,
                                      color: MaatramColors.secondaryText),
                                  const SizedBox(width: 2),
                                  Flexible(
                                    child: Text(
                                      event.formattedDate,
                                      style: const TextStyle(
                                        fontFamily: 'Roboto',
                                        fontSize: 10,
                                        color: MaatramColors.secondaryText,
                                        fontWeight: FontWeight.w500,
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            ConstrainedBox(
                              constraints: BoxConstraints(
                                  maxWidth: constraints.maxWidth),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.access_time_rounded,
                                      size: 10,
                                      color: MaatramColors.secondaryText),
                                  const SizedBox(width: 2),
                                  Flexible(
                                    child: Text(
                                      event.formattedTime,
                                      style: const TextStyle(
                                        fontFamily: 'Roboto',
                                        fontSize: 10,
                                        color: MaatramColors.secondaryText,
                                        fontWeight: FontWeight.w500,
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

/// Card representation for Past Activities faithful to `ref_03_my_activity.jpg`
class _PastActivityCard extends StatelessWidget {
  final String title;
  final String categoryDisplay;
  final IconData categoryIcon;
  final String assetImage;
  final String dateText;
  final String timeText;

  const _PastActivityCard({
    required this.title,
    required this.categoryDisplay,
    required this.categoryIcon,
    required this.assetImage,
    required this.dateText,
    required this.timeText,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact = constraints.maxWidth < 350;
        final thumbSize = isCompact ? 68.0 : 76.0;

        return MaatramFadeSlideIn(
          direction: SlideDirection.fromBottom,
          child: GestureDetector(
            onTap: () {
              context.push(
                RouteNames.activityDetailsPath
                    .replaceAll(':id', 'activity-record'),
              );
            },
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
                boxShadow: MaatramShadows.card,
              ),
              padding: EdgeInsets.all(isCompact ? 8.0 : MaatramSpacing.sm),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // Thumbnail image
                  ClipRRect(
                    borderRadius: BorderRadius.circular(10),
                    child: SizedBox(
                      width: thumbSize,
                      height: thumbSize,
                      child: Image.asset(
                        assetImage,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) =>
                            Container(color: const Color(0xFFF3F4F6)),
                      ),
                    ),
                  ),
                  SizedBox(width: isCompact ? 8.0 : 12.0),

                  // Card content
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Row: Category Badge + Completed Badge + Chevron
                        Row(
                          children: [
                            Flexible(
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFF3F4F6),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(categoryIcon,
                                        size: 10,
                                        color: MaatramColors.charcoal600),
                                    const SizedBox(width: 3),
                                    Flexible(
                                      child: Text(
                                        categoryDisplay,
                                        style: const TextStyle(
                                          fontFamily: 'Roboto',
                                          fontSize: 9.5,
                                          fontWeight: FontWeight.w600,
                                          color: MaatramColors.charcoal700,
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                            const SizedBox(width: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 5, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFFECFDF5),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: const Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.check_circle_rounded,
                                      size: 9, color: Color(0xFF047857)),
                                  SizedBox(width: 2),
                                  Text(
                                    'Completed',
                                    style: TextStyle(
                                      fontFamily: 'Roboto',
                                      fontSize: 9.5,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF047857),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const Spacer(),
                            Container(
                              width: 20,
                              height: 20,
                              decoration: const BoxDecoration(
                                color: Color(0xFFFFFBEB),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.chevron_right_rounded,
                                  size: 14, color: Color(0xFFB45309)),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),

                        // Title
                        Text(
                          title,
                          style: TextStyle(
                            fontFamily: 'Georgia',
                            fontSize: isCompact ? 13 : 14,
                            fontWeight: FontWeight.bold,
                            color: MaatramColors.deepNavy,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 3),

                        // Date & Time
                        Wrap(
                          spacing: 4,
                          runSpacing: 2,
                          crossAxisAlignment: WrapCrossAlignment.center,
                          children: [
                            ConstrainedBox(
                              constraints: BoxConstraints(
                                  maxWidth: constraints.maxWidth),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.calendar_today_outlined,
                                      size: 10,
                                      color: MaatramColors.secondaryText),
                                  const SizedBox(width: 2),
                                  Flexible(
                                    child: Text(
                                      dateText,
                                      style: const TextStyle(
                                        fontFamily: 'Roboto',
                                        fontSize: 10,
                                        color: MaatramColors.secondaryText,
                                        fontWeight: FontWeight.w500,
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const Text('|',
                                style: TextStyle(
                                    color: MaatramColors.secondaryText,
                                    fontSize: 9)),
                            ConstrainedBox(
                              constraints: BoxConstraints(
                                  maxWidth: constraints.maxWidth),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.access_time_rounded,
                                      size: 10,
                                      color: MaatramColors.secondaryText),
                                  const SizedBox(width: 2),
                                  Flexible(
                                    child: Text(
                                      timeText,
                                      style: const TextStyle(
                                        fontFamily: 'Roboto',
                                        fontSize: 10,
                                        color: MaatramColors.secondaryText,
                                        fontWeight: FontWeight.w500,
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

/// Motivational Banner widget faithful to `ref_03_my_activity.jpg`
class _MotivationalActivityBanner extends StatelessWidget {
  const _MotivationalActivityBanner();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFFFF9E6), Color(0xFFFFF0C2)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFFDE68A), width: 1.0),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0C000000),
            blurRadius: 8,
            offset: Offset(0, 3),
          ),
        ],
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Stack(
        clipBehavior: Clip.none,
        alignment: Alignment.centerRight,
        children: [
          // Botanical decoration on right
          Positioned(
            right: -8,
            child: Opacity(
              opacity: 0.20,
              child: SvgPicture.asset(
                'assets/decorations/wheat-stalks.svg',
                height: 60,
                colorFilter: const ColorFilter.mode(
                  Color(0xFFD97706),
                  BlendMode.srcIn,
                ),
              ),
            ),
          ),
          Row(
            children: [
              // Golden trophy icon with laurel wreath
              Container(
                padding: const EdgeInsets.all(8),
                decoration: const BoxDecoration(
                  color: Color(0xFFFDF0CD),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.emoji_events_rounded,
                    color: Color(0xFFD97706), size: 30),
              ),
              const SizedBox(width: 14),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Keep volunteering!',
                      style: TextStyle(
                        fontFamily: 'Georgia',
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: MaatramColors.deepNavy,
                      ),
                    ),
                    SizedBox(height: 2),
                    Text(
                      'Your efforts create a lasting impact.',
                      style: TextStyle(
                        fontFamily: 'Roboto',
                        fontSize: 11.5,
                        color: Color(0xFF92400E),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
