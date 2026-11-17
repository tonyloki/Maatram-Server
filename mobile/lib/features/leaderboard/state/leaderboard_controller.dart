import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/models/leaderboard_model.dart';
import '../data/leaderboard_repository.dart';

class LeaderboardState {
  final bool isLoading;
  final String? errorMessage;
  final String selectedCategory; // 'OVERALL', 'STUDENTS', 'ALUMNI'
  final List<LeaderboardItemModel> items;

  const LeaderboardState({
    this.isLoading = false,
    this.errorMessage,
    this.selectedCategory = 'OVERALL',
    this.items = const [],
  });

  LeaderboardState copyWith({
    bool? isLoading,
    String? errorMessage,
    String? selectedCategory,
    List<LeaderboardItemModel>? items,
  }) {
    return LeaderboardState(
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      selectedCategory: selectedCategory ?? this.selectedCategory,
      items: items ?? this.items,
    );
  }
}

final leaderboardControllerProvider =
    StateNotifierProvider<LeaderboardController, LeaderboardState>((ref) {
  final repo = ref.watch(leaderboardRepositoryProvider);
  return LeaderboardController(leaderboardRepository: repo);
});

class LeaderboardController extends StateNotifier<LeaderboardState> {
  final LeaderboardRepository _leaderboardRepository;

  LeaderboardController({
    required LeaderboardRepository leaderboardRepository,
    LeaderboardState? initialState,
    bool loadOnInit = true,
  })  : _leaderboardRepository = leaderboardRepository,
        super(initialState ?? const LeaderboardState(isLoading: false)) {
    if (loadOnInit) {
      loadLeaderboard('OVERALL');
    }
  }

  Future<void> changeCategory(String category) async {
    if (state.selectedCategory == category && state.items.isNotEmpty) return;
    state = state.copyWith(selectedCategory: category);
    await loadLeaderboard(category);
  }

  Future<void> loadLeaderboard(String category) async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final items =
          await _leaderboardRepository.getLeaderboard(category: category);
      state = state.copyWith(
        isLoading: false,
        items: items,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Could not load leaderboard data.',
      );
    }
  }

  Future<void> refresh() async {
    await loadLeaderboard(state.selectedCategory);
  }
}
