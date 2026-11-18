import 'package:flutter/material.dart';
import '../../animations/motion_tokens.dart';
import '../../animations/pressable.dart';
import '../../theme/colors.dart';
import '../../theme/shadows.dart';
import '../../theme/spacing.dart';

class MaatramNavItem {
  final String label;
  final IconData selectedIcon;
  final IconData unselectedIcon;
  final String routePath;

  const MaatramNavItem({
    required this.label,
    required this.selectedIcon,
    required this.unselectedIcon,
    required this.routePath,
  });
}

/// Floating bottom navigation bar with gold capsule around the active icon
/// and Roboto typography matching the approved design reference.
class MaatramBottomNavBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onDestinationSelected;

  static const List<MaatramNavItem> destinations = [
    MaatramNavItem(
      label: 'Home',
      selectedIcon: Icons.home_rounded,
      unselectedIcon: Icons.home_outlined,
      routePath: '/home',
    ),
    MaatramNavItem(
      label: 'Events',
      selectedIcon: Icons.calendar_month_rounded,
      unselectedIcon: Icons.calendar_month_outlined,
      routePath: '/events',
    ),
    MaatramNavItem(
      label: 'Leaderboard',
      selectedIcon: Icons.emoji_events_rounded,
      unselectedIcon: Icons.emoji_events_outlined,
      routePath: '/leaderboard',
    ),
    MaatramNavItem(
      label: 'More',
      selectedIcon: Icons.grid_view_rounded,
      unselectedIcon: Icons.grid_view_outlined,
      routePath: '/more',
    ),
  ];

  const MaatramBottomNavBar({
    super.key,
    required this.currentIndex,
    required this.onDestinationSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: MaatramColors.white,
        border: Border(
          top: BorderSide(color: MaatramColors.warmBorder, width: 1.0),
        ),
        boxShadow: MaatramShadows.elevated,
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: MaatramSpacing.sm,
            vertical: 6,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: List.generate(destinations.length, (index) {
              final item = destinations[index];
              final isSelected = index == currentIndex;

              return Expanded(
                child: MaatramPressable(
                  onTap: () => onDestinationSelected(index),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Active gold capsule around icon
                      AnimatedContainer(
                        duration: MaatramMotion.durationNormal,
                        curve: MaatramMotion.curveStandard,
                        width: 54,
                        height: 30,
                        decoration: BoxDecoration(
                          color: isSelected
                              ? MaatramColors.primaryGold
                              : Colors.transparent,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Center(
                          child: Icon(
                            isSelected
                                ? item.selectedIcon
                                : item.unselectedIcon,
                            size: 20,
                            color: isSelected
                                ? MaatramColors.deepNavy
                                : MaatramColors.secondaryText,
                          ),
                        ),
                      ),
                      const SizedBox(height: 3),
                      // Label in Roboto
                      Text(
                        item.label,
                        style: TextStyle(
                          fontFamily: 'Roboto',
                          fontSize: 11,
                          fontWeight:
                              isSelected ? FontWeight.w700 : FontWeight.w500,
                          color: isSelected
                              ? MaatramColors.deepNavy
                              : MaatramColors.secondaryText,
                          height: 1.2,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }),
          ),
        ),
      ),
    );
  }
}

/// Alias for component-level naming
typedef VolunteerBottomNavigation = MaatramBottomNavBar;
