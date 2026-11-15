import 'package:flutter/widgets.dart';
import '../../animations/shimmer.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../cards/maatram_card.dart';

/// Shimmer skeleton primitives for placeholder loading states.
class MaatramSkeletonBox extends StatelessWidget {
  final double width;
  final double height;
  final BorderRadius? borderRadius;

  const MaatramSkeletonBox({
    super.key,
    required this.width,
    required this.height,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    return MaatramShimmer(
      child: Container(
        width: width,
        height: height,
        decoration: BoxDecoration(
          color: MaatramColors.shimmerBase,
          borderRadius: borderRadius ?? MaatramRadii.radiusSm,
        ),
      ),
    );
  }
}

/// Skeleton representation of an event card during async fetch.
class MaatramEventCardSkeleton extends StatelessWidget {
  const MaatramEventCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaatramCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              MaatramSkeletonBox(width: 80, height: 22, borderRadius: MaatramRadii.radiusPill),
              MaatramSkeletonBox(width: 65, height: 22, borderRadius: MaatramRadii.radiusPill),
            ],
          ),
          SizedBox(height: MaatramSpacing.md),
          MaatramSkeletonBox(width: double.infinity, height: 20),
          SizedBox(height: MaatramSpacing.xs),
          MaatramSkeletonBox(width: 180, height: 20),
          SizedBox(height: MaatramSpacing.md),
          MaatramSkeletonBox(
            width: double.infinity,
            height: 38,
            borderRadius: MaatramRadii.radiusMd,
          ),
        ],
      ),
    );
  }
}

/// Skeleton representation of statistical summary cards.
class MaatramStatCardSkeleton extends StatelessWidget {
  const MaatramStatCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaatramCard(
      padding: MaatramSpacing.compactCardPadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          MaatramSkeletonBox(width: 38, height: 38, borderRadius: MaatramRadii.radiusLg),
          SizedBox(height: MaatramSpacing.md),
          MaatramSkeletonBox(width: 70, height: 28),
          SizedBox(height: MaatramSpacing.xs),
          MaatramSkeletonBox(width: 90, height: 14),
        ],
      ),
    );
  }
}

