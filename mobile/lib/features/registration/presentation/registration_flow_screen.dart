import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/route_names.dart';
import '../../../../core/auth/auth_controller.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/spacing.dart';
import '../../../../core/theme/typography.dart';
import '../../../../core/widgets/buttons/maatram_button.dart';
import '../../../../core/widgets/layout/organic_background.dart';
import '../state/registration_state.dart';
import 'steps/step1_basic_details.dart';
import 'steps/step2_category_selection.dart';
import 'steps/step3_category_details.dart';
import 'steps/step4_skills_availability.dart';
import 'steps/step5_privacy_consent.dart';
import 'steps/step6_account_review.dart';

class RegistrationFlowScreen extends ConsumerWidget {
  const RegistrationFlowScreen({super.key});

  static const List<String> stepTitles = [
    'Basic Details',
    'Select Category',
    'Category Details',
    'Skills & Availability',
    'Privacy & Consent',
    'Review & Submit',
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch(registrationProvider);
    final notifier = ref.read(registrationProvider.notifier);
    final authState = ref.watch(authControllerProvider);
    final authController = ref.read(authControllerProvider.notifier);

    final currentStep = formState.currentStep;
    final isSubmitting = authState.isLoading;

    const steps = [
      Step1BasicDetails(),
      Step2CategorySelection(),
      Step3CategoryDetails(),
      Step4SkillsAvailability(),
      Step5PrivacyConsent(),
      Step6AccountReview(),
    ];

    return Scaffold(
      appBar: AppBar(
        backgroundColor: MaatramColors.background,
        elevation: 0,
        scrolledUnderElevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new,
              color: MaatramColors.charcoal900, size: 20),
          onPressed: () {
            if (currentStep > 0) {
              notifier.previousStep();
            } else {
              _showExitConfirmation(context);
            }
          },
        ),
        title: Column(
          children: [
            Text(
              'Step ${currentStep + 1} of ${steps.length}',
              style: MaatramTypography.caption.copyWith(
                color: MaatramColors.charcoal500,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              stepTitles[currentStep],
              style: MaatramTypography.titleSmall.copyWith(
                color: MaatramColors.deepNavy,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        centerTitle: true,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(6.0),
          child: LinearProgressIndicator(
            value: (currentStep + 1) / steps.length,
            backgroundColor: MaatramColors.stone200,
            valueColor:
                const AlwaysStoppedAnimation<Color>(MaatramColors.primaryGold),
            minHeight: 4,
          ),
        ),
      ),
      body: MaatramOrganicBackground(
        showHeaderDecoration: false,
        child: SafeArea(
          child: Column(
            children: [
              Expanded(
                child: IndexedStack(
                  index: currentStep,
                  children: steps,
                ),
              ),

              // Bottom Navigation Actions
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: MaatramSpacing.lg,
                  vertical: MaatramSpacing.md,
                ),
                decoration: BoxDecoration(
                  color: MaatramColors.white,
                  border: const Border(
                    top:
                        BorderSide(color: MaatramColors.warmBorder, width: 1.0),
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.04),
                      blurRadius: 10,
                      offset: const Offset(0, -3),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    if (currentStep > 0) ...[
                      Expanded(
                        flex: 2,
                        child: MaatramButton(
                          label: 'Back',
                          variant: MaatramButtonVariant.outline,
                          onPressed: isSubmitting
                              ? null
                              : () => notifier.previousStep(),
                        ),
                      ),
                      const SizedBox(width: MaatramSpacing.md),
                    ],
                    Expanded(
                      flex: 3,
                      child: MaatramButton(
                        label: currentStep == steps.length - 1
                            ? 'Submit Application'
                            : 'Continue',
                        isLoading: isSubmitting,
                        onPressed: isSubmitting
                            ? null
                            : () async {
                                if (currentStep < steps.length - 1) {
                                  notifier.nextStep();
                                } else {
                                  // Validate final step and submit
                                  if (!notifier.validateCurrentStep()) return;

                                  final payload = formState.toPayload();
                                  final success =
                                      await authController.register(payload);
                                  if (context.mounted) {
                                    if (success) {
                                      context.go(
                                          RouteNames.pendingVerificationPath);
                                    } else {
                                      final err = authState.errorMessage ??
                                          'We couldn’t complete your registration right now. Please try again.';
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(
                                        SnackBar(
                                          content: Text(err),
                                          backgroundColor:
                                              MaatramColors.errorDark,
                                        ),
                                      );
                                    }
                                  }
                                }
                              },
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showExitConfirmation(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Exit Registration?'),
        content: const Text(
          'Your registration progress will be lost if you leave now. Are you sure you want to exit?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Continue Editing'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              if (context.mounted) {
                context.go(RouteNames.loginPath);
              }
            },
            child: const Text('Exit',
                style: TextStyle(color: MaatramColors.error)),
          ),
        ],
      ),
    );
  }
}
