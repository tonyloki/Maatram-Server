import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/leaderboard_model.dart';
import '../../../core/network/api_client.dart';
import '../../../core/auth/auth_controller.dart';

final leaderboardRepositoryProvider = Provider<LeaderboardRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return LeaderboardRepository(apiClient: apiClient);
});

class LeaderboardRepository {
  final ApiClient _apiClient;

  LeaderboardRepository({required ApiClient apiClient})
      : _apiClient = apiClient;

  /// Fetch leaderboard ranking list for the given category tab
  Future<List<LeaderboardItemModel>> getLeaderboard({
    String category = 'overall',
  }) async {
    final cat = category.toLowerCase();
    String endpoint;
    if (cat == 'students' || cat == 'student') {
      endpoint = '/gamification/leaderboard/student';
    } else if (cat == 'alumni') {
      endpoint = '/gamification/leaderboard/alumni';
    } else if (cat == 'corporate') {
      endpoint = '/gamification/leaderboard/corporate';
    } else {
      endpoint = '/gamification/leaderboard/overall';
    }

    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        endpoint,
        queryParameters: {'page': 1, 'page_size': 50},
      );

      if (response.data != null && response.data!['items'] is List) {
        final items = response.data!['items'] as List;
        return items
            .map((item) =>
                LeaderboardItemModel.fromJson(item as Map<String, dynamic>))
            .toList();
      }
    } catch (_) {
      // Fallback
      return [];
    }
    return [];
  }
}
