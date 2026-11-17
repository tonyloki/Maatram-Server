import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/attendance_model.dart';
import '../../../core/models/event_model.dart';
import '../../../core/models/event_registration_model.dart';
import '../../../core/network/api_client.dart';
import '../../../core/auth/auth_controller.dart';

final eventsRepositoryProvider = Provider<EventsRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return EventsRepository(apiClient: apiClient);
});

class EventsRepository {
  final ApiClient _apiClient;

  EventsRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  /// Fetch events list with optional category and search query
  Future<List<EventModel>> getEvents({
    String? category,
    String? search,
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'limit': limit,
      };
      if (category != null && category.isNotEmpty && category != 'ALL') {
        queryParams['category'] = category.toUpperCase();
      }
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }

      final response = await _apiClient.get<Map<String, dynamic>>(
        '/events',
        queryParameters: queryParams,
      );

      if (response.data != null && response.data!['items'] is List) {
        final items = response.data!['items'] as List;
        return items
            .map((item) => EventModel.fromJson(item as Map<String, dynamic>))
            .toList();
      }
    } catch (_) {
      // Return empty list on failure or network error
      return [];
    }
    return [];
  }

  /// Fetch event details by ID
  Future<EventModel?> getEventById(String eventId) async {
    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        '/events/$eventId',
      );
      if (response.data != null) {
        return EventModel.fromJson(response.data!);
      }
    } catch (_) {
      return null;
    }
    return null;
  }

  /// Fetch authenticated volunteer's registrations
  Future<List<EventRegistrationModel>> getMyRegistrations() async {
    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        '/registrations/me',
      );

      if (response.data != null && response.data!['items'] is List) {
        final items = response.data!['items'] as List;
        return items
            .map((item) =>
                EventRegistrationModel.fromJson(item as Map<String, dynamic>))
            .toList();
      }
    } catch (_) {
      // Fallback or empty
      return [];
    }
    return [];
  }

  /// Fetch authenticated volunteer's attendance records
  Future<List<AttendanceModel>> getMyAttendance() async {
    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        '/attendance/me',
      );

      if (response.data != null && response.data!['items'] is List) {
        final items = response.data!['items'] as List;
        return items
            .map((item) =>
                AttendanceModel.fromJson(item as Map<String, dynamic>))
            .toList();
      }
    } catch (_) {
      // Fallback or empty
      return [];
    }
    return [];
  }

  /// Register for an event
  Future<bool> registerForEvent(String eventId) async {
    try {
      await _apiClient.post<Map<String, dynamic>>(
        '/events/$eventId/register',
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  /// Withdraw from an event registration
  Future<bool> withdrawRegistration(String registrationId) async {
    try {
      await _apiClient.post<Map<String, dynamic>>(
        '/registrations/$registrationId/withdraw',
      );
      return true;
    } catch (_) {
      return false;
    }
  }
}
