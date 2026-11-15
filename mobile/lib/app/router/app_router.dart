import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/widgets/navigation/bottom_nav_bar.dart';
import '../../features/dev_showcase/presentation/dev_showcase_screen.dart';
import '../../features/events/presentation/events_placeholder_screen.dart';
import '../../features/home/presentation/home_placeholder_screen.dart';
import '../../features/leaderboard/presentation/leaderboard_placeholder_screen.dart';
import '../../features/more/presentation/more_placeholder_screen.dart';
import 'route_names.dart';

final rootNavigatorKey = GlobalKey<NavigatorState>(debugLabel: 'rootNav');

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    navigatorKey: rootNavigatorKey,
    initialLocation: RouteNames.homePath,
    debugLogDiagnostics: false,
    routes: [
      // 4-Destination Persistent Navigation Shell using StatefulShellRoute
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return Scaffold(
            body: navigationShell,
            bottomNavigationBar: MaatramBottomNavBar(
              currentIndex: navigationShell.currentIndex,
              onDestinationSelected: (index) {
                navigationShell.goBranch(
                  index,
                  initialLocation: index == navigationShell.currentIndex,
                );
              },
            ),
          );
        },
        branches: [
          // 1. Home
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteNames.homePath,
                name: RouteNames.home,
                builder: (context, state) => const HomePlaceholderScreen(),
              ),
            ],
          ),
          // 2. Events
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteNames.eventsPath,
                name: RouteNames.events,
                builder: (context, state) => const EventsPlaceholderScreen(),
              ),
            ],
          ),
          // 3. Leaderboard
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteNames.leaderboardPath,
                name: RouteNames.leaderboard,
                builder: (context, state) => const LeaderboardPlaceholderScreen(),
              ),
            ],
          ),
          // 4. More
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: RouteNames.morePath,
                name: RouteNames.more,
                builder: (context, state) => const MorePlaceholderScreen(),
              ),
            ],
          ),
        ],
      ),

      // Developer Design Showcase Route (Section 11)
      GoRoute(
        path: RouteNames.devShowcasePath,
        name: RouteNames.devShowcase,
        parentNavigatorKey: rootNavigatorKey,
        builder: (context, state) => const DevShowcaseScreen(),
      ),
    ],
  );
});

