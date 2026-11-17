import 'package:meta/meta.dart';

/// Models registration status of current volunteer for events from `GET /api/v1/volunteers/me/registrations`.
@immutable
class EventRegistrationModel {
  final String id;
  final String eventId;
  final String
      status; // SUBSCRIBED, SELECTED, WAITLISTED, NOT_SELECTED, DECLINED, WITHDRAWN

  const EventRegistrationModel({
    required this.id,
    required this.eventId,
    required this.status,
  });

  bool get isSelected => status.toUpperCase() == 'SELECTED';
  bool get isSubscribed => status.toUpperCase() == 'SUBSCRIBED';
  bool get isWaitlisted => status.toUpperCase() == 'WAITLISTED';

  String get statusDisplay {
    switch (status.toUpperCase()) {
      case 'SELECTED':
        return 'Confirmed';
      case 'SUBSCRIBED':
        return 'Registered';
      case 'WAITLISTED':
        return 'Waitlist';
      case 'NOT_SELECTED':
        return 'Not Selected';
      case 'DECLINED':
        return 'Declined';
      case 'WITHDRAWN':
        return 'Withdrawn';
      default:
        return status;
    }
  }

  factory EventRegistrationModel.fromJson(Map<String, dynamic> json) {
    return EventRegistrationModel(
      id: json['id']?.toString() ?? '',
      eventId: json['event_id']?.toString() ?? '',
      status: json['status']?.toString() ?? 'SUBSCRIBED',
    );
  }
}
