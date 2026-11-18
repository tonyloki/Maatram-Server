import 'package:intl/intl.dart';
import 'package:meta/meta.dart';

double _parseDouble(dynamic value, [double defaultValue = 0.0]) {
  if (value == null) return defaultValue;
  if (value is num) return value.toDouble();
  if (value is String) return double.tryParse(value) ?? defaultValue;
  return defaultValue;
}

int _parseInt(dynamic value, [int defaultValue = 0]) {
  if (value == null) return defaultValue;
  if (value is num) return value.toInt();
  if (value is String) {
    return int.tryParse(value) ??
        (double.tryParse(value)?.toInt() ?? defaultValue);
  }
  return defaultValue;
}

/// Models a single point transaction in the immutable ledger.
@immutable
class PointTransactionModel {
  final String id;
  final String volunteerProfileId;
  final String? eventId;
  final double eventPoints;
  final double hourPoints;
  final double totalPoints;
  final double hoursCredited;
  final String transactionType;
  final String? reason;
  final int cycleYear;
  final DateTime createdAt;

  const PointTransactionModel({
    required this.id,
    required this.volunteerProfileId,
    this.eventId,
    this.eventPoints = 0.0,
    this.hourPoints = 0.0,
    required this.totalPoints,
    this.hoursCredited = 0.0,
    required this.transactionType,
    this.reason,
    required this.cycleYear,
    required this.createdAt,
  });

  factory PointTransactionModel.fromJson(Map<String, dynamic> json) {
    return PointTransactionModel(
      id: json['id']?.toString() ?? '',
      volunteerProfileId: json['volunteer_profile_id']?.toString() ?? '',
      eventId: json['event_id']?.toString(),
      eventPoints: _parseDouble(json['event_points'], 0.0),
      hourPoints: _parseDouble(json['hour_points'], 0.0),
      totalPoints: _parseDouble(json['total_points'], 0.0),
      hoursCredited: _parseDouble(json['hours_credited'], 0.0),
      transactionType:
          json['transaction_type']?.toString() ?? 'EVENT_COMPLETION',
      reason: json['reason']?.toString(),
      cycleYear: _parseInt(json['cycle_year'], DateTime.now().year),
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  String get formattedDate =>
      DateFormat('d MMM yyyy, h:mm a').format(createdAt.toLocal());
  String get shortDate => DateFormat('d MMM yyyy').format(createdAt.toLocal());

  String get pointsDisplay {
    final prefix = totalPoints >= 0 ? '+' : '';
    if (totalPoints % 1 == 0) {
      return '$prefix${totalPoints.toInt()} pts';
    }
    return '$prefix${totalPoints.toStringAsFixed(1)} pts';
  }

  String get displayTitle {
    if (reason != null && reason!.isNotEmpty) return reason!;
    switch (transactionType) {
      case 'EVENT_COMPLETION':
        return 'Event Completion Award';
      case 'MANUAL_ADJUSTMENT':
        return 'Administrative Adjustment';
      case 'BONUS':
        return 'Bonus Karma Award';
      default:
        return 'Points Allocation';
    }
  }
}

/// Paginated ledger response container
@immutable
class PointLedgerModel {
  final List<PointTransactionModel> items;
  final int total;
  final int page;
  final int pageSize;
  final int totalPages;
  final double netPoints;

  const PointLedgerModel({
    required this.items,
    required this.total,
    required this.page,
    required this.pageSize,
    required this.totalPages,
    required this.netPoints,
  });

  factory PointLedgerModel.fromJson(Map<String, dynamic> json) {
    final list = (json['items'] as List<dynamic>?) ?? [];
    return PointLedgerModel(
      items: list
          .map((i) => PointTransactionModel.fromJson(i as Map<String, dynamic>))
          .toList(),
      total: _parseInt(json['total'], 0),
      page: _parseInt(json['page'], 1),
      pageSize: _parseInt(json['page_size'], 50),
      totalPages: _parseInt(json['total_pages'], 1),
      netPoints: _parseDouble(json['net_points'], 0.0),
    );
  }
}
