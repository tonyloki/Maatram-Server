import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/layout/organic_background.dart';

class RejectedScreen extends ConsumerWidget {
  const RejectedScreen({super.key});

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
                      color: const Color(0xFFDC2626).withOpacity(0.12),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                          color: const Color(0xFFDC2626).withOpacity(0.3),
                          width: 1.5),
                    ),
                    child: const Center(
                      child: Icon(
                        Icons.assignment_late_outlined,
                        size: 36,
                        color: Color(0xFFDC2626),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'Application Update',
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
                  'We\'re unable to approve your\napplication at this time.',
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
                  child: const Text(
                    'Thank you for your interest in volunteering with Maatram Foundation. For questions or further information regarding this decision, you may contact the foundation team.',
                    style: TextStyle(
                      fontSize: 13,
                      color: Color(0xFF827D73),
                      height: 1.45,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 28),
                MaatramButton(
                  label: 'Contact Support',
                  isFullWidth: true,
                  size: MaatramButtonSize.lg,
                  onPressed: () => context.push(RouteNames.helpSupportPath),
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
}
