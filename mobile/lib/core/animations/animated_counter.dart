import 'package:flutter/widgets.dart';
import '../theme/typography.dart';
import 'motion_tokens.dart';

/// Smooth rolling counter for metrics, gamification points, and leaderboards.
class MaatramAnimatedCounter extends StatelessWidget {
  final num value;
  final TextStyle? style;
  final String? prefix;
  final String? suffix;
  final Duration duration;
  final Curve curve;
  final int decimalPlaces;

  const MaatramAnimatedCounter({
    super.key,
    required this.value,
    this.style,
    this.prefix,
    this.suffix,
    this.duration = MaatramMotion.durationSlow,
    this.curve = MaatramMotion.curveEntrance,
    this.decimalPlaces = 0,
  });

  @override
  Widget build(BuildContext context) {
    if (MaatramMotion.isReducedMotion(context)) {
      final formatted = decimalPlaces > 0
          ? value.toStringAsFixed(decimalPlaces)
          : value.toInt().toString();
      return Text(
        '${prefix ?? ''}$formatted${suffix ?? ''}',
        style: style ?? MaatramTypography.statNumberLarge,
      );
    }

    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0, end: value.toDouble()),
      duration: duration,
      curve: curve,
      builder: (context, animatedVal, _) {
        final formatted = decimalPlaces > 0
            ? animatedVal.toStringAsFixed(decimalPlaces)
            : animatedVal.toInt().toString();
        return Text(
          '${prefix ?? ''}$formatted${suffix ?? ''}',
          style: style ?? MaatramTypography.statNumberLarge,
        );
      },
    );
  }
}

