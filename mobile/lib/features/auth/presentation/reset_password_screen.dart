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

class ResetPasswordScreen extends ConsumerStatefulWidget {
  final String? initialEmail;

  const ResetPasswordScreen({
    super.key,
    this.initialEmail,
  });

  @override
  ConsumerState<ResetPasswordScreen> createState() =>
      _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen> {
  late final TextEditingController _emailController;
  final _otpController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _obscureNewPassword = true;
  bool _obscureConfirmPassword = true;
  String? _passwordError;
  String? _confirmError;
  String? _formError;

  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController(text: widget.initialEmail ?? '');
  }

  @override
  void dispose() {
    _emailController.dispose();
    _otpController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _confirmReset() async {
    setState(() {
      _passwordError = null;
      _confirmError = null;
      _formError = null;
    });

    final email = _emailController.text.trim();
    final otp = _otpController.text.trim();
    final newPassword = _newPasswordController.text;
    final confirmPassword = _confirmPasswordController.text;

    bool hasError = false;

    if (email.isEmpty) {
      _formError = 'Please specify your email address.';
      hasError = true;
    }

    if (otp.isNotEmpty && (otp.length != 6 || int.tryParse(otp) == null)) {
      _formError = 'Enter the 6-digit numeric verification code.';
      hasError = true;
    }

    if (newPassword.length < 8) {
      _passwordError = 'Password must be at least 8 characters long.';
      hasError = true;
    }

    if (confirmPassword != newPassword) {
      _confirmError = 'Passwords do not match.';
      hasError = true;
    }

    if (hasError) {
      setState(() {});
      return;
    }

    final authController = ref.read(authControllerProvider.notifier);
    final success = await authController.confirmPasswordReset(
      email: email,
      otp: otp,
      newPassword: newPassword,
    );

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
              'Password updated successfully. Please sign in with your new password.'),
          backgroundColor: MaatramColors.forestGreen,
        ),
      );
      context.go(RouteNames.loginPath);
    } else {
      final stateErr = ref.read(authControllerProvider).errorMessage;
      setState(() {
        _formError = stateErr ??
            'The reset code is invalid or has expired. Please try again.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final isLoading = authState.isLoading;

    final pass = _newPasswordController.text;
    final hasMinLength = pass.length >= 8;
    final hasUppercase = pass.contains(RegExp(r'[A-Z]'));
    final hasNumber = pass.contains(RegExp(r'[0-9]'));

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
            physics: const ClampingScrollPhysics(),
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
                        Icons.lock_rounded,
                        size: 36,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'Reset Your Password',
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
                  'Create a new password for your account.',
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
                      if (_formError != null) ...[
                        Container(
                          padding: const EdgeInsets.all(MaatramSpacing.md),
                          decoration: BoxDecoration(
                            color: MaatramColors.error.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(
                                color: MaatramColors.error.withOpacity(0.3)),
                          ),
                          child: Text(
                            _formError!,
                            style: const TextStyle(
                              color: MaatramColors.errorDark,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],

                      // New Password
                      const Text(
                        'New password',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          color: MaatramColors.deepNavy,
                        ),
                      ),
                      const SizedBox(height: 6),
                      MaatramTextField(
                        controller: _newPasswordController,
                        hint: 'Enter new password',
                        obscureText: _obscureNewPassword,
                        errorText: _passwordError,
                        onChanged: (_) => setState(() {}),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscureNewPassword
                                ? Icons.visibility_off_outlined
                                : Icons.visibility_outlined,
                            color: MaatramColors.charcoal500,
                            size: 20,
                          ),
                          onPressed: () => setState(
                              () => _obscureNewPassword = !_obscureNewPassword),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Confirm Password
                      const Text(
                        'Confirm password',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          color: MaatramColors.deepNavy,
                        ),
                      ),
                      const SizedBox(height: 6),
                      MaatramTextField(
                        controller: _confirmPasswordController,
                        hint: 'Confirm new password',
                        obscureText: _obscureConfirmPassword,
                        errorText: _confirmError,
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscureConfirmPassword
                                ? Icons.visibility_off_outlined
                                : Icons.visibility_outlined,
                            color: MaatramColors.charcoal500,
                            size: 20,
                          ),
                          onPressed: () => setState(() =>
                              _obscureConfirmPassword =
                                  !_obscureConfirmPassword),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Criteria Checklist matching Reference
                      _buildCriteriaItem('At least 8 characters', hasMinLength),
                      const SizedBox(height: 6),
                      _buildCriteriaItem('One uppercase letter', hasUppercase),
                      const SizedBox(height: 6),
                      _buildCriteriaItem('One number', hasNumber),
                      const SizedBox(height: 24),

                      // Reset Password Button
                      MaatramButton(
                        label: 'Reset Password',
                        isLoading: isLoading,
                        isFullWidth: true,
                        size: MaatramButtonSize.lg,
                        onPressed: isLoading ? null : _confirmReset,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCriteriaItem(String label, bool satisfied) {
    return Row(
      children: [
        Icon(
          satisfied ? Icons.check_circle_rounded : Icons.check_circle_outline,
          size: 16,
          color: satisfied ? const Color(0xFFD49504) : const Color(0xFFD1CDC7),
        ),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: satisfied ? const Color(0xFFD49504) : const Color(0xFF827D73),
            fontWeight: satisfied ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
      ],
    );
  }
}
