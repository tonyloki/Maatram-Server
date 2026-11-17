import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/models/consent_model.dart';
import '../../../core/models/notification_model.dart';
import '../../../core/models/volunteer_profile_model.dart';
import '../../../core/network/api_client.dart';

final moreRepositoryProvider = Provider<MoreRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return MoreRepository(apiClient: apiClient);
});

class MoreRepository {
  final ApiClient _apiClient;

  MoreRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  /// Fetch in-app notifications
  Future<NotificationListModel?> getNotifications({
    bool unreadOnly = false,
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        '/notifications/me',
        queryParameters: {
          'unread_only': unreadOnly,
          'page': page,
          'limit': limit,
        },
      );
      if (response.data != null) {
        return NotificationListModel.fromJson(response.data!);
      }
    } catch (_) {
      return null;
    }
    return null;
  }

  /// Mark single notification as read
  Future<bool> markNotificationAsRead(String notificationId) async {
    try {
      await _apiClient.patch<Map<String, dynamic>>(
        '/notifications/$notificationId/read',
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  /// Mark all notifications as read
  Future<bool> markAllNotificationsAsRead() async {
    try {
      await _apiClient.post<Map<String, dynamic>>(
        '/notifications/read-all',
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  /// Fetch affirmative consent record
  Future<ConsentModel?> getConsent() async {
    try {
      final response = await _apiClient.get<Map<String, dynamic>>(
        '/consent/me',
      );
      if (response.data != null) {
        return ConsentModel.fromJson(response.data!);
      }
    } catch (_) {
      return null;
    }
    return null;
  }

  /// Update affirmative consent record
  Future<ConsentModel?> updateConsent(ConsentModel updated) async {
    try {
      final response = await _apiClient.put<Map<String, dynamic>>(
        '/consent/me',
        data: updated.toUpdateJson(),
      );
      if (response.data != null) {
        return ConsentModel.fromJson(response.data!);
      }
    } catch (_) {
      return null;
    }
    return null;
  }

  /// Update volunteer profile
  Future<VolunteerProfileModel?> updateProfile(
      Map<String, dynamic> updateData) async {
    try {
      final response = await _apiClient.patch<Map<String, dynamic>>(
        '/volunteers/me',
        data: updateData,
      );
      if (response.data != null) {
        return VolunteerProfileModel.fromJson(response.data!);
      }
    } catch (_) {
      return null;
    }
    return null;
  }

  /// Register Cloudinary media upload
  Future<Map<String, dynamic>?> generateSignedUpload({
    required String assetType,
    required String fileFormat,
    String? folder,
  }) async {
    try {
      final response = await _apiClient.post<Map<String, dynamic>>(
        '/media/signed-upload',
        data: {
          'asset_type': assetType,
          'file_format': fileFormat,
          if (folder != null) 'folder': folder,
        },
      );
      return response.data;
    } catch (_) {
      return null;
    }
  }

  /// Register uploaded media asset in canonical database
  Future<bool> registerMediaAsset({
    required String publicId,
    required String secureUrl,
    required String assetType,
    required String fileFormat,
    required int bytes,
  }) async {
    try {
      await _apiClient.post<Map<String, dynamic>>(
        '/media/assets',
        data: {
          'public_id': publicId,
          'secure_url': secureUrl,
          'asset_type': assetType,
          'file_format': fileFormat,
          'bytes': bytes,
        },
      );
      return true;
    } catch (_) {
      return false;
    }
  }
}
