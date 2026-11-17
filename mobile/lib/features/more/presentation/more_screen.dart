import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/shadows.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/layout/avatar.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../../home/state/home_controller.dart';
import 'logout_confirmation_dialog.dart';

class MoreScreen extends ConsumerWidget {
  const MoreScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);
    final homeState = ref.watch(homeControllerProvider);
    final profile = homeState.profile.valueOrNull;

    final displayName = profile?.shortName ??
        (authState.session?.firstName != null &&
                authState.session!.firstName!.isNotEmpty
            ? authState.session!.firstName!
            : authState.session?.displayName ?? 'Volunteer');

    final displayCategory = profile?.categoryDisplay ?? 'Volunteer';
    final institution = profile?.organizationOrCollege ?? 'Maatram Community';
    final email = authState.session?.email ?? '—';

    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          bottom: false,
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(
              parent: BouncingScrollPhysics(),
            ),
            padding: const EdgeInsets.only(bottom: 32),
            children: [
              // Header Title: "More"
              Padding(
                padding: const EdgeInsets.fromLTRB(
                  MaatramSpacing.md,
                  MaatramSpacing.md,
                  MaatramSpacing.md,
                  MaatramSpacing.sm,
                ),
                child: Text(
                  'More',
                  style: MaatramTypography.headlineLarge.copyWith(
                    fontFamily: 'Georgia',
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                    color: MaatramColors.deepNavy,
                  ),
                ),
              ),

              // Profile Summary Card (Tappable -> ProfileScreen)
              Padding(
                padding:
                    const EdgeInsets.symmetric(horizontal: MaatramSpacing.md),
                child: InkWell(
                  onTap: () => context.push(RouteNames.profilePath),
                  borderRadius: BorderRadius.circular(24),
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: MaatramRadii.cardRadius,
                      border: Border.all(color: MaatramColors.warmBorder),
                      boxShadow: MaatramShadows.card,
                    ),
                    padding: const EdgeInsets.all(MaatramSpacing.md),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(2),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                                color: MaatramColors.primaryGold, width: 2),
                          ),
                          child: MaatramAvatar(
                            name: displayName,
                            imageUrl: profile?.avatarUrl,
                            size: 52,
                          ),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Flexible(
                                    child: Text(
                                      displayName,
                                      style: const TextStyle(
                                        fontFamily: 'Georgia',
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                        color: MaatramColors.deepNavy,
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                  const SizedBox(width: 6),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 6, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFECFDF5),
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: const Text(
                                      'Active',
                                      style: TextStyle(
                                        fontFamily: 'Roboto',
                                        fontSize: 9.5,
                                        fontWeight: FontWeight.bold,
                                        color: Color(0xFF047857),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 2),
                              Text(
                                '$displayCategory • $institution',
                                style: const TextStyle(
                                  fontFamily: 'Roboto',
                                  fontSize: 11.5,
                                  color: MaatramColors.secondaryText,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 2),
                              Text(
                                email,
                                style: const TextStyle(
                                  fontFamily: 'Roboto',
                                  fontSize: 11,
                                  color: MaatramColors.charcoal500,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                        const Icon(Icons.chevron_right_rounded,
                            color: MaatramColors.secondaryText),
                      ],
                    ),
                  ),
                ),
              ),

              const SizedBox(height: MaatramSpacing.md),

              // Menu Navigation List
              Padding(
                padding:
                    const EdgeInsets.symmetric(horizontal: MaatramSpacing.md),
                child: Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: MaatramRadii.cardRadius,
                    border: Border.all(color: MaatramColors.warmBorder),
                    boxShadow: MaatramShadows.card,
                  ),
                  child: Column(
                    children: [
                      _MoreMenuItem(
                        icon: Icons.assignment_outlined,
                        title: 'My Activities',
                        iconBgColor: const Color(0xFFFFFBEB),
                        iconColor: const Color(0xFFD97706),
                        onTap: () => context.push(RouteNames.activityPath),
                      ),
                      const _MenuDivider(),
                      _MoreMenuItem(
                        icon: Icons.person_outline_rounded,
                        title: 'My Profile',
                        iconBgColor: const Color(0xFFEFF6FF),
                        iconColor: const Color(0xFF2563EB),
                        onTap: () => context.push(RouteNames.profilePath),
                      ),
                      const _MenuDivider(),
                      _MoreMenuItem(
                        icon: Icons.notifications_none_rounded,
                        title: 'Notification Settings',
                        iconBgColor: const Color(0xFFEFF6FF),
                        iconColor: const Color(0xFF2563EB),
                        onTap: () =>
                            context.push(RouteNames.notificationSettingsPath),
                      ),
                      const _MenuDivider(),
                      _MoreMenuItem(
                        icon: Icons.privacy_tip_outlined,
                        title: 'Privacy & Consents',
                        iconBgColor: const Color(0xFFECFDF5),
                        iconColor: const Color(0xFF059669),
                        onTap: () => context.push(RouteNames.privacyPath),
                      ),
                      const _MenuDivider(),
                      _MoreMenuItem(
                        icon: Icons.help_outline_rounded,
                        title: 'Help & Support',
                        iconBgColor: const Color(0xFFF3F4F6),
                        iconColor: const Color(0xFF4B5563),
                        onTap: () => context.push(RouteNames.helpSupportPath),
                      ),
                      const _MenuDivider(),
                      _MoreMenuItem(
                        icon: Icons.info_outline_rounded,
                        title: 'About Maatram',
                        iconBgColor: const Color(0xFFFEF3C7),
                        iconColor: const Color(0xFFB45309),
                        onTap: () => context.push(RouteNames.aboutMaatramPath),
                      ),
                      const _MenuDivider(),
                      _MoreMenuItem(
                        icon: Icons.logout_rounded,
                        title: 'Sign Out',
                        iconBgColor: const Color(0xFFFEE2E2),
                        iconColor: const Color(0xFFDC2626),
                        textColor: const Color(0xFFDC2626),
                        onTap: () => showModalBottomSheet(
                          context: context,
                          backgroundColor: Colors.transparent,
                          builder: (_) => const LogoutConfirmationDialog(),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MoreMenuItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final Color iconBgColor;
  final Color iconColor;
  final Color? textColor;
  final VoidCallback onTap;

  const _MoreMenuItem({
    required this.icon,
    required this.title,
    required this.iconBgColor,
    required this.iconColor,
    this.textColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: iconBgColor,
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: iconColor, size: 18),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Text(
                title,
                style: TextStyle(
                  fontFamily: 'Roboto',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: textColor ?? MaatramColors.deepNavy,
                ),
              ),
            ),
            const Icon(Icons.chevron_right_rounded,
                size: 20, color: MaatramColors.secondaryText),
          ],
        ),
      ),
    );
  }
}

class _MenuDivider extends StatelessWidget {
  const _MenuDivider();

  @override
  Widget build(BuildContext context) {
    return const Divider(
        height: 1, thickness: 1, color: MaatramColors.warmBorder);
  }
}
