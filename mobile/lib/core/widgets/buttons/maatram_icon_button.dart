import 'package:flutter/material.dart';
import '../../animations/pressable.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';

/// Circular or rounded icon button with warm border and tactile feedback.
class MaatramIconButton extends StatelessWidget {
  final Widget icon;
  final VoidCallback? onPressed;
  final double size;
  final Color? backgroundColor;
  final Color? borderColor;
  final String? tooltip;

  const MaatramIconButton({
    super.key,
    required this.icon,
    this.onPressed,
    this.size = 42.0,
    this.backgroundColor,
    this.borderColor,
    this.tooltip,
  });

  @override
  Widget build(BuildContext context) {
    final isEnabled = onPressed != null;

    Widget button = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: backgroundColor ?? MaatramColors.white,
        borderRadius: MaatramRadii.radiusLg,
        border: Border.all(
          color: borderColor ?? MaatramColors.warmBorder,
          width: 1.0,
        ),
      ),
      alignment: Alignment.center,
      child: icon,
    );

    if (tooltip != null) {
      button = Tooltip(message: tooltip!, child: button);
    }

    return MaatramPressable(
      onTap: isEnabled ? onPressed : null,
      enabled: isEnabled,
      child: button,
    );
  }
}
