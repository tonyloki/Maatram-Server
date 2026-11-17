import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/animations/fade_slide_in.dart';
import '../../../core/models/event_model.dart';
import '../../../core/models/event_registration_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/shadows.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../state/events_controller.dart';

/// Complete, production-grade Events Discovery & Registration Screen faithful to Master Screen 17.
/// Features search field, category chips (All, Education, Mentoring, Career),
/// real event list, and event detail modal sheet with register/withdraw actions.
class EventsScreen extends ConsumerStatefulWidget {
  const EventsScreen({super.key});

  @override
  ConsumerState<EventsScreen> createState() => _EventsScreenState();
}

class _EventsScreenState extends ConsumerState<EventsScreen> {
  final TextEditingController _searchController = TextEditingController();

  final List<Map<String, String>> _categories = const [
    {'id': 'ALL', 'label': 'All'},
    {'id': 'EDUCATION', 'label': 'Education'},
    {'id': 'MENTORING', 'label': 'Mentoring'},
    {'id': 'CAREER', 'label': 'Career'},
  ];

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(eventsControllerProvider);
    final displayEvents = state.events;

    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          bottom: false,
          child: RefreshIndicator(
            color: MaatramColors.primaryGold,
            backgroundColor: Colors.white,
            onRefresh: () async {
              await ref.read(eventsControllerProvider.notifier).refresh();
            },
            child: ListView(
              physics: const AlwaysScrollableScrollPhysics(
                parent: BouncingScrollPhysics(),
              ),
              padding: const EdgeInsets.only(bottom: 32),
              children: [
                // 1. Header Title: "Events"
                Padding(
                  padding: const EdgeInsets.fromLTRB(
                    MaatramSpacing.md,
                    MaatramSpacing.md,
                    MaatramSpacing.md,
                    MaatramSpacing.xs,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Events',
                        style: MaatramTypography.headlineLarge.copyWith(
                          fontFamily: 'Georgia',
                          fontSize: 26,
                          fontWeight: FontWeight.bold,
                          color: MaatramColors.deepNavy,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.history_rounded,
                            color: MaatramColors.deepNavy),
                        tooltip: 'My Activity',
                        onPressed: () => context.push(RouteNames.activityPath),
                      ),
                    ],
                  ),
                ),

                // 2. Search Field
                Padding(
                  padding: const EdgeInsets.symmetric(
                      horizontal: MaatramSpacing.md, vertical: 6),
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFE5E7EB)),
                      boxShadow: const [
                        BoxShadow(
                            color: Color(0x06000000),
                            blurRadius: 4,
                            offset: Offset(0, 1)),
                      ],
                    ),
                    child: TextField(
                      controller: _searchController,
                      onChanged: (val) {
                        ref
                            .read(eventsControllerProvider.notifier)
                            .setSearchQuery(val);
                      },
                      decoration: const InputDecoration(
                        hintText: 'Search events...',
                        hintStyle: TextStyle(
                          fontFamily: 'Roboto',
                          fontSize: 13,
                          color: MaatramColors.charcoal400,
                        ),
                        prefixIcon: Icon(Icons.search_rounded,
                            size: 20, color: MaatramColors.charcoal400),
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.symmetric(vertical: 11),
                      ),
                    ),
                  ),
                ),

                // 3. Category Filter Chips Row: "All", "Education", "Mentoring", "Career"
                Padding(
                  padding: const EdgeInsets.symmetric(
                      horizontal: MaatramSpacing.md, vertical: 8),
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: _categories.map((cat) {
                        final isSelected = state.selectedCategory == cat['id'];
                        return Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: GestureDetector(
                            onTap: () {
                              ref
                                  .read(eventsControllerProvider.notifier)
                                  .setCategory(cat['id']!);
                            },
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 14, vertical: 7),
                              decoration: BoxDecoration(
                                color: isSelected
                                    ? MaatramColors.primaryGold
                                    : Colors.white,
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(
                                  color: isSelected
                                      ? MaatramColors.primaryGold
                                      : const Color(0xFFE5E7EB),
                                ),
                                boxShadow: isSelected
                                    ? [
                                        const BoxShadow(
                                            color: Color(0x18F5B817),
                                            blurRadius: 4,
                                            offset: Offset(0, 2))
                                      ]
                                    : null,
                              ),
                              child: Text(
                                cat['label']!,
                                style: TextStyle(
                                  fontFamily: 'Roboto',
                                  fontSize: 12,
                                  fontWeight: isSelected
                                      ? FontWeight.w700
                                      : FontWeight.w500,
                                  color: isSelected
                                      ? MaatramColors.deepNavy
                                      : MaatramColors.charcoal700,
                                ),
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ),

                const SizedBox(height: 6),

                // 4. Events List Body
                if (state.isLoading)
                  const Padding(
                    padding: EdgeInsets.all(40),
                    child: Center(
                      child: CircularProgressIndicator(
                          color: MaatramColors.primaryGold, strokeWidth: 2.5),
                    ),
                  )
                else if (displayEvents.isEmpty)
                  _buildEmptyState()
                else
                  ...displayEvents.map((event) {
                    final isReg = state.registrations.containsKey(event.id);
                    return Padding(
                      padding: const EdgeInsets.symmetric(
                          horizontal: MaatramSpacing.md, vertical: 6),
                      child: _EventListItem(
                        event: event,
                        isRegistered: isReg,
                        onTap: () => _showEventDetailsSheet(
                            context, ref, event, state.registrations[event.id]),
                      ),
                    );
                  }),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
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
              color: Color(0xFFFFF9E6),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.event_note_rounded,
                color: Color(0xFFD97706), size: 28),
          ),
          const SizedBox(height: 12),
          const Text(
            'No matching events found',
            style: TextStyle(
                fontFamily: 'Georgia',
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: MaatramColors.deepNavy),
          ),
          const SizedBox(height: 4),
          const Text(
            'Try adjusting your search query or selecting a different category filter.',
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

  void _showEventDetailsSheet(
    BuildContext context,
    WidgetRef ref,
    EventModel event,
    EventRegistrationModel? registration,
  ) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (sheetCtx) {
        return Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Handle bar
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: const Color(0xFFE5E7EB),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Image header
              ClipRRect(
                borderRadius: BorderRadius.circular(14),
                child: SizedBox(
                  height: 160,
                  width: double.infinity,
                  child: Image.asset(event.assetFallback, fit: BoxFit.cover),
                ),
              ),
              const SizedBox(height: 14),

              // Category Badge
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 3.5),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFFBEB),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFFFDE68A)),
                ),
                child: Text(
                  event.categoryDisplay,
                  style: const TextStyle(
                    fontFamily: 'Roboto',
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFB45309),
                  ),
                ),
              ),
              const SizedBox(height: 8),

              // Title
              Text(
                event.title,
                style: const TextStyle(
                  fontFamily: 'Georgia',
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: MaatramColors.deepNavy,
                ),
              ),
              const SizedBox(height: 8),

              // Description
              Text(
                event.description,
                style: const TextStyle(
                  fontFamily: 'Roboto',
                  fontSize: 13,
                  color: MaatramColors.charcoal700,
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 14),

              // Location & Time info
              Row(
                children: [
                  const Icon(Icons.location_on_outlined,
                      size: 16, color: MaatramColors.charcoal600),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      event.locationDisplay,
                      style: const TextStyle(
                          fontFamily: 'Roboto',
                          fontSize: 12.5,
                          color: MaatramColors.charcoal800),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Row(
                children: [
                  const Icon(Icons.calendar_today_outlined,
                      size: 15, color: MaatramColors.charcoal600),
                  const SizedBox(width: 6),
                  Text(
                    '${event.formattedDate}  •  ${event.formattedTime}',
                    style: const TextStyle(
                        fontFamily: 'Roboto',
                        fontSize: 12.5,
                        color: MaatramColors.charcoal800),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Action button
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: registration != null
                        ? const Color(0xFFEF4444)
                        : MaatramColors.primaryGold,
                    foregroundColor: registration != null
                        ? Colors.white
                        : MaatramColors.deepNavy,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                  ),
                  onPressed: () async {
                    Navigator.pop(sheetCtx);
                    if (registration != null) {
                      await ref
                          .read(eventsControllerProvider.notifier)
                          .withdraw(registration.id);
                    } else {
                      await ref
                          .read(eventsControllerProvider.notifier)
                          .register(event.id);
                    }
                  },
                  child: Text(
                    registration != null
                        ? 'Withdraw Registration'
                        : 'Register for Event',
                    style: const TextStyle(
                        fontFamily: 'Roboto',
                        fontSize: 14,
                        fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Center(
                child: TextButton(
                  onPressed: () {
                    Navigator.pop(sheetCtx);
                    context.push(RouteNames.eventDetailsPath
                        .replaceAll(':id', event.id));
                  },
                  child: const Text(
                    'View Complete Event Details & Venue',
                    style: TextStyle(
                      fontFamily: 'Roboto',
                      fontSize: 12.5,
                      fontWeight: FontWeight.w600,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

/// Horizontal Event List Item matching Master Screen 17
class _EventListItem extends StatelessWidget {
  final EventModel event;
  final bool isRegistered;
  final VoidCallback onTap;

  const _EventListItem({
    required this.event,
    required this.isRegistered,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return MaatramFadeSlideIn(
      direction: SlideDirection.fromBottom,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: MaatramRadii.cardRadius,
            border: Border.all(color: MaatramColors.warmBorder),
            boxShadow: MaatramShadows.card,
          ),
          padding: const EdgeInsets.all(MaatramSpacing.sm),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Thumbnail
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: SizedBox(
                  width: 76,
                  height: 76,
                  child: Image.asset(
                    event.assetFallback,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) =>
                        Container(color: const Color(0xFFF3F4F6)),
                  ),
                ),
              ),
              const SizedBox(width: 12),

              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Category & registered badge
                    Wrap(
                      spacing: 6,
                      runSpacing: 4,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 7, vertical: 2.5),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFFFBEB),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(
                                color: const Color(0xFFFDE68A), width: 0.6),
                          ),
                          child: Text(
                            event.categoryDisplay,
                            style: const TextStyle(
                              fontFamily: 'Roboto',
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFFB45309),
                            ),
                          ),
                        ),
                        if (isRegistered)
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2.5),
                            decoration: BoxDecoration(
                              color: const Color(0xFFECFDF5),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.check_circle_rounded,
                                    size: 10, color: Color(0xFF047857)),
                                SizedBox(width: 3),
                                Text(
                                  'Registered',
                                  style: TextStyle(
                                    fontFamily: 'Roboto',
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF047857),
                                  ),
                                ),
                              ],
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 5),

                    // Title
                    Text(
                      event.title,
                      style: const TextStyle(
                        fontFamily: 'Georgia',
                        fontSize: 13.5,
                        fontWeight: FontWeight.bold,
                        color: MaatramColors.deepNavy,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),

                    // Date & Time
                    Text(
                      '📅 ${event.formattedDate}  |  🕒 ${event.formattedTime}',
                      style: const TextStyle(
                        fontFamily: 'Roboto',
                        fontSize: 10.5,
                        color: MaatramColors.secondaryText,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 4),

              // Chevron Right
              Container(
                width: 26,
                height: 26,
                decoration: const BoxDecoration(
                  color: Color(0xFFFFFBEB),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.chevron_right_rounded,
                    size: 16, color: Color(0xFFB45309)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
