import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/route_names.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/spacing.dart';
import '../../../../core/widgets/layout/avatar.dart';

/// Top App Bar / Header component for the Volunteer Home Screen.
/// Displays official Maatram brand identity, interactive notification bell with unread badge,
/// and quick-access profile avatar.
class HomeHeader extends StatelessWidget {
  final int unreadCount;
  final String volunteerName;
  final String? avatarUrl;

  const HomeHeader({
    super.key,
    this.unreadCount = 0,
    required this.volunteerName,
    this.avatarUrl,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: MaatramSpacing.md,
        vertical: 10,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // 1. Maatram Brand Logo
          Image.asset(
            'assets/images/logo.png',
            height: 34,
            fit: BoxFit.contain,
            errorBuilder: (_, __, ___) => const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.wb_sunny_rounded,
                  color: MaatramColors.primaryGold,
                  size: 24,
                ),
                SizedBox(width: 6),
                Text(
                  'MAATRAM',
                  style: TextStyle(
                    fontFamily: 'Georgia',
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.2,
                    fontSize: 18,
                    color: MaatramColors.deepNavy,
                  ),
                ),
              ],
            ),
          ),

          // 2. Action Icons: Notification Bell & Profile Avatar
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Notification Bell with Badge
              Stack(
                clipBehavior: Clip.none,
                children: [
                  IconButton(
                    icon: const Icon(
                      Icons.notifications_none_rounded,
                      color: MaatramColors.deepNavy,
                      size: 26,
                    ),
                    splashRadius: 22,
                    tooltip: 'Notifications',
                    onPressed: () {
                      context.push(RouteNames.notificationsPath);
                    },
                  ),
                  if (unreadCount > 0)
                    Positioned(
                      top: 6,
                      right: 6,
                      child: Container(
                        padding: const EdgeInsets.all(3.5),
                        decoration: const BoxDecoration(
                          color: MaatramColors.errorDark,
                          shape: BoxShape.circle,
                        ),
                        constraints: const BoxConstraints(
                          minWidth: 16,
                          minHeight: 16,
                        ),
                        child: Text(
                          unreadCount > 9 ? '9+' : '$unreadCount',
                          style: const TextStyle(
                            fontFamily: 'Roboto',
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            height: 1.0,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                ],
              ),
              const SizedBox(width: 6),

              // Profile Avatar (Tap to go to More / Profile)
              GestureDetector(
                onTap: () {
                  context.push(RouteNames.profilePath);
                },
                child: Container(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: MaatramColors.warmBorder,
                      width: 1.5,
                    ),
                  ),
                  child: MaatramAvatar(
                    name: volunteerName.isNotEmpty ? volunteerName : 'Volunteer',
                    imageUrl: avatarUrl,
                    size: 36,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
