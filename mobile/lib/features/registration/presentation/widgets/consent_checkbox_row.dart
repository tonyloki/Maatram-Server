import 'package:flutter/material.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/spacing.dart';
import '../../../../core/theme/typography.dart';

class ConsentCheckboxRow extends StatelessWidget {
  final String title;
  final String description;
  final bool value;
  final ValueChanged<bool?> onChanged;
  final bool isMandatory;

  const ConsentCheckboxRow({
    super.key,
    required this.title,
    required this.description,
    required this.value,
    required this.onChanged,
    this.isMandatory = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: MaatramSpacing.md),
      padding: const EdgeInsets.all(MaatramSpacing.md),
      decoration: BoxDecoration(
        color: MaatramColors.white,
        borderRadius: MaatramRadii.radiusLg,
        border: Border.all(
          color: value ? MaatramColors.primaryGold : MaatramColors.warmBorder,
          width: 1.0,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Checkbox(
            value: value,
            activeColor: MaatramColors.primaryGold,
            checkColor: MaatramColors.deepNavy,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
            onChanged: onChanged,
          ),
          const SizedBox(width: MaatramSpacing.xs),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Flexible(
                      child: Text(
                        title,
                        style: MaatramTypography.bodyMedium.copyWith(
                          color: MaatramColors.deepNavy,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    if (isMandatory) ...[
                      const SizedBox(width: 4),
                      const Text(
                        '*',
                        style: TextStyle(
                            color: Colors.red, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  description,
                  style: MaatramTypography.bodySmall.copyWith(
                    color: MaatramColors.secondaryText,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
