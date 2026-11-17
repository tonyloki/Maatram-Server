import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/models/attendance_model.dart';
import 'package:maatram_mobile/core/models/event_model.dart';
import 'package:maatram_mobile/core/network/api_client.dart';
import 'package:maatram_mobile/features/events/data/events_repository.dart';
import 'package:maatram_mobile/features/events/presentation/activity_details_screen.dart';
import 'package:maatram_mobile/features/events/presentation/event_details_screen.dart';
import 'package:maatram_mobile/features/events/presentation/event_registration_screen.dart';

class MockEventsRepository extends EventsRepository {
  MockEventsRepository() : super(apiClient: ApiClient());

  @override
  Future<EventModel> getEventById(String eventId) async {
    return EventModel(
      id: eventId,
      title: 'Government High School Career Guidance',
      description:
          'Mentoring underprivileged students on career opportunities.',
      category: 'STUDENT',
      mode: 'OFFLINE',
      locationName: 'Government High School',
      address: 'Ashok Nagar, Chennai',
      city: 'Chennai',
      startTime: DateTime(2026, 11, 26, 9, 30),
      endTime: DateTime(2026, 11, 26, 13, 30),
      maxVolunteers: 25,
      registeredCount: 18,
      status: 'PUBLISHED',
    );
  }

  @override
  Future<bool> registerForEvent(String eventId) async {
    return true;
  }
}

void main() {
  final mockRepo = MockEventsRepository();

  Widget buildTestableWidget(Widget child) {
    return ProviderScope(
      overrides: [
        eventsRepositoryProvider.overrideWithValue(mockRepo),
      ],
      child: MaterialApp(
        home: child,
      ),
    );
  }

  group('Phase 4 Event Screens Tests', () {
    testWidgets(
        'EventDetailsScreen displays event info and registration button',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(
        buildTestableWidget(const EventDetailsScreen(eventId: 'event-101')),
      );
      await tester.pumpAndSettle();

      expect(find.text('Event Details'), findsOneWidget);
      expect(
          find.text('Government High School Career Guidance'), findsOneWidget);
      expect(find.text('Register for Event'), findsOneWidget);
    });

    testWidgets(
        'EventRegistrationScreen displays registration form and confirmation',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(
        buildTestableWidget(
            const EventRegistrationScreen(eventId: 'event-101')),
      );
      await tester.pumpAndSettle();

      expect(find.text('Event Registration'), findsOneWidget);

      // Check both commitment checkboxes
      final checkTiles = find.byType(CheckboxListTile);
      for (final element in checkTiles.evaluate()) {
        final tile = element.widget as CheckboxListTile;
        tile.onChanged?.call(true);
      }
      await tester.pumpAndSettle();

      // Submit
      final submitBtn = find.text('Confirm Registration');
      await tester.ensureVisible(submitBtn);
      await tester.pumpAndSettle();
      await tester.tap(submitBtn);
      await tester.pumpAndSettle();

      // Verify confirmation view
      expect(find.text('Registration Confirmed!'), findsOneWidget);
      expect(find.text('View My Activity'), findsOneWidget);
    });

    testWidgets(
        'ActivityDetailsScreen displays verified hours and certificate disclaimer',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final sampleAttendance = AttendanceModel(
        id: 'att-1',
        eventId: 'event-101',
        eventTitle: 'School Visit - Government High School',
        checkInTime: DateTime(2026, 11, 26, 9, 30),
        checkOutTime: DateTime(2026, 11, 26, 14, 0),
        hoursCredited: 4.5,
        status: 'VERIFIED',
      );

      await tester.pumpWidget(
        buildTestableWidget(ActivityDetailsScreen(
          activityId: 'att-1',
          attendance: sampleAttendance,
        )),
      );
      await tester.pumpAndSettle();

      expect(find.text('Activity Details'), findsOneWidget);
      expect(
          find.text('School Visit - Government High School'), findsOneWidget);
      expect(find.text('4.5 hrs'), findsOneWidget);
      expect(find.text('+19 pts'), findsOneWidget);

      // Verify governance compliant certificate disclaimer
      expect(find.text('Participation Certificate'), findsOneWidget);
      expect(find.text('Certificate Unavailable (Pending Official Policy)'),
          findsOneWidget);
    });
  });
}
