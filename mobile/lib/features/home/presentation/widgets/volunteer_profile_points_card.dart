import 'package:flutter/material.dart';
import '../../../../core/animations/fade_slide_in.dart';
import '../../../../core/animations/shimmer.dart';
import '../../../../core/models/gamification_summary_model.dart';
import '../../../../core/models/volunteer_profile_model.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/shadows.dart';
import '../../../../core/theme/spacing.dart';
import '../../../../core/widgets/layout/avatar.dart';

/// Section 3: Volunteer Profile Card with Category, Verification Status, and Real-time Points Balance.
/// Recreated to match the Maatram volunteer app design.
class VolunteerProfilePointsCard extends StatelessWidget {
  final VolunteerProfileModel? profile;
  final GamificationSummaryModel? gamification;
  final bool isLoading;
  final VoidCallback? onEditProfile;

  const VolunteerProfilePointsCard({
    super.key,
    this.profile,
    this.gamification,
    this.isLoading = false,
    this.onEditProfile,
  });

  @override
  Widget build(BuildContext context) {
    final name = profile?.shortName ?? 'Volunteer';
    final subtitle = profile?.subtitle; // null if profile not loaded
    // Points display: distinct states for loading, loaded, and unavailable.
    // - isLoading: show shimmer skeleton
    // - gamification != null: show real formatted points (may be '0' for genuine zero)
    // - gamification == null && !isLoading: show '—' (error / data unavailable)
    final String? pointsValue = isLoading
        ? null
        : gamification != null
            ? gamification!.formattedPoints
            : '—';

    return MaatramFadeSlideIn(
      direction: SlideDirection.fromBottom,
      delay: const Duration(milliseconds: 100),
      child: Container(
        margin: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.md,
          vertical: MaatramSpacing.xs,
        ),
        padding: const EdgeInsets.all(MaatramSpacing.md),
        decoration: BoxDecoration(
          color: MaatramColors.white,
          borderRadius: MaatramRadii.cardRadius,
          border: Border.all(color: MaatramColors.warmBorder),
          boxShadow: MaatramShadows.card,
        ),
        child: Row(
          children: [
            // 1. Volunteer Avatar with Edit Badge
            Stack(
              clipBehavior: Clip.none,
              children: [
                Container(
                  padding: const EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: const Color(0xFFFDE68A),
                      width: 2,
                    ),
                  ),
                  child: MaatramAvatar(
                    name: profile?.fullName.isNotEmpty == true
                        ? profile!.fullName
                        : 'Volunteer',
                    imageUrl: profile?.avatarUrl,
                    size: 48,
                  ),
                ),
                Positioned(
                  bottom: -2,
                  right: -2,
                  child: GestureDetector(
                    onTap: onEditProfile,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: MaatramColors.white,
                        shape: BoxShape.circle,
                        border: Border.all(color: MaatramColors.warmBorder),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x15000000),
                            blurRadius: 4,
                            offset: Offset(0, 1),
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.edit_outlined,
                        size: 11,
                        color: MaatramColors.deepNavy,
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(width: MaatramSpacing.md),

            // 2. Identity, Verification Badge & Subtitle
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Wrap(
                    crossAxisAlignment: WrapCrossAlignment.center,
                    spacing: 6,
                    runSpacing: 2,
                    children: [
                      Text(
                        name,
                        style: const TextStyle(
                          fontFamily: 'Georgia',
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: MaatramColors.deepNavy,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      // Approved Badge Pill
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 7, vertical: 2.5),
                        decoration: BoxDecoration(
                          color: MaatramColors.successLight,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                              color: MaatramColors.successBorder, width: 0.8),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.check_circle_rounded,
                              size: 11,
                              color: MaatramColors.successDark,
                            ),
                            SizedBox(width: 3),
                            Text(
                              'Approved',
                              style: TextStyle(
                                fontFamily: 'Roboto',
                                fontSize: 10,
                                fontWeight: FontWeight.w600,
                                color: MaatramColors.successDark,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  if (isLoading)
                    MaatramShimmer(
                      child: Container(
                        height: 12,
                        width: 140,
                        decoration: BoxDecoration(
                          color: MaatramColors.shimmerBase,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                    )
                  else if (subtitle != null)
                    Text(
                      subtitle,
                      style: const TextStyle(
                        fontFamily: 'Roboto',
                        fontSize: 12,
                        color: MaatramColors.secondaryText,
                        height: 1.25,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),
            const SizedBox(width: MaatramSpacing.sm),

            // 3. Subtle Vertical Divider
            Container(
              height: 38,
              width: 1,
              color: MaatramColors.warmBorder,
            ),
            const SizedBox(width: MaatramSpacing.md),

            // 4. Points Balance with Gold Star
            Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const Icon(
                  Icons.star_rounded,
                  color: MaatramColors.primaryGold,
                  size: 22,
                ),
                const SizedBox(height: 2),
                if (isLoading)
                  MaatramShimmer(
                    child: Container(
                      height: 22,
                      width: 48,
                      decoration: BoxDecoration(
                        color: MaatramColors.shimmerBase,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                  )
                else
                  Text(
                    pointsValue ?? '—',
                    style: const TextStyle(
                      fontFamily: 'Roboto',
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: MaatramColors.deepNavy,
                      letterSpacing: -0.5,
                    ),
                  ),
                const Text(
                  'Points',
                  style: TextStyle(
                    fontFamily: 'Roboto',
                    fontSize: 11,
                    color: MaatramColors.secondaryText,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
