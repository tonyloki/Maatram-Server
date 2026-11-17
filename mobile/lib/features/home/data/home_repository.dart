import '../../../core/models/event_model.dart';
import '../../../core/models/event_registration_model.dart';
import '../../../core/models/gamification_summary_model.dart';
import '../../../core/models/volunteer_profile_model.dart';
import '../../../core/network/api_client.dart';

/// Repository abstracting backend endpoints for the volunteer Home Screen dashboard.
class HomeRepository {
  final ApiClient _apiClient;

  HomeRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  /// Fetch authenticated volunteer profile details
  Future<VolunteerProfileModel> getProfile() async {
    final response =
        await _apiClient.get<Map<String, dynamic>>('/volunteers/me');
    if (response.data != null) {
      return VolunteerProfileModel.fromJson(response.data!);
    }
    throw const ApiException(
      code: 'EMPTY_PROFILE',
      message: 'Failed to retrieve profile data from server.',
    );
  }

  /// Fetch current cycle gamification impact summary
  Future<GamificationSummaryModel> getGamificationSummary() async {
    try {
      final response =
          await _apiClient.get<Map<String, dynamic>>('/gamification/summary');
      if (response.data != null) {
        return GamificationSummaryModel.fromJson(response.data!);
      }
    } catch (_) {
      // Re-throw or handle in controller
      rethrow;
    }
    return GamificationSummaryModel.empty();
  }

  /// Fetch published upcoming volunteering opportunities
  Future<List<EventModel>> getUpcomingEvents({int limit = 10}) async {
    final response = await _apiClient.get<Map<String, dynamic>>(
      '/events',
      queryParameters: {
        'status': 'PUBLISHED',
        'limit': limit,
        'page': 1,
      },
    );

    if (response.data != null && response.data!['items'] is List) {
      final items = response.data!['items'] as List;
      return items
          .map((item) => EventModel.fromJson(item as Map<String, dynamic>))
          .toList();
    }
    return [];
  }

  /// Fetch current volunteer's registrations mapped by eventId
  Future<Map<String, EventRegistrationModel>> getRegistrations(
      {int limit = 20}) async {
    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        '/registrations/me',
        queryParameters: {'limit': limit, 'page': 1},
      );

      if (response.data != null && response.data!['items'] is List) {
        final items = response.data!['items'] as List;
        final map = <String, EventRegistrationModel>{};
        for (final item in items) {
          final reg =
              EventRegistrationModel.fromJson(item as Map<String, dynamic>);
          map[reg.eventId] = reg;
        }
        return map;
      }
    } catch (_) {
      // Fallback empty registrations map if endpoint fails or not found
      return {};
    }
    return {};
  }

  /// Fetch unread notifications count
  Future<int> getUnreadNotificationCount() async {
    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        '/notifications/unread-count',
      );
      if (response.data != null && response.data!['unread_count'] is int) {
        return response.data!['unread_count'] as int;
      }
    } catch (_) {
      // Fallback
    }
    return 0;
  }
}
