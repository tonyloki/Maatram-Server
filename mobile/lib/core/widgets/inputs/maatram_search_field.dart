import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';

/// Pill search input with clear action and subtle styling.
class MaatramSearchField extends StatelessWidget {
  final TextEditingController? controller;
  final String hintText;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final VoidCallback? onClear;

  const MaatramSearchField({
    super.key,
    this.controller,
    this.hintText = 'Search events, topics, or locations...',
    this.onChanged,
    this.onSubmitted,
    this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: MaatramColors.white,
        borderRadius: MaatramRadii.radiusPill,
        border: Border.all(color: MaatramColors.warmBorder, width: 1.0),
      ),
      child: TextField(
        controller: controller,
        onChanged: onChanged,
        onSubmitted: onSubmitted,
        style: MaatramTypography.bodyMedium,
        decoration: InputDecoration(
          hintText: hintText,
          hintStyle: MaatramTypography.bodySmall
              .copyWith(color: MaatramColors.secondaryText),
          prefixIcon: const Icon(Icons.search,
              size: 20, color: MaatramColors.charcoal600),
          suffixIcon: controller?.text.isNotEmpty == true
              ? IconButton(
                  icon: const Icon(Icons.close,
                      size: 18, color: MaatramColors.charcoal600),
                  onPressed: () {
                    controller?.clear();
                    onClear?.call();
                    onChanged?.call('');
                  },
                )
              : null,
          border: InputBorder.none,
          enabledBorder: InputBorder.none,
          focusedBorder: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: MaatramSpacing.lg,
            vertical: MaatramSpacing.md,
          ),
        ),
      ),
    );
  }
}
