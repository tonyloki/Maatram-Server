import 'package:flutter/widgets.dart';
import '../theme/colors.dart';
import 'motion_tokens.dart';

/// Shimmer gradient animation used for skeleton loading states.
class MaatramShimmer extends StatefulWidget {
  final Widget child;
  final Color baseColor;
  final Color highlightColor;
  final Duration duration;

  const MaatramShimmer({
    super.key,
    required this.child,
    this.baseColor = MaatramColors.shimmerBase,
    this.highlightColor = MaatramColors.shimmerHighlight,
    this.duration = const Duration(milliseconds: 1400),
  });

  @override
  State<MaatramShimmer> createState() => _MaatramShimmerState();
}

class _MaatramShimmerState extends State<MaatramShimmer>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (MaatramMotion.isReducedMotion(context)) {
      return widget.child;
    }

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return ShaderMask(
          blendMode: BlendMode.srcATop,
          shaderCallback: (bounds) {
            return LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                widget.baseColor,
                widget.highlightColor,
                widget.baseColor,
              ],
              stops: const [0.0, 0.5, 1.0],
              transform: _SlidingGradientTransform(slidePercent: _controller.value),
            ).createShader(bounds);
          },
          child: child,
        );
      },
      child: widget.child,
    );
  }
}

class _SlidingGradientTransform extends GradientTransform {
  final double slidePercent;

  const _SlidingGradientTransform({required this.slidePercent});

  @override
  Matrix4? transform(Rect bounds, {TextDirection? textDirection}) {
    return Matrix4.translationValues(bounds.width * (2 * slidePercent - 1), 0.0, 0.0);
  }
}

