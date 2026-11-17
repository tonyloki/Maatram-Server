import 'package:flutter/widgets.dart';
import 'motion_tokens.dart';

enum SlideDirection { fromBottom, fromTop, fromLeft, fromRight }

/// Reusable entrance animation providing subtle coordinated opacity and position translation.
class MaatramFadeSlideIn extends StatefulWidget {
  final Widget child;
  final Duration? duration;
  final Duration delay;
  final SlideDirection direction;
  final double distance;
  final Curve curve;

  const MaatramFadeSlideIn({
    super.key,
    required this.child,
    this.duration,
    this.delay = Duration.zero,
    this.direction = SlideDirection.fromBottom,
    this.distance = 16.0,
    this.curve = MaatramMotion.curveEntrance,
  });

  @override
  State<MaatramFadeSlideIn> createState() => _MaatramFadeSlideInState();
}

class _MaatramFadeSlideInState extends State<MaatramFadeSlideIn>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _fadeAnimation;
  late final Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    final animDuration = widget.duration ?? MaatramMotion.durationMedium;

    _controller = AnimationController(
      vsync: this,
      duration: animDuration,
    );

    _fadeAnimation = CurvedAnimation(
      parent: _controller,
      curve: widget.curve,
    );

    final startOffset = _calculateOffset(widget.direction, widget.distance);
    _slideAnimation = Tween<Offset>(
      begin: startOffset,
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: widget.curve,
    ));

    if (widget.delay == Duration.zero) {
      _controller.forward();
    } else {
      Future.delayed(widget.delay, () {
        if (mounted) {
          _controller.forward();
        }
      });
    }
  }

  Offset _calculateOffset(SlideDirection direction, double distance) {
    switch (direction) {
      case SlideDirection.fromBottom:
        return Offset(0, distance / 100);
      case SlideDirection.fromTop:
        return Offset(0, -distance / 100);
      case SlideDirection.fromLeft:
        return Offset(-distance / 100, 0);
      case SlideDirection.fromRight:
        return Offset(distance / 100, 0);
    }
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

    return FadeTransition(
      opacity: _fadeAnimation,
      child: SlideTransition(
        position: _slideAnimation,
        child: widget.child,
      ),
    );
  }
}
