import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/route_names.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/models/event_model.dart';
import '../../../../core/models/event_registration_model.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/shadows.dart';
import '../../../../core/theme/spacing.dart';

/// Section 5: Upcoming Events section showcasing volunteering drives.
/// Features section header with "View All ->" link, horizontal event card preview,
/// registration status badges, and resilient empty / error states.
class UpcomingEventsSection extends StatelessWidget {
  final List<EventModel> events;
  final Map<String, EventRegistrationModel> registrations;
  final bool isLoading;
  final String? errorMessage;
  final VoidCallback? onRetry;

  const UpcomingEventsSection({
    super.key,
    required this.events,
    this.registrations = const {},
    this.isLoading = false,
    this.errorMessage,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        // 1. Section Header Row
        Padding(
          padding: const EdgeInsets.fromLTRB(
            MaatramSpacing.md,
            MaatramSpacing.md,
            MaatramSpacing.md,
            MaatramSpacing.xs,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Expanded(
                child: Text(
                  'Upcoming Events',
                  style: TextStyle(
                    fontFamily: 'Georgia',
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: MaatramColors.deepNavy,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              GestureDetector(
                onTap: () {
                  context.go(RouteNames.eventsPath);
                },
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'View All',
                      style: TextStyle(
                        fontFamily: 'Roboto',
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFFD97706),
                      ),
                    ),
                    SizedBox(width: 4),
                    Icon(
                      Icons.arrow_forward_rounded,
                      size: 15,
                      color: Color(0xFFD97706),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        // 2. Events Body (Loading, Error, Empty, or Content)
        if (isLoading)
          _buildLoadingState()
        else if (errorMessage != null)
          _buildErrorState()
        else if (events.isEmpty)
          _buildEmptyState(context)
        else
          _buildEventsList(context),
      ],
    );
  }

  Widget _buildEventsList(BuildContext context) {
    // If only 1 event, display as full width card; if multiple, horizontal scroll
    return SizedBox(
      height: 275,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.md,
          vertical: MaatramSpacing.xs,
        ),
        scrollDirection: Axis.horizontal,
        itemCount: events.length,
        separatorBuilder: (_, __) => const SizedBox(width: MaatramSpacing.md),
        itemBuilder: (context, index) {
          final event = events[index];
          final reg = registrations[event.id];
          return _EventCard(
            event: event,
            registration: reg,
            onTap: () {
              context.push('/events/${event.id}');
            },
          );
        },
      ),
    );
  }

  Widget _buildLoadingState() {
    return Container(
      height: 250,
      margin: const EdgeInsets.symmetric(
        horizontal: MaatramSpacing.md,
        vertical: MaatramSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: MaatramColors.white,
        borderRadius: MaatramRadii.cardRadius,
        border: Border.all(color: MaatramColors.warmBorder),
      ),
      child: const Center(
        child: CircularProgressIndicator(
          color: MaatramColors.primaryGold,
          strokeWidth: 2.5,
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: MaatramSpacing.md,
        vertical: MaatramSpacing.xs,
      ),
      padding: const EdgeInsets.all(MaatramSpacing.md),
      decoration: BoxDecoration(
        color: MaatramColors.white,
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
              'Could not load upcoming events.',
              style: TextStyle(
                fontFamily: 'Roboto',
                fontSize: 13,
                color: MaatramColors.secondaryText,
              ),
            ),
          ),
          if (onRetry != null)
            TextButton(
              onPressed: onRetry,
              child: const Text(
                'Retry',
                style: TextStyle(
                  color: Color(0xFFD97706),
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: MaatramSpacing.md,
        vertical: MaatramSpacing.xs,
      ),
      padding: const EdgeInsets.all(MaatramSpacing.lg),
      decoration: BoxDecoration(
        color: MaatramColors.white,
        borderRadius: MaatramRadii.cardRadius,
        border: Border.all(color: MaatramColors.warmBorder),
        boxShadow: MaatramShadows.card,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: const BoxDecoration(
              color: Color(0xFFFFF9E6),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.event_available_rounded,
              color: Color(0xFFD97706),
              size: 28,
            ),
          ),
          const SizedBox(height: 10),
          const Text(
            'No upcoming events scheduled right now',
            style: TextStyle(
              fontFamily: 'Georgia',
              fontSize: 15,
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 4),
          const Text(
            'New volunteering drives will appear here soon.',
            style: TextStyle(
              fontFamily: 'Roboto',
              fontSize: 12,
              color: MaatramColors.secondaryText,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          OutlinedButton(
            onPressed: () => context.go(RouteNames.eventsPath),
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: MaatramColors.primaryGold),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
            ),
            child: const Text(
              'Explore All Events',
              style: TextStyle(
                color: Color(0xFFD97706),
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _EventCard extends StatelessWidget {
  final EventModel event;
  final EventRegistrationModel? registration;
  final VoidCallback onTap;

  const _EventCard({
    required this.event,
    this.registration,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MaatramFadeSlideIn(
      direction: SlideDirection.fromRight,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          width: 290,
          decoration: BoxDecoration(
            color: MaatramColors.white,
            borderRadius: MaatramRadii.cardRadius,
            border: Border.all(color: MaatramColors.warmBorder),
            boxShadow: MaatramShadows.card,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 1. Cover Image & Category Pill
              Stack(
                children: [
                  ClipRRect(
                    borderRadius:
                        const BorderRadius.vertical(top: Radius.circular(16)),
                    child: SizedBox(
                      height: 120,
                      width: double.infinity,
                      child: event.coverImageUrl != null &&
                              event.coverImageUrl!.isNotEmpty
                          ? CachedNetworkImage(
                              imageUrl: event.coverImageUrl!,
                              fit: BoxFit.cover,
                              errorWidget: (_, __, ___) => Image.asset(
                                event.assetFallback,
                                fit: BoxFit.cover,
                              ),
                            )
                          : Image.asset(
                              event.assetFallback,
                              fit: BoxFit.cover,
                            ),
                    ),
                  ),

                  // Category Pill Overlay
                  Positioned(
                    top: 10,
                    right: 10,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 9, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFFBEB),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                            color: const Color(0xFFFDE68A), width: 0.8),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x15000000),
                            blurRadius: 4,
                            offset: Offset(0, 1),
                          ),
                        ],
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(
                            Icons.school_rounded,
                            size: 12,
                            color: Color(0xFFB45309),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            event.categoryDisplay,
                            style: const TextStyle(
                              fontFamily: 'Roboto',
                              fontSize: 10.5,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFFB45309),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Registration status badge (if registered)
                  if (registration != null)
                    Positioned(
                      top: 10,
                      left: 10,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 3.5),
                        decoration: BoxDecoration(
                          color: MaatramColors.successLight,
                          borderRadius: BorderRadius.circular(10),
                          border:
                              Border.all(color: MaatramColors.successBorder),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(
                              Icons.check_circle_rounded,
                              size: 10,
                              color: MaatramColors.successDark,
                            ),
                            const SizedBox(width: 3),
                            Text(
                              registration!.statusDisplay,
                              style: const TextStyle(
                                fontFamily: 'Roboto',
                                fontSize: 9.5,
                                fontWeight: FontWeight.bold,
                                color: MaatramColors.successDark,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                ],
              ),

              // 2. Details Body
              Padding(
                padding: const EdgeInsets.all(MaatramSpacing.sm + 2),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title
                    Text(
                      event.title,
                      style: const TextStyle(
                        fontFamily: 'Roboto',
                        fontSize: 14.5,
                        fontWeight: FontWeight.bold,
                        color: MaatramColors.deepNavy,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 5),

                    // Location
                    Row(
                      children: [
                        const Icon(
                          Icons.location_on_outlined,
                          size: 13,
                          color: MaatramColors.secondaryText,
                        ),
                        const SizedBox(width: 4),
                        Expanded(
                          child: Text(
                            event.locationDisplay,
                            style: const TextStyle(
                              fontFamily: 'Roboto',
                              fontSize: 11.5,
                              color: MaatramColors.secondaryText,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),

                    // Date & Time + Arrow Button
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Expanded(
                          child: Row(
                            children: [
                              const Icon(
                                Icons.calendar_today_outlined,
                                size: 12,
                                color: Color(0xFFD97706),
                              ),
                              const SizedBox(width: 4),
                              Expanded(
                                child: Text(
                                  '${event.formattedDate} • ${event.formattedTime}',
                                  style: const TextStyle(
                                    fontFamily: 'Roboto',
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: MaatramColors.deepNavy,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 8),

                        // Gold circular arrow icon
                        Container(
                          padding: const EdgeInsets.all(6),
                          decoration: const BoxDecoration(
                            color: Color(0xFFFFF3D6),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.arrow_forward_rounded,
                            size: 14,
                            color: Color(0xFFB45309),
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
  }
}
