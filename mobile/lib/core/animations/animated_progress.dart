import 'package:flutter/widgets.dart';
import '../theme/colors.dart';
import '../theme/radii.dart';
import 'motion_tokens.dart';

/// Smooth animated progress indicator for attendance and gamification tier tracking.
class MaatramAnimatedProgress extends StatelessWidget {
  final double progress; // 0.0 to 1.0
  final double height;
  final Color backgroundColor;
  final Color progressColor;
  final BorderRadius? borderRadius;
  final Duration duration;

  const MaatramAnimatedProgress({
    super.key,
    required this.progress,
    this.height = 8.0,
    this.backgroundColor = MaatramColors.warmBorder,
    this.progressColor = MaatramColors.primaryGold,
    this.borderRadius,
    this.duration = MaatramMotion.durationMedium,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveProgress = progress.clamp(0.0, 1.0);
    final effectiveRadius = borderRadius ?? MaatramRadii.radiusPill;

    if (MaatramMotion.isReducedMotion(context)) {
      return Container(
        height: height,
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: effectiveRadius,
        ),
        child: FractionallySizedBox(
          alignment: Alignment.centerLeft,
          widthFactor: effectiveProgress,
          child: Container(
            decoration: BoxDecoration(
              color: progressColor,
              borderRadius: effectiveRadius,
            ),
          ),
        ),
      );
    }

    return Container(
      height: height,
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: effectiveRadius,
      ),
      child: TweenAnimationBuilder<double>(
        tween: Tween<double>(begin: 0.0, end: effectiveProgress),
        duration: duration,
        curve: MaatramMotion.curveEntrance,
        builder: (context, value, _) {
          return FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: value,
            child: Container(
              decoration: BoxDecoration(
                color: progressColor,
                borderRadius: effectiveRadius,
              ),
            ),
          );
        },
      ),
    );
  }
}
