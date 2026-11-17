import 'package:flutter/material.dart';
import '../../animations/pressable.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';

enum MaatramButtonVariant { primary, secondary, outline, danger }

enum MaatramButtonSize { sm, md, lg }

/// Standard production button supporting brand variants, sizes, icons, and loading state.
class MaatramButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final MaatramButtonVariant variant;
  final MaatramButtonSize size;
  final Widget? leadingIcon;
  final Widget? trailingIcon;
  final bool isLoading;
  final bool isFullWidth;

  const MaatramButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = MaatramButtonVariant.primary,
    this.size = MaatramButtonSize.md,
    this.leadingIcon,
    this.trailingIcon,
    this.isLoading = false,
    this.isFullWidth = false,
  });

  @override
  Widget build(BuildContext context) {
    final isEnabled = onPressed != null && !isLoading;

    Color bg;
    Color fg;
    BorderSide border = BorderSide.none;

    switch (variant) {
      case MaatramButtonVariant.primary:
        bg = isEnabled ? MaatramColors.primaryGold : MaatramColors.stone200;
        fg = isEnabled ? MaatramColors.deepNavy : MaatramColors.charcoal400;
        break;
      case MaatramButtonVariant.secondary:
        bg = isEnabled ? MaatramColors.deepNavy : MaatramColors.stone200;
        fg = isEnabled ? MaatramColors.white : MaatramColors.charcoal400;
        break;
      case MaatramButtonVariant.outline:
        bg = Colors.transparent;
        fg = isEnabled ? MaatramColors.deepNavy : MaatramColors.charcoal400;
        border = BorderSide(
          color: isEnabled ? MaatramColors.warmBorder : MaatramColors.stone200,
          width: 1.5,
        );
        break;
      case MaatramButtonVariant.danger:
        bg = isEnabled ? MaatramColors.error : MaatramColors.stone200;
        fg = MaatramColors.white;
        break;
    }

    double height;
    EdgeInsets padding;
    TextStyle textStyle;

    switch (size) {
      case MaatramButtonSize.sm:
        height = 36;
        padding = const EdgeInsets.symmetric(horizontal: MaatramSpacing.md);
        textStyle = MaatramTypography.labelSmall;
        break;
      case MaatramButtonSize.md:
        height = 46;
        padding = const EdgeInsets.symmetric(horizontal: MaatramSpacing.xl);
        textStyle = MaatramTypography.labelMedium;
        break;
      case MaatramButtonSize.lg:
        height = 54;
        padding = const EdgeInsets.symmetric(horizontal: MaatramSpacing.xxl);
        textStyle = MaatramTypography.labelLarge;
        break;
    }

    Widget content = Row(
      mainAxisSize: isFullWidth ? MainAxisSize.max : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (isLoading) ...[
          SizedBox(
            width: size == MaatramButtonSize.sm ? 14 : 18,
            height: size == MaatramButtonSize.sm ? 14 : 18,
            child: CircularProgressIndicator(
              strokeWidth: 2.2,
              valueColor: AlwaysStoppedAnimation<Color>(fg),
            ),
          ),
          const SizedBox(width: MaatramSpacing.sm),
        ] else if (leadingIcon != null) ...[
          leadingIcon!,
          const SizedBox(width: MaatramSpacing.sm),
        ],
        Flexible(
          child: Text(
            label,
            style: textStyle.copyWith(color: fg),
            overflow: TextOverflow.ellipsis,
            maxLines: 1,
            textAlign: TextAlign.center,
          ),
        ),
        if (trailingIcon != null && !isLoading) ...[
          const SizedBox(width: MaatramSpacing.sm),
          trailingIcon!,
        ],
      ],
    );

    return MaatramPressable(
      onTap: isEnabled ? onPressed : null,
      enabled: isEnabled,
      child: Container(
        height: height,
        width: isFullWidth ? double.infinity : null,
        padding: padding,
        decoration: BoxDecoration(
          color: bg,
          borderRadius: MaatramRadii.buttonRadius,
          border:
              border == BorderSide.none ? null : Border.fromBorderSide(border),
        ),
        alignment: Alignment.center,
        child: content,
      ),
    );
  }
}
