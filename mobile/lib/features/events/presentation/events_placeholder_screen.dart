import 'package:flutter/material.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/widgets/badges/category_badge.dart';
import '../../../core/widgets/badges/status_badge.dart';
import '../../../core/widgets/cards/maatram_event_card.dart';
import '../../../core/widgets/inputs/maatram_search_field.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../../../core/widgets/navigation/section_header.dart';

/// M1 Events Destination Shell demonstrating search, event card primitives, and filters.
class EventsPlaceholderScreen extends StatelessWidget {
  const EventsPlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          title: const Text('Discover Events'),
        ),
        body: ListView(
          padding: MaatramSpacing.screenPadding,
          children: const [
            MaatramSearchField(
              hintText: 'Search mock interviews, school visits...',
            ),
            SizedBox(height: MaatramSpacing.lg),
            MaatramSectionHeader(
              title: 'Featured Opportunities',
              subtitle: 'Participate and earn gamification points',
            ),
            SizedBox(height: MaatramSpacing.sm),
            MaatramEventCard(
              title: 'Mock Interview & Aptitude Mentorship 2026',
              category: VolunteerCategory.student,
              dateText: 'Sat, Nov 22',
              timeText: '09:30 AM',
              locationText: 'Chennai Tech Park (On-site)',
              points: 10,
              status: MaatramStatus.approved,
            ),
            SizedBox(height: MaatramSpacing.md),
            MaatramEventCard(
              title: 'Rural School Digital Literacy Workshop',
              category: VolunteerCategory.corporate,
              dateText: 'Sun, Nov 30',
              timeText: '10:00 AM',
              locationText: 'Virtual Zoom Session',
              points: 15,
              isOnline: true,
              status: MaatramStatus.live,
            ),
          ],
        ),
      ),
    );
  }
}
