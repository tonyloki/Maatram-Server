import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';

enum VolunteerCategory { student, alumni, corporate }

/// Pill badge identifying volunteer category (Student, Alumni, Corporate Panelist).
class MaatramCategoryBadge extends StatelessWidget {
  final VolunteerCategory category;
  final bool isCompact;

  const MaatramCategoryBadge({
    super.key,
    required this.category,
    this.isCompact = false,
  });

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    Color border;
    String label;
    IconData icon;

    switch (category) {
      case VolunteerCategory.student:
        bg = MaatramColors.categoryStudentBg;
        fg = MaatramColors.categoryStudent;
        border = MaatramColors.categoryStudentBorder;
        label = 'Student';
        icon = Icons.school_outlined;
        break;
      case VolunteerCategory.alumni:
        bg = MaatramColors.categoryAlumniBg;
        fg = MaatramColors.categoryAlumni;
        border = MaatramColors.categoryAlumniBorder;
        label = 'Alumni';
        icon = Icons.work_outline;
        break;
      case VolunteerCategory.corporate:
        bg = MaatramColors.categoryCorporateBg;
        fg = MaatramColors.categoryCorporate;
        border = MaatramColors.categoryCorporateBorder;
        label = 'Corporate';
        icon = Icons.business_outlined;
        break;
    }

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isCompact ? MaatramSpacing.sm : MaatramSpacing.md,
        vertical: isCompact ? 2 : MaatramSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: MaatramRadii.radiusPill,
        border: Border.all(color: border, width: 1.0),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: isCompact ? 11 : 13, color: fg),
          const SizedBox(width: MaatramSpacing.xs),
          Text(
            label,
            style: (isCompact
                    ? MaatramTypography.labelSmall
                    : MaatramTypography.labelMedium)
                .copyWith(color: fg),
          ),
        ],
      ),
    );
  }
}
