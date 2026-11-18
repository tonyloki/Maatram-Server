import 'package:intl/intl.dart';
import 'package:meta/meta.dart';

/// Models the backend `EventResponse` from `GET /api/v1/events`.
@immutable
class EventModel {
  final String id;
  final String title;
  final String description;
  final String category; // EDUCATION, HEALTHCARE, COMMUNITY, ENVIRONMENT, etc.
  final String mode; // PHYSICAL, VIRTUAL, HYBRID
  final DateTime startTime;
  final DateTime endTime;
  final String? locationName;
  final String? address;
  final String? city;
  final int maxVolunteers;
  final int registeredCount;
  final String status;
  final String? coverImageUrl;

  const EventModel({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.mode,
    required this.startTime,
    required this.endTime,
    this.locationName,
    this.address,
    this.city,
    required this.maxVolunteers,
    this.registeredCount = 0,
    required this.status,
    this.coverImageUrl,
  });

  /// Formatted date e.g. "26 Nov 2026"
  String get formattedDate {
    return DateFormat('d MMM yyyy').format(startTime.toLocal());
  }

  /// Formatted time e.g. "2:30 PM – 6:30 PM"
  String get formattedTime {
    final start = DateFormat('h:mm a').format(startTime.toLocal());
    final end = DateFormat('h:mm a').format(endTime.toLocal());
    return '$start – $end';
  }

  /// Category display name e.g. "School Visit", "Mentorship", "Community"
  String get categoryDisplay {
    switch (category.toUpperCase()) {
      case 'EDUCATION':
        return 'School Visit';
      case 'HEALTHCARE':
        return 'Health Camp';
      case 'COMMUNITY':
        return 'Community Outreach';
      case 'ENVIRONMENT':
        return 'Green Drive';
      case 'DISASTER_RELIEF':
        return 'Relief Support';
      case 'SPECIAL_NEEDS':
        return 'Special Needs';
      default:
        // Title case formatting
        if (category.isEmpty) return 'Volunteering';
        return category[0].toUpperCase() + category.substring(1).toLowerCase();
    }
  }

  String get locationDisplay {
    if (locationName != null && locationName!.isNotEmpty) {
      if (city != null &&
          city!.isNotEmpty &&
          !locationName!.toLowerCase().contains(city!.toLowerCase())) {
        return '$locationName, $city';
      }
      return locationName!;
    }
    if (city != null && city!.isNotEmpty) {
      return city!;
    }
    if (mode.toUpperCase() == 'VIRTUAL') {
      return 'Online / Virtual Session';
    }
    return 'Venue TBD';
  }

  /// Select a suitable local asset fallback if coverImageUrl is missing
  String get assetFallback {
    final cat = category.toUpperCase();
    if (cat.contains('EDU') || title.toLowerCase().contains('school')) {
      return 'assets/images/school-visit.jpg';
    }
    if (title.toLowerCase().contains('interview') || cat.contains('MENTOR')) {
      return 'assets/images/mock-interview.jpg';
    }
    if (title.toLowerCase().contains('bgv') ||
        title.toLowerCase().contains('support')) {
      return 'assets/images/bgv-support.jpg';
    }
    return 'assets/images/community-engagement.jpg';
  }

  static int _parseInt(dynamic value, [int defaultValue = 0]) {
    if (value == null) return defaultValue;
    if (value is num) return value.toInt();
    if (value is String) {
      return int.tryParse(value) ??
          (double.tryParse(value)?.toInt() ?? defaultValue);
    }
    return defaultValue;
  }

  factory EventModel.fromJson(Map<String, dynamic> json) {
    DateTime parseDate(dynamic val) {
      if (val is String) {
        return DateTime.tryParse(val) ?? DateTime.now();
      }
      return DateTime.now();
    }

    final rawLocation = json['location_name']?.toString() ?? json['location']?.toString();

    return EventModel(
      id: json['id']?.toString() ?? '',
      title: json['title']?.toString() ?? 'Volunteering Opportunity',
      description: json['description']?.toString() ?? '',
      category: json['category']?.toString() ?? 'COMMUNITY',
      mode: json['mode']?.toString() ?? 'PHYSICAL',
      startTime: parseDate(json['start_time']),
      endTime: parseDate(json['end_time']),
      locationName: rawLocation,
      address: json['address']?.toString() ?? rawLocation,
      city: json['city']?.toString(),
      maxVolunteers: _parseInt(
        json['capacity_required'] ??
            json['volunteer_capacity'] ??
            json['max_volunteers'],
        10,
      ),
      registeredCount: _parseInt(json['registered_count'], 0),
      status: json['status']?.toString() ?? 'PUBLISHED',
      coverImageUrl: json['cover_image_url']?.toString(),
    );
  }
}
