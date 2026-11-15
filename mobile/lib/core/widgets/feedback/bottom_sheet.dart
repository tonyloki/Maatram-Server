import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/spacing.dart';
import '../../theme/typography.dart';
import '../buttons/maatram_button.dart';

/// Modal bottom sheet utility adhering to Maatram organic curved visual tokens.
abstract final class MaatramBottomSheet {
  static Future<T?> show<T>({
    required BuildContext context,
    required String title,
    String? subtitle,
    required Widget child,
    bool isDismissible = true,
  }) {
    return showModalBottomSheet<T>(
      context: context,
      isDismissible: isDismissible,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          decoration: const BoxDecoration(
            color: MaatramColors.white,
            borderRadius: MaatramRadii.bottomSheetRadius,
          ),
          padding: EdgeInsets.only(
            left: MaatramSpacing.xl,
            right: MaatramSpacing.xl,
            top: MaatramSpacing.md,
            bottom: MediaQuery.of(context).viewInsets.bottom + MaatramSpacing.xl,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Drag Handle
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.only(bottom: MaatramSpacing.md),
                  decoration: BoxDecoration(
                    color: MaatramColors.stone300,
                    borderRadius: MaatramRadii.radiusPill,
                  ),
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(title, style: MaatramTypography.headlineMedium),
                        if (subtitle != null) ...[
                          const SizedBox(height: MaatramSpacing.xxs),
                          Text(subtitle, style: MaatramTypography.bodySmall),
                        ],
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 20, color: MaatramColors.charcoal600),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              const SizedBox(height: MaatramSpacing.lg),
              child,
            ],
          ),
        );
      },
    );
  }

  /// Show confirmation prompt bottom sheet
  static Future<bool> showConfirmation({
    required BuildContext context,
    required String title,
    required String message,
    String confirmLabel = 'Confirm',
    String cancelLabel = 'Cancel',
    bool isDanger = false,
  }) async {
    final result = await show<bool>(
      context: context,
      title: title,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(message, style: MaatramTypography.bodyMedium),
          const SizedBox(height: MaatramSpacing.xl),
          Row(
            children: [
              Expanded(
                child: MaatramButton(
                  label: cancelLabel,
                  variant: MaatramButtonVariant.outline,
                  onPressed: () => Navigator.of(context).pop(false),
                ),
              ),
              const SizedBox(width: MaatramSpacing.md),
              Expanded(
                child: MaatramButton(
                  label: confirmLabel,
                  variant: isDanger ? MaatramButtonVariant.danger : MaatramButtonVariant.primary,
                  onPressed: () => Navigator.of(context).pop(true),
                ),
              ),
            ],
          ),
        ],
      ),
    );

    return result ?? false;
  }
}

