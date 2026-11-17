import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/attendance_model.dart';
import '../../../core/models/event_model.dart';
import '../../../core/models/event_registration_model.dart';
import '../data/events_repository.dart';

class ActivityState {
  final bool isLoading;
  final String? errorMessage;
  final List<EventModel> upcomingEvents;
  final List<AttendanceModel> completedActivities;
  final List<EventRegistrationModel> cancelledRegistrations;
  final String selectedTab; // 'UPCOMING', 'COMPLETED', 'CANCELLED'

  const ActivityState({
    this.isLoading = false,
    this.errorMessage,
    this.upcomingEvents = const [],
    this.completedActivities = const [],
    this.cancelledRegistrations = const [],
    this.selectedTab = 'UPCOMING',
  });

  ActivityState copyWith({
    bool? isLoading,
    String? errorMessage,
    List<EventModel>? upcomingEvents,
    List<AttendanceModel>? completedActivities,
    List<EventRegistrationModel>? cancelledRegistrations,
    String? selectedTab,
  }) {
    return ActivityState(
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      upcomingEvents: upcomingEvents ?? this.upcomingEvents,
      completedActivities: completedActivities ?? this.completedActivities,
      cancelledRegistrations:
          cancelledRegistrations ?? this.cancelledRegistrations,
      selectedTab: selectedTab ?? this.selectedTab,
    );
  }
}

final activityControllerProvider =
    StateNotifierProvider<ActivityController, ActivityState>((ref) {
  final repo = ref.watch(eventsRepositoryProvider);
  return ActivityController(eventsRepository: repo);
});

class ActivityController extends StateNotifier<ActivityState> {
  final EventsRepository _eventsRepository;

  ActivityController({
    required EventsRepository eventsRepository,
    ActivityState? initialState,
    bool loadOnInit = true,
  })  : _eventsRepository = eventsRepository,
        super(initialState ?? const ActivityState(isLoading: false)) {
    if (loadOnInit) {
      loadData();
    }
  }

  void selectTab(String tab) {
    state = state.copyWith(selectedTab: tab);
  }

  Future<void> loadData() async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final results = await Future.wait([
        _eventsRepository.getEvents(limit: 20),
        _eventsRepository.getMyRegistrations(),
        _eventsRepository.getMyAttendance(),
      ]);

      final allEvents = results[0] as List<EventModel>;
      final registrations = results[1] as List<EventRegistrationModel>;
      final attendance = results[2] as List<AttendanceModel>;

      // Filter upcoming events that the user is registered for or published future events
      final now = DateTime.now();
      final upcoming = allEvents
          .where((e) =>
              e.startTime.isAfter(now.subtract(const Duration(hours: 4))))
          .toList();

      final cancelled = registrations
          .where((r) =>
              r.status.toUpperCase() == 'CANCELLED' ||
              r.status.toUpperCase() == 'WITHDRAWN')
          .toList();

      state = state.copyWith(
        isLoading: false,
        upcomingEvents: upcoming,
        completedActivities: attendance,
        cancelledRegistrations: cancelled,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Unable to load activity logs.',
      );
    }
  }

  Future<void> refresh() async {
    await loadData();
  }
}
