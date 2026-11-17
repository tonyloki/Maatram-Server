import 'package:intl/intl.dart';
import 'package:meta/meta.dart';

/// Models the backend `AttendanceRecordResponse` from `GET /api/v1/attendance/me`.
@immutable
class AttendanceModel {
  final String id;
  final String eventId;
  final String? eventTitle;
  final DateTime checkInTime;
  final DateTime? checkOutTime;
  final double hoursCredited;
  final String status;

  const AttendanceModel({
    required this.id,
    required this.eventId,
    this.eventTitle,
    required this.checkInTime,
    this.checkOutTime,
    this.hoursCredited = 0.0,
    required this.status,
  });

  factory AttendanceModel.fromJson(Map<String, dynamic> json) {
    return AttendanceModel(
      id: json['id'] as String? ?? '',
      eventId: json['event_id'] as String? ?? '',
      eventTitle: json['event_title'] as String?,
      checkInTime: json['check_in_time'] != null
          ? DateTime.tryParse(json['check_in_time'] as String) ?? DateTime.now()
          : DateTime.now(),
      checkOutTime: json['check_out_time'] != null
          ? DateTime.tryParse(json['check_out_time'] as String)
          : null,
      hoursCredited: json['hours_credited'] != null
          ? (json['hours_credited'] is num
              ? (json['hours_credited'] as num).toDouble()
              : double.tryParse(json['hours_credited'].toString()) ?? 0.0)
          : 0.0,
      status: json['status'] as String? ?? 'VERIFIED',
    );
  }

  String get formattedDate {
    return DateFormat('d MMM yyyy').format(checkInTime.toLocal());
  }

  String get formattedTimeRange {
    final start = DateFormat('h:mm a').format(checkInTime.toLocal());
    if (checkOutTime != null) {
      final end = DateFormat('h:mm a').format(checkOutTime!.toLocal());
      return '$start – $end';
    }
    return start;
  }
}
