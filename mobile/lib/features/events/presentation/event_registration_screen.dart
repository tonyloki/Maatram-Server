import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/models/event_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/badges/category_badge.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/inputs/maatram_text_field.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../data/events_repository.dart';

class EventRegistrationScreen extends ConsumerStatefulWidget {
  final String eventId;
  final EventModel? event;

  const EventRegistrationScreen({super.key, required this.eventId, this.event});

  @override
  ConsumerState<EventRegistrationScreen> createState() =>
      _EventRegistrationScreenState();
}

class _EventRegistrationScreenState
    extends ConsumerState<EventRegistrationScreen> {
  final TextEditingController _notesController = TextEditingController();
  bool _confirmedAvailability = true;
  bool _agreedToCodeOfConduct = true;
  bool _isSubmitting = false;
  bool _isRegisteredSuccessfully = false;
  String? _errorMessage;
  EventModel? _event;

  VolunteerCategory _parseCategory(String cat) {
    final lower = cat.toLowerCase();
    if (lower.contains('student')) return VolunteerCategory.student;
    if (lower.contains('alumni')) return VolunteerCategory.alumni;
    return VolunteerCategory.corporate;
  }

  @override
  void initState() {
    super.initState();
    _event = widget.event;
    if (_event == null) {
      _loadEvent();
    }
  }

  Future<void> _loadEvent() async {
    final repo = ref.read(eventsRepositoryProvider);
    final e = await repo.getEventById(widget.eventId);
    if (mounted) {
      setState(() => _event = e);
    }
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _submitRegistration() async {
    if (!_confirmedAvailability || !_agreedToCodeOfConduct) {
      setState(() {
        _errorMessage = 'Please confirm availability and agree to guidelines.';
      });
      return;
    }

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
    });

    final repo = ref.read(eventsRepositoryProvider);
    final success = await repo.registerForEvent(widget.eventId);

    if (mounted) {
      setState(() {
        _isSubmitting = false;
        if (success) {
          _isRegisteredSuccessfully = true;
        } else {
          _errorMessage =
              'Unable to register at this time. The event may be full or already registered.';
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authControllerProvider).user;

    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_rounded,
                color: MaatramColors.deepNavy),
            onPressed: () => context.pop(),
          ),
          title: Text(
            _isRegisteredSuccessfully
                ? 'Registration Confirmed'
                : 'Event Registration',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
        ),
        body: _isRegisteredSuccessfully
            ? _buildSuccessView()
            : _buildRegistrationForm(user?.displayName ?? 'Volunteer'),
      ),
    );
  }

  Widget _buildSuccessView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(MaatramSpacing.lg),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: const BoxDecoration(
                color: MaatramColors.success,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.check_rounded,
                  color: Colors.white, size: 40),
            ),
            const SizedBox(height: MaatramSpacing.md),
            Text(
              'Registration Confirmed!',
              style: MaatramTypography.headlineMedium.copyWith(
                fontFamily: 'Georgia',
                fontWeight: FontWeight.bold,
                color: MaatramColors.deepNavy,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Your slot has been reserved. You can review and manage this in My Activity.',
              style: MaatramTypography.bodyMedium.copyWith(
                color: MaatramColors.secondaryText,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MaatramSpacing.xl),
            MaatramButton(
              label: 'View My Activity',
              onPressed: () {
                context.go(RouteNames.activityPath);
              },
            ),
            const SizedBox(height: 12),
            TextButton(
              onPressed: () => context.go(RouteNames.eventsPath),
              child: Text(
                'Browse More Events',
                style: MaatramTypography.labelLarge.copyWith(
                  color: MaatramColors.deepNavy,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRegistrationForm(String volunteerName) {
    return ListView(
      padding: const EdgeInsets.all(MaatramSpacing.md),
      children: [
        if (_errorMessage != null) ...[
          Container(
            padding: const EdgeInsets.all(MaatramSpacing.md),
            decoration: BoxDecoration(
              color: const Color(0xFFFEF2F2),
              borderRadius: MaatramRadii.cardRadius,
              border: Border.all(color: const Color(0xFFFCA5A5)),
            ),
            child: Row(
              children: [
                const Icon(Icons.error_outline_rounded,
                    color: MaatramColors.error, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _errorMessage!,
                    style: MaatramTypography.bodySmall
                        .copyWith(color: MaatramColors.error),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: MaatramSpacing.md),
        ],

        // Event Summary Card
        if (_event != null) ...[
          Container(
            padding: const EdgeInsets.all(MaatramSpacing.md),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: MaatramRadii.cardRadius,
              border: Border.all(color: MaatramColors.warmBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                MaatramCategoryBadge(
                    category: _parseCategory(_event!.category)),
                const SizedBox(height: 8),
                Text(
                  _event!.title,
                  style: MaatramTypography.titleMedium.copyWith(
                    fontFamily: 'Georgia',
                    fontWeight: FontWeight.bold,
                    color: MaatramColors.deepNavy,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.calendar_today_rounded,
                        size: 16, color: MaatramColors.secondaryText),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        '${_event!.formattedDate} • ${_event!.formattedTime}',
                        style: MaatramTypography.bodySmall
                            .copyWith(color: MaatramColors.secondaryText),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: MaatramSpacing.md),
        ],

        // Volunteer confirmation card
        Container(
          padding: const EdgeInsets.all(MaatramSpacing.md),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: MaatramRadii.cardRadius,
            border: Border.all(color: MaatramColors.warmBorder),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Registering As',
                style: MaatramTypography.labelLarge.copyWith(
                  fontWeight: FontWeight.bold,
                  color: MaatramColors.deepNavy,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                volunteerName,
                style: MaatramTypography.bodyMedium.copyWith(
                  color: MaatramColors.deepNavy,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: MaatramSpacing.md),

        // Volunteer Notes Field
        MaatramTextField(
          label: 'Notes / Dietary / Transportation (Optional)',
          hintText: 'Any special requirements or notes for the coordinator',
          controller: _notesController,
          maxLines: 3,
        ),
        const SizedBox(height: MaatramSpacing.md),

        // Commitments Checklist
        Container(
          padding: const EdgeInsets.all(MaatramSpacing.md),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: MaatramRadii.cardRadius,
            border: Border.all(color: MaatramColors.warmBorder),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Volunteer Commitment',
                style: MaatramTypography.labelLarge.copyWith(
                  fontWeight: FontWeight.bold,
                  color: MaatramColors.deepNavy,
                ),
              ),
              const SizedBox(height: 8),
              Material(
                color: Colors.transparent,
                child: Column(
                  children: [
                    CheckboxListTile(
                      value: _confirmedAvailability,
                      activeColor: MaatramColors.primaryGold,
                      contentPadding: EdgeInsets.zero,
                      controlAffinity: ListTileControlAffinity.leading,
                      title: Text(
                        'I confirm my availability and will attend on time.',
                        style: MaatramTypography.bodySmall
                            .copyWith(color: MaatramColors.deepNavy),
                      ),
                      onChanged: (val) =>
                          setState(() => _confirmedAvailability = val ?? false),
                    ),
                    CheckboxListTile(
                      value: _agreedToCodeOfConduct,
                      activeColor: MaatramColors.primaryGold,
                      contentPadding: EdgeInsets.zero,
                      controlAffinity: ListTileControlAffinity.leading,
                      title: Text(
                        'I agree to adhere to Maatram volunteer code of conduct.',
                        style: MaatramTypography.bodySmall
                            .copyWith(color: MaatramColors.deepNavy),
                      ),
                      onChanged: (val) =>
                          setState(() => _agreedToCodeOfConduct = val ?? false),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: MaatramSpacing.lg),

        MaatramButton(
          label: 'Confirm Registration',
          isLoading: _isSubmitting,
          onPressed: _submitRegistration,
        ),
        const SizedBox(height: MaatramSpacing.lg),
      ],
    );
  }
}
