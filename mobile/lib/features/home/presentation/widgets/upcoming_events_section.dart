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
            14,
            MaatramSpacing.md,
            8,
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
                    fontSize: 19,
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
                      size: 14,
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

  Widget _buildLoadingState() {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: MaatramSpacing.md,
        vertical: 6,
      ),
      child: Container(
        height: 130,
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
      ),
    );
  }

  Widget _buildErrorState() {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: MaatramSpacing.md,
        vertical: 6,
      ),
      padding: const EdgeInsets.all(MaatramSpacing.md),
      decoration: BoxDecoration(
        color: MaatramColors.white,
        borderRadius: MaatramRadii.cardRadius,
        border: Border.all(color: MaatramColors.warmBorder),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.info_outline_rounded,
            color: MaatramColors.secondaryText,
            size: 20,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              errorMessage ?? 'Unable to load upcoming events.',
              style: const TextStyle(
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
                  fontFamily: 'Roboto',
                  fontWeight: FontWeight.bold,
                  color: Color(0xFFD97706),
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
        vertical: 6,
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
              fontFamily: 'Roboto',
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
                fontFamily: 'Roboto',
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

  Widget _buildEventsList(BuildContext context) {
    // Show top upcoming event in the hero position matching reference
    final primaryEvent = events.first;
    final registration = registrations[primaryEvent.id];

    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: MaatramSpacing.md,
        vertical: 4,
      ),
      child: UpcomingEventCard(
        event: primaryEvent,
        registration: registration,
        onTap: () {
          context.push('${RouteNames.eventDetailsPath}/${primaryEvent.id}');
        },
      ),
    );
  }
}

/// Horizontal event card matching the approved reference design.
/// Left: image with 24dp rounded corner clipping. Right: category badge, title, location, date & time, arrow.
class UpcomingEventCard extends StatelessWidget {
  final EventModel event;
  final EventRegistrationModel? registration;
  final VoidCallback onTap;

  const UpcomingEventCard({
    super.key,
    required this.event,
    this.registration,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MaatramFadeSlideIn(
      direction: SlideDirection.fromBottom,
      child: GestureDetector(
        onTap: onTap,
        child: LayoutBuilder(
          builder: (context, constraints) {
            final isCompact = constraints.maxWidth < 340;
            final imageWidth = isCompact ? 100.0 : 120.0;

            return Container(
              height: 130,
              decoration: BoxDecoration(
                color: MaatramColors.white,
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
                boxShadow: MaatramShadows.card,
              ),
              child: Stack(
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // ── Left: Event Image (with 24dp left clipping) ──────
                      ClipRRect(
                        borderRadius: const BorderRadius.only(
                          topLeft: Radius.circular(24),
                          bottomLeft: Radius.circular(24),
                        ),
                        child: SizedBox(
                          width: imageWidth,
                          height: 130,
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

                      // ── Right: Event Details in Roboto ───────────────────
                      Expanded(
                        child: Padding(
                          padding: EdgeInsets.fromLTRB(
                            10,
                            8,
                            isCompact ? 34 : 40,
                            8,
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              // Category badge pill
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 2.5,
                                ),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFFFFBEB),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(
                                    color: const Color(0xFFFDE68A),
                                    width: 0.8,
                                  ),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(
                                      Icons.school_rounded,
                                      size: 11,
                                      color: Color(0xFFB45309),
                                    ),
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

                              // Event title
                              Text(
                                event.title,
                                style: const TextStyle(
                                  fontFamily: 'Roboto',
                                  fontSize: 13.5,
                                  fontWeight: FontWeight.bold,
                                  color: MaatramColors.deepNavy,
                                  height: 1.25,
                                ),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),

                              // Location
                              Row(
                                children: [
                                  const Icon(
                                    Icons.location_on_outlined,
                                    size: 12,
                                    color: MaatramColors.secondaryText,
                                  ),
                                  const SizedBox(width: 3),
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

                              // Date & time row (using Wrap to prevent overflow on 320dp)
                              Wrap(
                                crossAxisAlignment: WrapCrossAlignment.center,
                                spacing: 6,
                                runSpacing: 2,
                                children: [
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(
                                        Icons.calendar_today_outlined,
                                        size: 10.5,
                                        color: Color(0xFFD97706),
                                      ),
                                      const SizedBox(width: 3),
                                      ConstrainedBox(
                                        constraints: const BoxConstraints(maxWidth: 130),
                                        child: Text(
                                          event.formattedDate,
                                          style: const TextStyle(
                                            fontFamily: 'Roboto',
                                            fontSize: 10,
                                            fontWeight: FontWeight.w600,
                                            color: MaatramColors.deepNavy,
                                          ),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ],
                                  ),
                                  Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Icon(
                                        Icons.access_time_rounded,
                                        size: 10.5,
                                        color: MaatramColors.secondaryText,
                                      ),
                                      const SizedBox(width: 2),
                                      ConstrainedBox(
                                        constraints: const BoxConstraints(maxWidth: 110),
                                        child: Text(
                                          event.formattedTime,
                                          style: const TextStyle(
                                            fontFamily: 'Roboto',
                                            fontSize: 10,
                                            color: MaatramColors.secondaryText,
                                          ),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),

                  // ── Registration badge (if registered) ────────────────
                  if (registration != null)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 7,
                          vertical: 3,
                        ),
                        decoration: BoxDecoration(
                          color: MaatramColors.successLight,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: MaatramColors.successBorder),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(
                              Icons.check_circle_rounded,
                              size: 9,
                              color: MaatramColors.successDark,
                            ),
                            const SizedBox(width: 3),
                            Text(
                              registration!.statusDisplay,
                              style: const TextStyle(
                                fontFamily: 'Roboto',
                                fontSize: 9,
                                fontWeight: FontWeight.bold,
                                color: MaatramColors.successDark,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                  // ── Action: Circular Arrow Button on Right Edge ───────
                  Positioned(
                    right: 8,
                    top: 0,
                    bottom: 0,
                    child: Center(
                      child: Container(
                        width: 30,
                        height: 30,
                        decoration: const BoxDecoration(
                          color: Color(0xFFFFF3D6),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.arrow_forward_rounded,
                          size: 15,
                          color: Color(0xFFB45309),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}
