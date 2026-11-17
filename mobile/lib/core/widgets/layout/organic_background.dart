import 'package:flutter/material.dart';
import '../../theme/colors.dart';

/// Warm ivory background container with subtle organic gradient curves.
class MaatramOrganicBackground extends StatelessWidget {
  final Widget child;
  final bool showHeaderDecoration;

  const MaatramOrganicBackground({
    super.key,
    required this.child,
    this.showHeaderDecoration = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: MaatramColors.background,
      child: Stack(
        fit: StackFit.expand,
        children: [
          if (showHeaderDecoration) ...[
            // Soft warm gold ambient radial glow at top right
            Positioned(
              top: -60,
              right: -60,
              child: Container(
                width: 240,
                height: 240,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      MaatramColors.primaryGold.withOpacity(0.08),
                      MaatramColors.primaryGold.withOpacity(0.0),
                    ],
                  ),
                ),
              ),
            ),
            // Soft organic curve at bottom left
            Positioned(
              bottom: -100,
              left: -80,
              child: Container(
                width: 280,
                height: 280,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      MaatramColors.primaryGold.withOpacity(0.05),
                      MaatramColors.background.withOpacity(0.0),
                    ],
                  ),
                ),
              ),
            ),
          ],
          child,
        ],
      ),
    );
  }
}
