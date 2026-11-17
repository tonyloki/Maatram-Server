import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';
import '../buttons/maatram_button.dart';

/// Reusable error state display for network or service failures with retry callback.
class MaatramErrorState extends StatelessWidget {
  final String title;
  final String message;
  final VoidCallback? onRetry;
  final String retryLabel;

  const MaatramErrorState({
    super.key,
    this.title = 'Unable to Load Content',
    required this.message,
    this.onRetry,
    this.retryLabel = 'Try Again',
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: MaatramSpacing.xxl,
        vertical: MaatramSpacing.xxxl,
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 68,
              height: 68,
              decoration: BoxDecoration(
                color: MaatramColors.errorLight,
                shape: BoxShape.circle,
                border: Border.all(
                  color: MaatramColors.errorBorder,
                  width: 1.5,
                ),
              ),
              child: const Icon(
                Icons.error_outline_rounded,
                size: 34,
                color: MaatramColors.error,
              ),
            ),
            const SizedBox(height: MaatramSpacing.lg),
            Text(
              title,
              textAlign: TextAlign.center,
              style: MaatramTypography.titleLarge,
            ),
            const SizedBox(height: MaatramSpacing.sm),
            Text(
              message,
              textAlign: TextAlign.center,
              style: MaatramTypography.bodyMedium.copyWith(
                color: MaatramColors.secondaryText,
              ),
            ),
            if (onRetry != null) ...[
              const SizedBox(height: MaatramSpacing.xl),
              MaatramButton(
                label: retryLabel,
                onPressed: onRetry,
                variant: MaatramButtonVariant.secondary,
                size: MaatramButtonSize.sm,
                leadingIcon: const Icon(Icons.refresh_rounded,
                    size: 16, color: MaatramColors.white),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
