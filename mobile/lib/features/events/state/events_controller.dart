import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/event_model.dart';
import '../../../core/models/event_registration_model.dart';
import '../data/events_repository.dart';

class EventsState {
  final bool isLoading;
  final String? errorMessage;
  final String selectedCategory; // 'ALL', 'EDUCATION', 'MENTORING', 'CAREER'
  final String searchQuery;
  final List<EventModel> events;
  final Map<String, EventRegistrationModel> registrations;

  const EventsState({
    this.isLoading = false,
    this.errorMessage,
    this.selectedCategory = 'ALL',
    this.searchQuery = '',
    this.events = const [],
    this.registrations = const {},
  });

  EventsState copyWith({
    bool? isLoading,
    String? errorMessage,
    String? selectedCategory,
    String? searchQuery,
    List<EventModel>? events,
    Map<String, EventRegistrationModel>? registrations,
  }) {
    return EventsState(
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      selectedCategory: selectedCategory ?? this.selectedCategory,
      searchQuery: searchQuery ?? this.searchQuery,
      events: events ?? this.events,
      registrations: registrations ?? this.registrations,
    );
  }
}

final eventsControllerProvider =
    StateNotifierProvider<EventsController, EventsState>((ref) {
  final repo = ref.watch(eventsRepositoryProvider);
  return EventsController(eventsRepository: repo);
});

class EventsController extends StateNotifier<EventsState> {
  final EventsRepository _eventsRepository;

  EventsController({
    required EventsRepository eventsRepository,
    EventsState? initialState,
    bool loadOnInit = true,
  })  : _eventsRepository = eventsRepository,
        super(initialState ?? const EventsState(isLoading: false)) {
    if (loadOnInit) {
      loadEvents();
    }
  }

  void setCategory(String category) {
    if (state.selectedCategory == category) return;
    state = state.copyWith(selectedCategory: category);
    loadEvents();
  }

  void setSearchQuery(String query) {
    state = state.copyWith(searchQuery: query);
    loadEvents();
  }

  Future<void> loadEvents() async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final categoryFilter =
          state.selectedCategory == 'ALL' ? null : state.selectedCategory;
      final queryFilter =
          state.searchQuery.trim().isEmpty ? null : state.searchQuery.trim();

      final results = await Future.wait([
        _eventsRepository.getEvents(
          category: categoryFilter,
          search: queryFilter,
          limit: 30,
        ),
        _eventsRepository.getMyRegistrations(),
      ]);

      final eventsList = results[0] as List<EventModel>;
      final regList = results[1] as List<EventRegistrationModel>;
      final regMap = <String, EventRegistrationModel>{};
      for (final r in regList) {
        regMap[r.eventId] = r;
      }

      state = state.copyWith(
        isLoading: false,
        events: eventsList,
        registrations: regMap,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Unable to retrieve event opportunities.',
      );
    }
  }

  Future<bool> register(String eventId) async {
    final success = await _eventsRepository.registerForEvent(eventId);
    if (success) {
      await loadEvents();
    }
    return success;
  }

  Future<bool> withdraw(String registrationId) async {
    final success =
        await _eventsRepository.withdrawRegistration(registrationId);
    if (success) {
      await loadEvents();
    }
    return success;
  }

  Future<void> refresh() async {
    await loadEvents();
  }
}
