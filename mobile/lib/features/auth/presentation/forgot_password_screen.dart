import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/inputs/maatram_text_field.dart';
import '../../../core/widgets/layout/organic_background.dart';

class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  String? _emailError;
  bool _requestSent = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  void _submitRequest() async {
    setState(() {
      _emailError = null;
    });

    final email = _emailController.text.trim();
    if (email.isEmpty) {
      setState(() => _emailError = 'Enter your email address.');
      return;
    } else if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(email)) {
      setState(() => _emailError = 'Enter a valid email address.');
      return;
    }

    final authController = ref.read(authControllerProvider.notifier);
    await authController.requestPasswordReset(email: email);

    if (!mounted) return;

    // Backend returns neutral response for security
    setState(() {
      _requestSent = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final isLoading = authState.isLoading;

    return Scaffold(
      backgroundColor: MaatramColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new,
              color: MaatramColors.charcoal900, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: MaatramOrganicBackground(
        showHeaderDecoration: true,
        child: SafeArea(
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: MaatramSpacing.xl),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 12),
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
                        Icons.mail_rounded,
                        size: 38,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'Forgot Password?',
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
                  'No worries! Enter your registered email and we\'ll send a reset link.',
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
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      if (_requestSent) ...[
                        Container(
                          padding: const EdgeInsets.all(MaatramSpacing.md),
                          decoration: BoxDecoration(
                            color: MaatramColors.success.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(
                                color: MaatramColors.success.withOpacity(0.3)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Row(
                                children: [
                                  Icon(Icons.check_circle_outline,
                                      color: MaatramColors.forestGreen, size: 20),
                                  SizedBox(width: 8),
                                  Text(
                                    'Request Submitted',
                                    style: TextStyle(
                                      color: MaatramColors.forestGreen,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 6),
                              const Text(
                                'If an account matches this email, password-reset instructions will be sent.',
                                style: TextStyle(
                                  color: MaatramColors.charcoal800,
                                  fontSize: 13,
                                  height: 1.4,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 18),
                        MaatramButton(
                          label: 'Enter Reset Code',
                          isFullWidth: true,
                          size: MaatramButtonSize.lg,
                          onPressed: () {
                            final email = _emailController.text.trim();
                            context.push(
                                '${RouteNames.resetPasswordPath}?email=$email');
                          },
                        ),
                      ] else ...[
                        const Text(
                          'Email address',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                            color: MaatramColors.deepNavy,
                          ),
                        ),
                        const SizedBox(height: 6),
                        MaatramTextField(
                          controller: _emailController,
                          hint: 'Enter your email address',
                          keyboardType: TextInputType.emailAddress,
                          errorText: _emailError,
                        ),
                        const SizedBox(height: 24),
                        MaatramButton(
                          label: 'Send Reset Link',
                          isLoading: isLoading,
                          isFullWidth: true,
                          size: MaatramButtonSize.lg,
                          onPressed: isLoading ? null : _submitRequest,
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                Center(
                  child: GestureDetector(
                    onTap: () => context.go(RouteNames.loginPath),
                    child: const Text(
                      'Back to Sign In',
                      style: TextStyle(
                        color: MaatramColors.deepNavy,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
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
