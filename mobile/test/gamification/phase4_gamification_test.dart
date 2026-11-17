import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/models/achievement_model.dart';
import 'package:maatram_mobile/core/models/gamification_summary_model.dart';
import 'package:maatram_mobile/core/models/point_ledger_model.dart';
import 'package:maatram_mobile/core/network/api_client.dart';
import 'package:maatram_mobile/features/gamification/data/gamification_repository.dart';
import 'package:maatram_mobile/features/gamification/presentation/achievement_details_modal.dart';
import 'package:maatram_mobile/features/gamification/presentation/achievements_screen.dart';
import 'package:maatram_mobile/features/gamification/presentation/points_history_screen.dart';
import 'package:maatram_mobile/features/gamification/presentation/points_overview_screen.dart';

class MockGamificationRepository extends GamificationRepository {
  MockGamificationRepository() : super(apiClient: ApiClient());

  @override
  Future<GamificationSummaryModel> getSummary() async {
    return const GamificationSummaryModel(
      volunteerProfileId: 'vol-123',
      cycleYear: 2026,
      totalPoints: 180.0,
      totalHours: 24.0,
      completedEventsCount: 5,
      badgesEarnedCount: 4,
      rank: 1,
      eventsThisYear: 5,
    );
  }

  @override
  Future<PointLedgerModel?> getLedger({int page = 1, int pageSize = 50}) async {
    return PointLedgerModel(
      items: [
        PointTransactionModel(
          id: 'tx-1',
          volunteerProfileId: 'vol-123',
          totalPoints: 18.0,
          transactionType: 'EVENT_COMPLETION',
          reason: 'Completed School Visit - Government High School',
          cycleYear: 2026,
          createdAt: DateTime(2026, 11, 26, 14, 30),
        ),
        PointTransactionModel(
          id: 'tx-2',
          volunteerProfileId: 'vol-123',
          totalPoints: 10.0,
          transactionType: 'EVENT_COMPLETION',
          reason: 'Completed Mock Interview Session',
          cycleYear: 2026,
          createdAt: DateTime(2026, 10, 20, 12, 0),
        ),
      ],
      total: 2,
      page: 1,
      pageSize: 20,
      totalPages: 1,
      netPoints: 28.0,
    );
  }

  @override
  Future<VolunteerAchievementsModel> getAchievements() async {
    return VolunteerAchievementsModel(
      items: [
        AchievementModel(
          id: 'ach-1',
          code: 'FIRST_STEP',
          title: 'First Step',
          description:
              'Completed your very first volunteering activity with Maatram.',
          iconUrl: '',
          category: 'GENERAL',
          criteriaType: 'EVENTS',
          criteriaThreshold: 1.0,
          isActive: true,
          isEarned: true,
          awardedAt: DateTime(2026, 9, 15),
        ),
        AchievementModel(
          id: 'ach-2',
          code: 'CENTURY_CLUB',
          title: '100 Club',
          description:
              'Accumulated over 100 verified Karma points across events.',
          iconUrl: '',
          category: 'POINTS',
          criteriaType: 'POINTS',
          criteriaThreshold: 100.0,
          isActive: true,
          isEarned: true,
          awardedAt: DateTime(2026, 11, 20),
        ),
        const AchievementModel(
          id: 'ach-3',
          code: 'MASTER_MENTOR',
          title: 'Master Mentor',
          description:
              'Conduct career guidance across 10 distinct institutions.',
          iconUrl: '',
          category: 'HOURS',
          criteriaType: 'HOURS',
          criteriaThreshold: 50.0,
          isActive: true,
          isEarned: false,
        ),
      ],
      totalEarned: 2,
      totalAvailable: 3,
    );
  }
}

void main() {
  final mockRepo = MockGamificationRepository();

  Widget buildTestableWidget(Widget child) {
    return ProviderScope(
      overrides: [
        gamificationRepositoryProvider.overrideWithValue(mockRepo),
      ],
      child: MaterialApp(
        home: child,
      ),
    );
  }

  group('Phase 4 Gamification Screens Tests', () {
    testWidgets(
        'PointsOverviewScreen displays hero score and calculation breakdown',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(
        buildTestableWidget(const PointsOverviewScreen()),
      );
      await tester.pumpAndSettle();

      expect(find.text('Points & Karma'), findsOneWidget);
      expect(find.text('180'), findsOneWidget);
      expect(find.text('Points Formula & Breakdown'), findsOneWidget);
      expect(find.text('Events Completed'), findsOneWidget);
      expect(find.text('Volunteering Hours'), findsOneWidget);
      expect(find.text('Transaction History (Ledger)'), findsOneWidget);
      expect(find.text('Achievements & Badges'), findsOneWidget);
    });

    testWidgets('PointsHistoryScreen displays audit log ledger transactions',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(
        buildTestableWidget(const PointsHistoryScreen()),
      );
      await tester.pumpAndSettle();

      expect(find.text('Points Ledger'), findsOneWidget);
      expect(find.text('Completed School Visit - Government High School'),
          findsOneWidget);
      expect(find.text('+18 pts'), findsOneWidget);
      expect(find.text('Completed Mock Interview Session'), findsOneWidget);
      expect(find.text('+10 pts'), findsOneWidget);
    });

    testWidgets('AchievementsScreen displays unlocked and locked badges',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      await tester.pumpWidget(
        buildTestableWidget(const AchievementsScreen()),
      );
      await tester.pumpAndSettle();

      expect(find.text('Achievements'), findsOneWidget);
      expect(find.text('First Step'), findsOneWidget);
      expect(find.text('100 Club'), findsOneWidget);
      expect(find.text('Master Mentor'), findsOneWidget);
      expect(find.text('Locked'), findsOneWidget);
    });

    testWidgets(
        'AchievementDetailsModal displays badge criteria and share option',
        (tester) async {
      tester.view.physicalSize = const Size(390 * 3, 844 * 3);
      tester.view.devicePixelRatio = 3.0;
      addTearDown(() => tester.view.resetPhysicalSize());

      final sampleBadge = AchievementModel(
        id: 'ach-2',
        code: 'CENTURY_CLUB',
        title: '100 Club',
        description:
            'Accumulated over 100 verified Karma points across events.',
        iconUrl: '',
        category: 'POINTS',
        criteriaType: 'POINTS',
        criteriaThreshold: 100.0,
        isActive: true,
        isEarned: true,
        awardedAt: DateTime(2026, 11, 20),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AchievementDetailsModal(
              achievement: sampleBadge,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('100 Club'), findsOneWidget);
      expect(
          find.text(
              'Accumulated over 100 verified Karma points across events.'),
          findsOneWidget);
      expect(find.text('Share Achievement'), findsOneWidget);
    });
  });
}
