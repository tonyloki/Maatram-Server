import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/models/event_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/badges/category_badge.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/feedback/skeleton_loader.dart';
import '../data/events_repository.dart';

class EventDetailsScreen extends ConsumerStatefulWidget {
  final String eventId;

  const EventDetailsScreen({super.key, required this.eventId});

  @override
  ConsumerState<EventDetailsScreen> createState() => _EventDetailsScreenState();
}

class _EventDetailsScreenState extends ConsumerState<EventDetailsScreen> {
  EventModel? _event;
  bool _isLoading = true;
  String? _errorMessage;

  VolunteerCategory _parseCategory(String cat) {
    final lower = cat.toLowerCase();
    if (lower.contains('student')) return VolunteerCategory.student;
    if (lower.contains('alumni')) return VolunteerCategory.alumni;
    return VolunteerCategory.corporate;
  }

  @override
  void initState() {
    super.initState();
    _loadEventDetails();
  }

  Future<void> _loadEventDetails() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final repo = ref.read(eventsRepositoryProvider);
    final event = await repo.getEventById(widget.eventId);

    if (mounted) {
      setState(() {
        _event = event;
        _isLoading = false;
        if (event == null) {
          _errorMessage = 'Event details currently unavailable.';
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Plain cream scaffold — no organic background wrapper (matches reference)
    return Scaffold(
      backgroundColor: const Color(0xFFFAF8F5),
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Material(
            color: Colors.white,
            shape: const CircleBorder(),
            elevation: 2,
            child: InkWell(
              customBorder: const CircleBorder(),
              onTap: () => context.pop(),
              child: const Padding(
                padding: EdgeInsets.all(6.0),
                child: Icon(Icons.arrow_back_rounded,
                    color: MaatramColors.deepNavy, size: 20),
              ),
            ),
          ),
        ),
        title: Text(
          'Event Details',
          style: MaatramTypography.headlineMedium.copyWith(
            fontFamily: 'Georgia',
            fontWeight: FontWeight.bold,
            color: MaatramColors.deepNavy,
          ),
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Material(
              color: Colors.white,
              shape: const CircleBorder(),
              elevation: 2,
              child: InkWell(
                customBorder: const CircleBorder(),
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Sharing event details...')),
                  );
                },
                child: const Padding(
                  padding: EdgeInsets.all(6.0),
                  child: Icon(Icons.share_outlined,
                      color: MaatramColors.deepNavy, size: 20),
                ),
              ),
            ),
          ),
        ],
      ),
      body: _isLoading
          ? _buildLoadingSkeleton()
          : _errorMessage != null || _event == null
              ? _buildError()
              : _buildContent(_event!),
      bottomNavigationBar: _event == null || _isLoading
          ? null
          : Container(
              padding: const EdgeInsets.fromLTRB(
                  MaatramSpacing.md,
                  MaatramSpacing.sm,
                  MaatramSpacing.md,
                  MaatramSpacing.md),
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(
                  top: BorderSide(color: Color(0xFFEFECE6), width: 1.0),
                ),
              ),
              child: SafeArea(
                child: MaatramButton(
                  label: 'Register for Event',
                  onPressed: () {
                    context.push(
                      RouteNames.eventRegistrationPath
                          .replaceAll(':id', _event!.id),
                      extra: _event,
                    );
                  },
                ),
              ),
            ),
    );
  }

  Widget _buildLoadingSkeleton() {
    return Column(
      children: [
        // Hero skeleton — full-width, no margin
        const MaatramSkeletonBox(
          width: double.infinity,
          height: 230,
          borderRadius: BorderRadius.zero,
        ),
        Padding(
          padding: const EdgeInsets.all(MaatramSpacing.md),
          child: Column(
            children: const [
              SizedBox(height: 12),
              MaatramSkeletonBox(
                  width: double.infinity,
                  height: 28,
                  borderRadius: BorderRadius.all(Radius.circular(8))),
              SizedBox(height: 10),
              MaatramSkeletonBox(
                  width: double.infinity,
                  height: 20,
                  borderRadius: BorderRadius.all(Radius.circular(8))),
              SizedBox(height: 10),
              MaatramSkeletonBox(
                  width: double.infinity,
                  height: 20,
                  borderRadius: BorderRadius.all(Radius.circular(8))),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(MaatramSpacing.lg),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.event_busy_rounded,
                size: 56, color: MaatramColors.secondaryText),
            const SizedBox(height: 16),
            Text(_errorMessage ?? 'Event not found',
                style: MaatramTypography.titleMedium
                    .copyWith(color: MaatramColors.deepNavy)),
            const SizedBox(height: 16),
            MaatramButton(
              label: 'Back to Events',
              onPressed: () => context.pop(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContent(EventModel event) {
    return CustomScrollView(
      slivers: [
        SliverToBoxAdapter(child: _buildHero(event)),
        SliverToBoxAdapter(
          child: Container(
            // White content area with rounded top corners only — overlaps hero bottom
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(24),
                topRight: Radius.circular(24),
              ),
            ),
            // Pull up over the bottom of the hero image
            transform: Matrix4.translationValues(0, -24, 0),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(
                  MaatramSpacing.md, MaatramSpacing.md, MaatramSpacing.md, 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Badges row: category + registered count (matches reference)
                  Row(
                    children: [
                      MaatramCategoryBadge(
                          category: _parseCategory(event.category)),
                      const SizedBox(width: MaatramSpacing.sm),
                      _buildRegisteredBadge(event),
                    ],
                  ),
                  const SizedBox(height: MaatramSpacing.sm),

                  // Event title — Georgia bold, large (matches reference)
                  Text(
                    event.title,
                    style: MaatramTypography.headlineLarge.copyWith(
                      fontFamily: 'Georgia',
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                  const SizedBox(height: MaatramSpacing.md),

                  // Date/time/location as plain icon-rows (not card boxes — matches reference)
                  _buildInfoRow(
                    icon: Icons.calendar_today_outlined,
                    text: event.formattedDate,
                    bold: true,
                  ),
                  const SizedBox(height: 8),
                  _buildInfoRow(
                    icon: Icons.access_time_outlined,
                    text: event.formattedTime,
                  ),
                  const SizedBox(height: 8),
                  _buildInfoRow(
                    icon: Icons.location_on_outlined,
                    text: event.locationName ?? 'Location TBD',
                    bold: true,
                  ),
                  if (event.address != null || event.city != null) ...[
                    Padding(
                      padding: const EdgeInsets.only(left: 28),
                      child: Text(
                        [event.address, event.city]
                            .where((s) => s != null && s.isNotEmpty)
                            .join(', '),
                        style: MaatramTypography.bodySmall.copyWith(
                          color: MaatramColors.secondaryText,
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                  ],
                  _buildInfoRow(
                    icon: Icons.person_outline_rounded,
                    text: 'Coordinator: TBD',
                  ),

                  const SizedBox(height: MaatramSpacing.md),
                  const Divider(color: Color(0xFFE8E4DF)),
                  const SizedBox(height: MaatramSpacing.md),

                  // About This Event section (matches reference layout)
                  Text(
                    'About This Event',
                    style: MaatramTypography.titleMedium.copyWith(
                      fontFamily: 'Georgia',
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    event.description.isNotEmpty
                        ? event.description
                        : 'Join fellow volunteers to make a tangible impact in our community.',
                    style: MaatramTypography.bodyMedium.copyWith(
                      color: MaatramColors.deepNavy,
                      height: 1.5,
                    ),
                  ),

                  // Prerequisites section (shown in reference)
                  // Only shown if the model has requirements in future; placeholder for extensibility

                  const SizedBox(height: MaatramSpacing.xl),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  /// Full-width hero with NO rounded corners, NO horizontal margin (~230dp tall).
  Widget _buildHero(EventModel event) {
    return SizedBox(
      height: 230,
      width: double.infinity,
      child: Stack(
        fit: StackFit.expand,
        children: [
          // Cover image — edge-to-edge, no border radius
          Image(
            image: event.coverImageUrl != null &&
                    event.coverImageUrl!.isNotEmpty
                ? NetworkImage(event.coverImageUrl!) as ImageProvider
                : AssetImage(event.assetFallback),
            fit: BoxFit.cover,
          ),
          // Bottom gradient overlay only (subtle — no rounded corners)
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                stops: const [0.5, 1.0],
                colors: [
                  Colors.transparent,
                  Colors.black.withValues(alpha: 0.35),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Plain icon-text row (no card box — matches reference style)
  Widget _buildInfoRow({
    required IconData icon,
    required String text,
    bool bold = false,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 18, color: MaatramColors.deepNavy),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: MaatramTypography.bodyMedium.copyWith(
              color: MaatramColors.deepNavy,
              fontWeight: bold ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ),
      ],
    );
  }

  /// Green registered count badge (matches reference "15 / 20 Registered")
  Widget _buildRegisteredBadge(EventModel event) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F5E9),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        '${event.registeredCount} / ${event.maxVolunteers} Registered',
        style: MaatramTypography.labelSmall.copyWith(
          color: const Color(0xFF2E7D32),
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
