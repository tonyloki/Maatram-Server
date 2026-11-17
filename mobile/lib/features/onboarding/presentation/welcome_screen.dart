import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/layout/organic_background.dart';

class WelcomeScreen extends ConsumerWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authController = ref.read(authControllerProvider.notifier);

    return Scaffold(
      backgroundColor: MaatramColors.background,
      body: MaatramOrganicBackground(
        showHeaderDecoration: true,
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              padding: const EdgeInsets.symmetric(
                  horizontal: MaatramSpacing.xl, vertical: MaatramSpacing.lg),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Center(
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFFDE68A), Color(0xFFF5B817)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFFF5B817).withOpacity(0.35),
                            blurRadius: 20,
                            offset: const Offset(0, 6),
                          ),
                        ],
                      ),
                      child: const Center(
                        child: Text(
                          '🎉',
                          style: TextStyle(fontSize: 40),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  const Text(
                    'Welcome to\nMaatram!',
                    style: TextStyle(
                      fontFamily: 'Georgia',
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                      color: MaatramColors.deepNavy,
                      height: 1.25,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 10),

                  const Text(
                    'You\'re now a verified volunteer. Let\'s create a better tomorrow together!',
                    style: TextStyle(
                      fontSize: 14,
                      color: Color(0xFF827D73),
                      height: 1.45,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 28),

                  Container(
                    padding: const EdgeInsets.all(MaatramSpacing.lg),
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
                        _buildFeatureRow(
                          icon: Icons.event_available_rounded,
                          title: 'Participate in Initiatives',
                          description:
                              'Sign up for ground drives, workshops, and student mentorship.',
                        ),
                        const SizedBox(height: MaatramSpacing.md),
                        _buildFeatureRow(
                          icon: Icons.stars_rounded,
                          title: 'Track Hours & Impact',
                          description:
                              'Earn gamified impact points and milestone badges as you contribute.',
                        ),
                        const SizedBox(height: MaatramSpacing.md),
                        _buildFeatureRow(
                          icon: Icons.groups_rounded,
                          title: 'Community Network',
                          description:
                              'Collaborate with student volunteers, alumni, and corporate panels.',
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 28),

                  MaatramButton(
                    label: 'Go to Home',
                    isFullWidth: true,
                    size: MaatramButtonSize.lg,
                    onPressed: () async {
                      await authController.completeFirstLaunchWelcome();
                      if (context.mounted) {
                        context.go(RouteNames.homePath);
                      }
                    },
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureRow({
    required IconData icon,
    required String title,
    required String description,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: MaatramColors.primaryGold.withValues(alpha: 0.15),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: MaatramColors.deepNavy, size: 22),
        ),
        const SizedBox(width: MaatramSpacing.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: MaatramTypography.bodyMedium.copyWith(
                  color: MaatramColors.deepNavy,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                description,
                style: MaatramTypography.bodySmall.copyWith(
                  color: MaatramColors.charcoal600,
                  height: 1.3,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
