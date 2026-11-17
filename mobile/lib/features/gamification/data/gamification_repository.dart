import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/models/achievement_model.dart';
import '../../../core/models/gamification_summary_model.dart';
import '../../../core/models/point_ledger_model.dart';
import '../../../core/network/api_client.dart';

final gamificationRepositoryProvider = Provider<GamificationRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return GamificationRepository(apiClient: apiClient);
});

class GamificationRepository {
  final ApiClient _apiClient;

  GamificationRepository({required ApiClient apiClient})
      : _apiClient = apiClient;

  /// Retrieve personal gamification summary
  Future<GamificationSummaryModel?> getSummary() async {
    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        '/gamification/summary',
      );
      if (response.data != null) {
        return GamificationSummaryModel.fromJson(response.data!);
      }
    } catch (_) {
      return null;
    }
    return null;
  }

  /// Retrieve paginated point ledger transactions
  Future<PointLedgerModel?> getLedger({int page = 1, int pageSize = 50}) async {
    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        '/gamification/ledger',
        queryParameters: {'page': page, 'page_size': pageSize},
      );
      if (response.data != null) {
        return PointLedgerModel.fromJson(response.data!);
      }
    } catch (_) {
      return null;
    }
    return null;
  }

  /// Retrieve available and earned achievements/badges
  Future<VolunteerAchievementsModel?> getAchievements() async {
    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        '/gamification/achievements/me',
      );
      if (response.data != null) {
        return VolunteerAchievementsModel.fromJson(response.data!);
      }
    } catch (_) {
      return null;
    }
    return null;
  }
}
