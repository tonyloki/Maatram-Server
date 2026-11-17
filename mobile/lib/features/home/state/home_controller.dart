import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/models/event_model.dart';
import '../../../core/models/event_registration_model.dart';
import '../../../core/models/gamification_summary_model.dart';
import '../../../core/models/volunteer_profile_model.dart';
import '../data/home_repository.dart';

/// Provider for the HomeRepository
final homeRepositoryProvider = Provider<HomeRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return HomeRepository(apiClient: apiClient);
});

/// Immutable state container supporting independent section loading and error isolation
class HomeState {
  final AsyncValue<VolunteerProfileModel> profile;
  final AsyncValue<GamificationSummaryModel> gamification;
  final AsyncValue<List<EventModel>> events;
  final Map<String, EventRegistrationModel> registrations;
  final int unreadNotifications;
  final bool isRefreshing;

  const HomeState({
    required this.profile,
    required this.gamification,
    required this.events,
    this.registrations = const {},
    this.unreadNotifications = 0,
    this.isRefreshing = false,
  });

  bool get isLoadingInitial =>
      profile.isLoading && gamification.isLoading && events.isLoading;

  HomeState copyWith({
    AsyncValue<VolunteerProfileModel>? profile,
    AsyncValue<GamificationSummaryModel>? gamification,
    AsyncValue<List<EventModel>>? events,
    Map<String, EventRegistrationModel>? registrations,
    int? unreadNotifications,
    bool? isRefreshing,
  }) {
    return HomeState(
      profile: profile ?? this.profile,
      gamification: gamification ?? this.gamification,
      events: events ?? this.events,
      registrations: registrations ?? this.registrations,
      unreadNotifications: unreadNotifications ?? this.unreadNotifications,
      isRefreshing: isRefreshing ?? this.isRefreshing,
    );
  }
}

/// Controller orchestrating parallel and resilient data fetches for the volunteer Home Screen
class HomeController extends StateNotifier<HomeState> {
  final HomeRepository _repository;

  HomeController({required HomeRepository repository})
      : _repository = repository,
        super(const HomeState(
          profile: AsyncValue.loading(),
          gamification: AsyncValue.loading(),
          events: AsyncValue.loading(),
        )) {
    loadAll();
  }

  /// Initial load or full reload with concurrent requests and graceful individual fallbacks
  Future<void> loadAll() async {
    // 1. Kick off all fetch operations concurrently
    final profileFuture = _fetchProfile();
    final gamificationFuture = _fetchGamification();
    final eventsFuture = _fetchEvents();
    final notificationsFuture = _fetchNotifications();
    final registrationsFuture = _fetchRegistrations();

    await Future.wait([
      profileFuture,
      gamificationFuture,
      eventsFuture,
      notificationsFuture,
      registrationsFuture,
    ]);
  }

  /// Pull-to-refresh handler that keeps existing data visible while fetching latest
  Future<void> refresh() async {
    state = state.copyWith(isRefreshing: true);
    await loadAll();
    if (mounted) {
      state = state.copyWith(isRefreshing: false);
    }
  }

  /// Reload only profile
  Future<void> retryProfile() async {
    state = state.copyWith(profile: const AsyncValue.loading());
    await _fetchProfile();
  }

  /// Reload only gamification
  Future<void> retryGamification() async {
    state = state.copyWith(gamification: const AsyncValue.loading());
    await _fetchGamification();
  }

  /// Reload only upcoming events
  Future<void> retryEvents() async {
    state = state.copyWith(events: const AsyncValue.loading());
    await Future.wait([_fetchEvents(), _fetchRegistrations()]);
  }

  Future<void> _fetchProfile() async {
    try {
      final profile = await _repository.getProfile();
      if (mounted) {
        state = state.copyWith(profile: AsyncValue.data(profile));
      }
    } catch (e, st) {
      if (mounted) {
        state = state.copyWith(profile: AsyncValue.error(e, st));
      }
    }
  }

  Future<void> _fetchGamification() async {
    try {
      final summary = await _repository.getGamificationSummary();
      if (mounted) {
        state = state.copyWith(gamification: AsyncValue.data(summary));
      }
    } catch (e, st) {
      if (mounted) {
        state = state.copyWith(gamification: AsyncValue.error(e, st));
      }
    }
  }

  Future<void> _fetchEvents() async {
    try {
      final events = await _repository.getUpcomingEvents();
      if (mounted) {
        state = state.copyWith(events: AsyncValue.data(events));
      }
    } catch (e, st) {
      if (mounted) {
        state = state.copyWith(events: AsyncValue.error(e, st));
      }
    }
  }

  Future<void> _fetchRegistrations() async {
    try {
      final regs = await _repository.getRegistrations();
      if (mounted) {
        state = state.copyWith(registrations: regs);
      }
    } catch (_) {
      // Ignored non-critical failure
    }
  }

  Future<void> _fetchNotifications() async {
    try {
      final unread = await _repository.getUnreadNotificationCount();
      if (mounted) {
        state = state.copyWith(unreadNotifications: unread);
      }
    } catch (_) {
      // Non-critical fallback
    }
  }
}

/// Global provider for the HomeController and HomeState
final homeControllerProvider =
    StateNotifierProvider<HomeController, HomeState>((ref) {
  final repository = ref.watch(homeRepositoryProvider);
  return HomeController(repository: repository);
});
