import 'package:flutter/widgets.dart';
import '../../animations/pressable.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/shadows.dart';
import '../../theme/spacing.dart';

/// Standard white surface card container with warm organic border and elevation.
class MaatramCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final VoidCallback? onTap;
  final Color backgroundColor;
  final Color borderColor;
  final BorderRadius? borderRadius;
  final List<BoxShadow>? shadows;
  final double? width;
  final double? height;

  const MaatramCard({
    super.key,
    required this.child,
    this.padding = MaatramSpacing.cardPadding,
    this.onTap,
    this.backgroundColor = MaatramColors.white,
    this.borderColor = MaatramColors.warmBorder,
    this.borderRadius,
    this.shadows = MaatramShadows.card,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveRadius = borderRadius ?? MaatramRadii.cardRadius;

    Widget cardContent = Container(
      width: width,
      height: height,
      padding: padding,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: effectiveRadius,
        border: Border.all(color: borderColor, width: 1.0),
        boxShadow: shadows,
      ),
      child: child,
    );

    if (onTap != null) {
      return MaatramPressable(
        onTap: onTap,
        child: cardContent,
      );
    }

    return cardContent;
  }
}

