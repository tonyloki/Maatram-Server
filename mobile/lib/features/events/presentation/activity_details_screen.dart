import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/models/attendance_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/badges/status_badge.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/layout/organic_background.dart';

class ActivityDetailsScreen extends StatelessWidget {
  final String activityId;
  final AttendanceModel? attendance;

  const ActivityDetailsScreen({
    super.key,
    required this.activityId,
    this.attendance,
  });

  @override
  Widget build(BuildContext context) {
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
            'Activity Details',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
        ),
        body: ListView(
          padding: const EdgeInsets.all(MaatramSpacing.md),
          children: [
            // Status and Header Card
            Container(
              padding: const EdgeInsets.all(MaatramSpacing.lg),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const MaatramStatusBadge(status: MaatramStatus.completed),
                      const SizedBox(width: 8),
                      Flexible(
                        child: Text(
                          attendance?.formattedDate ?? '—',
                          style: MaatramTypography.bodySmall.copyWith(
                            color: MaatramColors.secondaryText,
                            fontWeight: FontWeight.w600,
                          ),
                          textAlign: TextAlign.end,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    attendance?.eventTitle ?? 'Event Attendance',
                    style: MaatramTypography.headlineSmall.copyWith(
                      fontFamily: 'Georgia',
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Divider(color: MaatramColors.warmBorder),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _buildMetric(
                          label: 'Hours Credited',
                          value: attendance != null
                              ? '${attendance!.hoursCredited.toStringAsFixed(1)} hrs'
                              : '—',
                          icon: Icons.access_time_rounded,
                          accentColor: MaatramColors.categoryStudent,
                        ),
                      ),
                      Container(
                          width: 1,
                          height: 40,
                          color: MaatramColors.warmBorder),
                      Expanded(
                        child: _buildMetric(
                          label: 'Points Earned',
                          value: attendance != null
                              ? '+${((attendance!.hoursCredited * 2) + 10).toInt()} pts'
                              : '—',
                          icon: Icons.stars_rounded,
                          accentColor: MaatramColors.primaryGold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.md),

            // Attendance Log Card
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
                    'Attendance Log',
                    style: MaatramTypography.titleSmall.copyWith(
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      const Icon(Icons.login_rounded,
                          size: 20, color: MaatramColors.success),
                      const SizedBox(width: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Check-in',
                              style: MaatramTypography.labelSmall.copyWith(
                                  color: MaatramColors.secondaryText)),
                          Text(
                              attendance?.formattedTimeRange
                                      .split('–')
                                      .first
                                      .trim() ??
                                  '—',
                              style: MaatramTypography.bodySmall.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: MaatramColors.deepNavy)),
                        ],
                      ),
                    ],
                  ),
                  const Padding(
                    padding: EdgeInsets.only(left: 10),
                    child: SizedBox(
                        height: 16,
                        child: VerticalDivider(
                            color: MaatramColors.warmBorder, thickness: 1)),
                  ),
                  Row(
                    children: [
                      const Icon(Icons.logout_rounded,
                          size: 20, color: MaatramColors.primaryGold),
                      const SizedBox(width: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Check-out',
                              style: MaatramTypography.labelSmall.copyWith(
                                  color: MaatramColors.secondaryText)),
                          Text(
                              attendance?.formattedTimeRange
                                      .split('–')
                                      .last
                                      .trim() ??
                                  '—',
                              style: MaatramTypography.bodySmall.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: MaatramColors.deepNavy)),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.md),

            // Certificate Status Card (Governance Compliant)
            Container(
              padding: const EdgeInsets.all(MaatramSpacing.md),
              decoration: BoxDecoration(
                color: const Color(0xFFF9FAFB),
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.workspace_premium_outlined,
                          color: MaatramColors.secondaryText, size: 22),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Participation Certificate',
                          style: MaatramTypography.titleSmall.copyWith(
                            fontWeight: FontWeight.bold,
                            color: MaatramColors.deepNavy,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Official digital certificates are issued directly by the Maatram Foundation administrative team following complete batch verification. This feature is currently unavailable until official certificate issuance policy is finalized.',
                    style: MaatramTypography.bodySmall.copyWith(
                      color: MaatramColors.secondaryText,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: MaatramColors.warmBorder,
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.lock_outline_rounded,
                            size: 14, color: MaatramColors.secondaryText),
                        const SizedBox(width: 6),
                        Flexible(
                          child: Text(
                            'Certificate Unavailable (Pending Official Policy)',
                            style: MaatramTypography.labelSmall.copyWith(
                              color: MaatramColors.secondaryText,
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.xl),

            MaatramButton(
              label: 'Back to Activity',
              onPressed: () => context.pop(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetric({
    required String label,
    required String value,
    required IconData icon,
    required Color accentColor,
  }) {
    return Column(
      children: [
        Icon(icon, color: accentColor, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: MaatramTypography.titleMedium.copyWith(
            fontWeight: FontWeight.bold,
            color: MaatramColors.deepNavy,
          ),
        ),
        Text(
          label,
          style: MaatramTypography.labelSmall.copyWith(
            color: MaatramColors.secondaryText,
          ),
        ),
      ],
    );
  }
}
