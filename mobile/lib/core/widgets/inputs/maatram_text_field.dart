import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';

/// Clean branded text field with gold focus highlight, autofill support, and error handling.
class MaatramTextField extends StatefulWidget {
  final TextEditingController? controller;
  final String? initialValue;
  final String? label;
  final String? hint;
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
  final Iterable<String>? autofillHints;

  const MaatramTextField({
    super.key,
    this.controller,
    this.initialValue,
    this.label,
    this.hint,
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
    this.autofillHints,
  });

  @override
  State<MaatramTextField> createState() => _MaatramTextFieldState();
}

class _MaatramTextFieldState extends State<MaatramTextField> {
  TextEditingController? _internalController;

  TextEditingController get _effectiveController {
    if (widget.controller != null) {
      return widget.controller!;
    }
    _internalController ??=
        TextEditingController(text: widget.initialValue ?? '');
    return _internalController!;
  }

  @override
  void didUpdateWidget(MaatramTextField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.controller == null && oldWidget.controller == null) {
      if (widget.initialValue != null &&
          widget.initialValue != _internalController?.text &&
          widget.initialValue != oldWidget.initialValue) {
        _internalController?.text = widget.initialValue!;
      }
    }
  }

  @override
  void dispose() {
    _internalController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final effectiveHint = widget.hint ?? widget.hintText;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (widget.label != null) ...[
          Text(
            widget.label!,
            style: MaatramTypography.labelMedium
                .copyWith(color: MaatramColors.charcoal800),
          ),
          const SizedBox(height: MaatramSpacing.xs),
        ],
        TextField(
          controller: _effectiveController,
          focusNode: widget.focusNode,
          enabled: widget.enabled,
          obscureText: widget.obscureText,
          keyboardType: widget.keyboardType,
          textInputAction: widget.textInputAction,
          autofillHints: widget.autofillHints,
          onChanged: widget.onChanged,
          onSubmitted: widget.onSubmitted,
          maxLines: widget.maxLines,
          style: MaatramTypography.bodyMedium
              .copyWith(color: MaatramColors.charcoal900),
          decoration: InputDecoration(
            hintText: effectiveHint,
            prefixIcon: widget.prefixIcon,
            suffixIcon: widget.suffixIcon,
            errorText: widget.errorText,
            helperText: widget.helperText,
            filled: true,
            fillColor:
                widget.enabled ? MaatramColors.white : MaatramColors.stone100,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: MaatramSpacing.lg,
              vertical: MaatramSpacing.md,
            ),
            border: OutlineInputBorder(
              borderRadius: MaatramRadii.radiusLg,
              borderSide:
                  const BorderSide(color: MaatramColors.warmBorder, width: 1.0),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: MaatramRadii.radiusLg,
              borderSide:
                  const BorderSide(color: MaatramColors.warmBorder, width: 1.0),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: MaatramRadii.radiusLg,
              borderSide: const BorderSide(
                  color: MaatramColors.primaryGold, width: 1.8),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: MaatramRadii.radiusLg,
              borderSide:
                  const BorderSide(color: MaatramColors.error, width: 1.2),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: MaatramRadii.radiusLg,
              borderSide:
                  const BorderSide(color: MaatramColors.errorDark, width: 1.8),
            ),
          ),
        ),
      ],
    );
  }
}
