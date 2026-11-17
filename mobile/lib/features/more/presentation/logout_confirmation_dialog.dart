import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/buttons/maatram_button.dart';

class LogoutConfirmationDialog extends ConsumerStatefulWidget {
  const LogoutConfirmationDialog({super.key});

  @override
  ConsumerState<LogoutConfirmationDialog> createState() =>
      _LogoutConfirmationDialogState();
}

class _LogoutConfirmationDialogState
    extends ConsumerState<LogoutConfirmationDialog> {
  bool _isLoggingOut = false;

  Future<void> _handleLogout() async {
    setState(() => _isLoggingOut = true);
    final controller = ref.read(authControllerProvider.notifier);
    await controller.logout();
    if (mounted) {
      Navigator.of(context).pop();
      context.go(RouteNames.welcomeSplashPath);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      padding: const EdgeInsets.all(MaatramSpacing.lg),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Drag handle
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: MaatramColors.warmBorder,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: MaatramSpacing.lg),

            // Warning Icon
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: const Color(0xFFFEF2F2),
                shape: BoxShape.circle,
                border: Border.all(color: const Color(0xFFFCA5A5)),
              ),
              child: const Icon(Icons.logout_rounded,
                  color: MaatramColors.error, size: 32),
            ),
            const SizedBox(height: MaatramSpacing.md),

            // Headline
            Text(
              'Sign Out of Maatram?',
              style: MaatramTypography.headlineSmall.copyWith(
                fontFamily: 'Georgia',
                fontWeight: FontWeight.bold,
                color: MaatramColors.deepNavy,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),

            // Explanatory copy
            Text(
              'Are you sure you want to sign out? Your credentials and session will be securely terminated.',
              style: MaatramTypography.bodyMedium.copyWith(
                color: MaatramColors.secondaryText,
                height: 1.4,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MaatramSpacing.xl),

            // Sign out button
            MaatramButton(
              label: 'Sign Out',
              variant: MaatramButtonVariant.primary,
              isLoading: _isLoggingOut,
              onPressed: _handleLogout,
            ),
            const SizedBox(height: 10),

            // Cancel button
            OutlinedButton(
              onPressed: () => Navigator.of(context).pop(),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size.fromHeight(48),
                side: const BorderSide(color: MaatramColors.warmBorder),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16)),
              ),
              child: Text(
                'Cancel',
                style: MaatramTypography.labelLarge.copyWith(
                  color: MaatramColors.deepNavy,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}
