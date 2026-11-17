import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/layout/organic_background.dart';

class PendingVerificationScreen extends ConsumerWidget {
  const PendingVerificationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authController = ref.read(authControllerProvider.notifier);

    return Scaffold(
      backgroundColor: MaatramColors.background,
      body: MaatramOrganicBackground(
        showHeaderDecoration: true,
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: MaatramSpacing.xl),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Center(
                  child: Container(
                    width: 76,
                    height: 60,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFFFDE68A), Color(0xFFF5B817)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFFF5B817).withOpacity(0.3),
                          blurRadius: 16,
                          offset: const Offset(0, 6),
                        ),
                      ],
                    ),
                    child: const Center(
                      child: Icon(
                        Icons.hourglass_top_rounded,
                        size: 36,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'Email Verification Pending',
                  style: TextStyle(
                    fontFamily: 'Georgia',
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: MaatramColors.deepNavy,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                const Text(
                  'Please verify your email to\ncontinue your registration.',
                  style: TextStyle(
                    fontSize: 14,
                    color: Color(0xFF827D73),
                    height: 1.4,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 28),
                Container(
                  padding: const EdgeInsets.all(MaatramSpacing.xl),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: const Color(0xFFEFECE6)),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.04),
                        blurRadius: 16,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      _buildChecklistItem('Check your inbox (and spam)'),
                      const SizedBox(height: 14),
                      _buildChecklistItem('Use the 6-digit code we sent'),
                      const SizedBox(height: 14),
                      _buildChecklistItem('Verification links expire in 10 minutes'),
                    ],
                  ),
                ),
                const SizedBox(height: 28),
                MaatramButton(
                  label: 'Enter Verification Code',
                  isFullWidth: true,
                  size: MaatramButtonSize.lg,
                  onPressed: () {
                    context.push(RouteNames.verifyEmailPath);
                  },
                ),
                const SizedBox(height: 14),
                OutlinedButton(
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    side: const BorderSide(color: Color(0xFFD1CDC7), width: 1.2),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  onPressed: () async {
                    await authController.logout();
                    if (context.mounted) {
                      context.go(RouteNames.loginPath);
                    }
                  },
                  child: const Text(
                    'Sign Out',
                    style: TextStyle(
                      color: MaatramColors.deepNavy,
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildChecklistItem(String text) {
    return Row(
      children: [
        const Icon(
          Icons.check_circle_rounded,
          color: Color(0xFFD49504),
          size: 20,
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              fontSize: 13,
              color: MaatramColors.deepNavy,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }
}
