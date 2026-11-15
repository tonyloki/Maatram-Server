import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:maatram_mobile/core/theme/colors.dart';
import 'package:maatram_mobile/core/widgets/badges/category_badge.dart';
import 'package:maatram_mobile/core/widgets/badges/points_badge.dart';
import 'package:maatram_mobile/core/widgets/badges/status_badge.dart';
import 'package:maatram_mobile/core/widgets/buttons/maatram_button.dart';
import 'package:maatram_mobile/core/widgets/buttons/maatram_icon_button.dart';
import 'package:maatram_mobile/core/widgets/cards/maatram_card.dart';
import 'package:maatram_mobile/core/widgets/cards/maatram_stat_card.dart';
import 'package:maatram_mobile/core/widgets/inputs/maatram_search_field.dart';
import 'package:maatram_mobile/core/widgets/inputs/maatram_text_field.dart';
import 'package:maatram_mobile/core/widgets/navigation/bottom_nav_bar.dart';

void main() {
  group('Core Component Library Tests', () {
    testWidgets('MaatramButton renders primary, responds to tap and shows loading', (tester) async {
      var pressed = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MaatramButton(
              label: 'Submit Application',
              onPressed: () => pressed = true,
            ),
          ),
        ),
      );

      expect(find.text('Submit Application'), findsOneWidget);
      await tester.tap(find.text('Submit Application'));
      expect(pressed, isTrue);

      // Loading state
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: MaatramButton(
              label: 'Submit Application',
              isLoading: true,
            ),
          ),
        ),
      );
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('MaatramIconButton renders and triggers onPressed', (tester) async {
      var iconTapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MaatramIconButton(
              icon: const Icon(Icons.notifications_outlined),
              onPressed: () => iconTapped = true,
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.notifications_outlined), findsOneWidget);
      await tester.tap(find.byIcon(Icons.notifications_outlined));
      expect(iconTapped, isTrue);
    });

    testWidgets('MaatramTextField renders label, hint, and accepts input', (tester) async {
      final controller = TextEditingController();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MaatramTextField(
              controller: controller,
              label: 'Full Name',
              hintText: 'Enter your legal name',
            ),
          ),
        ),
      );

      expect(find.text('Full Name'), findsOneWidget);
      expect(find.text('Enter your legal name'), findsOneWidget);

      await tester.enterText(find.byType(TextField), 'Ananya Krishnan');
      expect(controller.text, 'Ananya Krishnan');
    });

    testWidgets('MaatramSearchField renders and clears search query', (tester) async {
      final controller = TextEditingController(text: 'Teaching');
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MaatramSearchField(
              controller: controller,
              hintText: 'Search events...',
            ),
          ),
        ),
      );

      expect(find.text('Teaching'), findsOneWidget);
      expect(find.byIcon(Icons.close), findsOneWidget);

      await tester.tap(find.byIcon(Icons.close));
      await tester.pump();
      expect(controller.text, '');
    });

    testWidgets('MaatramCard renders child inside bordered container', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: MaatramCard(
              child: Text('Card Content'),
            ),
          ),
        ),
      );

      expect(find.text('Card Content'), findsOneWidget);
    });

    testWidgets('MaatramStatCard renders icon, count, and label', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: MaatramStatCard(
              icon: Icons.star_rounded,
              iconColor: MaatramColors.primaryGold,
              value: 1250,
              label: 'Volunteer Points',
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();
      expect(find.text('1250'), findsOneWidget);
      expect(find.text('Volunteer Points'), findsOneWidget);
    });

    testWidgets('MaatramCategoryBadge, MaatramStatusBadge, MaatramPointsBadge render properly', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: Column(
              children: [
                MaatramCategoryBadge(category: VolunteerCategory.student),
                MaatramStatusBadge(status: MaatramStatus.approved),
                MaatramPointsBadge(points: 150),
              ],
            ),
          ),
        ),
      );

      expect(find.text('Student'), findsOneWidget);
      expect(find.text('Approved'), findsOneWidget);
      expect(find.text('+150 pts'), findsOneWidget);
    });

    testWidgets('MaatramBottomNavBar renders 4 navigation destinations', (tester) async {
      var selectedIndex = 0;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            bottomNavigationBar: MaatramBottomNavBar(
              currentIndex: selectedIndex,
              onDestinationSelected: (index) => selectedIndex = index,
            ),
          ),
        ),
      );

      expect(find.text('Home'), findsOneWidget);
      expect(find.text('Events'), findsOneWidget);
      expect(find.text('Leaderboard'), findsOneWidget);
      expect(find.text('More'), findsOneWidget);

      await tester.tap(find.text('Events'));
      expect(selectedIndex, 1);
    });
  });
}
