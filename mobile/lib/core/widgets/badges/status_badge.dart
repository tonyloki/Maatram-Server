import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';

enum MaatramStatus { pending, approved, live, completed, rejected, cancelled }

/// Visual status indicator for application and event lifecycles.
class MaatramStatusBadge extends StatelessWidget {
  final MaatramStatus status;
  final String? customLabel;

  const MaatramStatusBadge({
    super.key,
    required this.status,
    this.customLabel,
  });

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    Color border;
    String label;
    IconData? icon;

    switch (status) {
      case MaatramStatus.pending:
        bg = MaatramColors.warningLight;
        fg = MaatramColors.warningDark;
        border = MaatramColors.warningBorder;
        label = customLabel ?? 'Pending';
        icon = Icons.schedule;
        break;
      case MaatramStatus.approved:
        bg = MaatramColors.successLight;
        fg = MaatramColors.successDark;
        border = MaatramColors.successBorder;
        label = customLabel ?? 'Approved';
        icon = Icons.check_circle_outline;
        break;
      case MaatramStatus.live:
        bg = MaatramColors.goldSurface;
        fg = MaatramColors.goldDark;
        border = MaatramColors.primaryGold;
        label = customLabel ?? 'Live Now';
        icon = Icons.fiber_manual_record;
        break;
      case MaatramStatus.completed:
        bg = MaatramColors.stone100;
        fg = MaatramColors.charcoal700;
        border = MaatramColors.warmBorder;
        label = customLabel ?? 'Completed';
        icon = Icons.done_all;
        break;
      case MaatramStatus.rejected:
      case MaatramStatus.cancelled:
        bg = MaatramColors.errorLight;
        fg = MaatramColors.errorDark;
        border = MaatramColors.errorBorder;
        label = customLabel ??
            (status == MaatramStatus.rejected ? 'Rejected' : 'Cancelled');
        icon = Icons.cancel_outlined;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.sm, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: MaatramRadii.radiusPill,
        border: Border.all(color: border, width: 1.0),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 11, color: fg),
          const SizedBox(width: 4),
          Text(
            label,
            style: MaatramTypography.labelSmall.copyWith(color: fg),
          ),
        ],
      ),
    );
  }
}
