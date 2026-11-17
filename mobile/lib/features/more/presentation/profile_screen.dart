import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/badges/category_badge.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/layout/avatar.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../../home/state/home_controller.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  VolunteerCategory _parseCategory(String? cat) {
    final lower = (cat ?? '').toLowerCase();
    if (lower.contains('alumni')) return VolunteerCategory.alumni;
    if (lower.contains('corporate')) return VolunteerCategory.corporate;
    return VolunteerCategory.student;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);
    final homeState = ref.watch(homeControllerProvider);
    final profile = homeState.profile.valueOrNull;
    final summary = homeState.gamification.valueOrNull;

    final displayName = profile?.fullName ??
        (authState.session?.firstName != null &&
                authState.session!.firstName!.isNotEmpty
            ? '${authState.session!.firstName!} ${authState.session!.lastName ?? ''}'
                .trim()
            : authState.session?.email.split('@').first ?? 'Volunteer');

    final institution = profile?.organizationOrCollege ?? '—';
    final email = authState.session?.email ?? '—';
    final mobileNumber = profile?.mobileNumber ?? '—';

    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_rounded,
                color: MaatramColors.deepNavy),
            onPressed: () => context.pop(),
          ),
          title: Text(
            'Volunteer Profile',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.edit_outlined,
                  color: MaatramColors.deepNavy),
              onPressed: () => context.push(RouteNames.editProfilePath),
            ),
          ],
        ),
        body: ListView(
          padding: const EdgeInsets.all(MaatramSpacing.md),
          children: [
            // Avatar and summary card
            Container(
              padding: const EdgeInsets.all(MaatramSpacing.lg),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
              ),
              child: Column(
                children: [
                  Stack(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(3),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(
                              color: MaatramColors.primaryGold, width: 2.5),
                        ),
                        child: MaatramAvatar(
                          name: displayName,
                          imageUrl: profile?.avatarUrl,
                          size: 72,
                        ),
                      ),
                      Positioned(
                        bottom: 0,
                        right: 0,
                        child: InkWell(
                          onTap: () =>
                              context.push(RouteNames.profilePhotoPath),
                          child: Container(
                            padding: const EdgeInsets.all(6),
                            decoration: const BoxDecoration(
                              color: MaatramColors.primaryGold,
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(Icons.camera_alt_rounded,
                                size: 14, color: MaatramColors.deepNavy),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    displayName,
                    style: const TextStyle(
                      fontFamily: 'Georgia',
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                  const SizedBox(height: 6),
                  MaatramCategoryBadge(
                      category: _parseCategory(profile?.category)),
                  const SizedBox(height: 16),
                  const Divider(color: MaatramColors.warmBorder),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      Expanded(
                        child: _buildQuickStat(
                          context,
                          label: 'Karma Points',
                          value:
                              summary != null ? summary.formattedPoints : '—',
                          onTap: () =>
                              context.push(RouteNames.pointsOverviewPath),
                        ),
                      ),
                      Container(
                          width: 1,
                          height: 32,
                          color: MaatramColors.warmBorder),
                      Expanded(
                        child: _buildQuickStat(
                          context,
                          label: 'Total Hours',
                          value: summary != null ? summary.formattedHours : '—',
                          onTap: () =>
                              context.push(RouteNames.pointsOverviewPath),
                        ),
                      ),
                      Container(
                          width: 1,
                          height: 32,
                          color: MaatramColors.warmBorder),
                      Expanded(
                        child: _buildQuickStat(
                          context,
                          label: 'Leaderboard',
                          value: summary != null && summary.rank != null
                              ? '#${summary.rank}'
                              : '—',
                          onTap: () => context.go(RouteNames.leaderboardPath),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.md),

            // Profile info details
            Container(
              padding: const EdgeInsets.all(MaatramSpacing.md),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Contact & Organization',
                    style: MaatramTypography.titleSmall.copyWith(
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                  const SizedBox(height: 14),
                  _buildField(
                      'Full Name', displayName, Icons.person_outline_rounded),
                  const Divider(height: 20, color: MaatramColors.warmBorder),
                  _buildField('Email Address', email, Icons.email_outlined),
                  const Divider(height: 20, color: MaatramColors.warmBorder),
                  _buildField(
                      'Mobile Number', mobileNumber, Icons.phone_outlined),
                  const Divider(height: 20, color: MaatramColors.warmBorder),
                  _buildField('Institution / Organization', institution,
                      Icons.school_outlined),
                  const Divider(height: 20, color: MaatramColors.warmBorder),
                  _buildField('Account Status', 'Active & Approved',
                      Icons.verified_rounded,
                      valueColor: MaatramColors.success),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.lg),

            MaatramButton(
              label: 'Edit Profile Information',
              onPressed: () => context.push(RouteNames.editProfilePath),
            ),
            const SizedBox(height: MaatramSpacing.md),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickStat(BuildContext context,
      {required String label,
      required String value,
      required VoidCallback onTap}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        child: Column(
          children: [
            Text(
              value,
              style: MaatramTypography.titleMedium.copyWith(
                fontWeight: FontWeight.bold,
                color: MaatramColors.deepNavy,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: MaatramTypography.labelSmall.copyWith(
                color: MaatramColors.secondaryText,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildField(String label, String value, IconData icon,
      {Color? valueColor}) {
    return Row(
      children: [
        Icon(icon, size: 20, color: MaatramColors.secondaryText),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontFamily: 'Roboto',
                  fontSize: 11.5,
                  color: MaatramColors.secondaryText,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: TextStyle(
                  fontFamily: 'Roboto',
                  fontSize: 13.5,
                  fontWeight: FontWeight.w600,
                  color: valueColor ?? MaatramColors.deepNavy,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
