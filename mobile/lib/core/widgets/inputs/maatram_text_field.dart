import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';

/// Clean branded text field with gold focus highlight and error handling.
class MaatramTextField extends StatelessWidget {
  final TextEditingController? controller;
  final String? label;
  final String? hintText;
  final String? helperText;
  final String? errorText;
  final bool obscureText;
  final TextInputType keyboardType;
  final TextInputAction textInputAction;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final int maxLines;
  final bool enabled;
  final FocusNode? focusNode;

  const MaatramTextField({
    super.key,
    this.controller,
    this.label,
    this.hintText,
    this.helperText,
    this.errorText,
    this.obscureText = false,
    this.keyboardType = TextInputType.text,
    this.textInputAction = TextInputAction.next,
    this.onChanged,
    this.onSubmitted,
    this.prefixIcon,
    this.suffixIcon,
    this.maxLines = 1,
    this.enabled = true,
    this.focusNode,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (label != null) ...[
          Text(
            label!,
            style: MaatramTypography.labelMedium.copyWith(color: MaatramColors.charcoal800),
          ),
          const SizedBox(height: MaatramSpacing.xs),
        ],
        TextField(
          controller: controller,
          focusNode: focusNode,
          enabled: enabled,
          obscureText: obscureText,
          keyboardType: keyboardType,
          textInputAction: textInputAction,
          onChanged: onChanged,
          onSubmitted: onSubmitted,
          maxLines: maxLines,
          style: MaatramTypography.bodyMedium.copyWith(color: MaatramColors.charcoal900),
          decoration: InputDecoration(
            hintText: hintText,
            prefixIcon: prefixIcon,
            suffixIcon: suffixIcon,
            errorText: errorText,
            helperText: helperText,
            filled: true,
            fillColor: enabled ? MaatramColors.white : MaatramColors.stone100,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: MaatramSpacing.lg,
              vertical: MaatramSpacing.md,
            ),
            border: OutlineInputBorder(
              borderRadius: MaatramRadii.radiusLg,
              borderSide: const BorderSide(color: MaatramColors.warmBorder, width: 1.0),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: MaatramRadii.radiusLg,
              borderSide: const BorderSide(color: MaatramColors.warmBorder, width: 1.0),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: MaatramRadii.radiusLg,
              borderSide: const BorderSide(color: MaatramColors.primaryGold, width: 1.8),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: MaatramRadii.radiusLg,
              borderSide: const BorderSide(color: MaatramColors.error, width: 1.2),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: MaatramRadii.radiusLg,
              borderSide: const BorderSide(color: MaatramColors.errorDark, width: 1.8),
            ),
          ),
        ),
      ],
    );
  }
}

