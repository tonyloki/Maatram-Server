import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/layout/organic_background.dart';

class VerifyEmailScreen extends ConsumerStatefulWidget {
  final String? initialEmail;
  final String? initialToken;

  const VerifyEmailScreen({
    super.key,
    this.initialEmail,
    this.initialToken,
  });

  @override
  ConsumerState<VerifyEmailScreen> createState() => _VerifyEmailScreenState();
}

class _VerifyEmailScreenState extends ConsumerState<VerifyEmailScreen> {
  late final TextEditingController _tokenController;
  late final TextEditingController _emailController;
  String? _errorMessage;
  bool _showDeliveryNotice = false;

  String get _maskedEmail {
    final email = _emailController.text.trim();
    if (email.isEmpty) return 'your email address.';
    final parts = email.split('@');
    if (parts.length != 2) return email;
    final name = parts[0];
    final domain = parts[1];
    if (name.length <= 2) return '$name***@$domain';
    return '${name[0]}***${name[name.length - 1]}@$domain';
  }

  @override
  void initState() {
    super.initState();
    _tokenController = TextEditingController(text: widget.initialToken ?? '');
    _emailController = TextEditingController(text: widget.initialEmail ?? '');
  }

  @override
  void dispose() {
    _tokenController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  void _verifyToken() async {
    setState(() {
      _errorMessage = null;
    });

    final token = _tokenController.text.trim();
    final authState = ref.read(authControllerProvider);
    final email = _emailController.text.trim().isNotEmpty
        ? _emailController.text.trim()
        : (authState.user?.email ?? '');

    if (token.isEmpty) {
      setState(() {
        _errorMessage =
            'Please enter the verification token received in your email.';
      });
      return;
    }

    final authController = ref.read(authControllerProvider.notifier);
    final success =
        await authController.verifyEmail(token: token, email: email);

    if (!mounted) return;

    if (success) {
      context.go(RouteNames.pendingApprovalPath);
    } else {
      final stateErr = ref.read(authControllerProvider).errorMessage;
      setState(() {
        _errorMessage = stateErr ??
            'Verification token is invalid or expired. Please try again.';
      });
    }
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
          onPressed: () => context.go(RouteNames.loginPath),
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
                  'Verify Your Email',
                  style: TextStyle(
                    fontFamily: 'Georgia',
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: MaatramColors.deepNavy,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  'We\'ve sent a 6-digit code to\n$_maskedEmail',
                  style: const TextStyle(
                    fontSize: 14,
                    color: Color(0xFF827D73),
                    height: 1.4,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 28),

                // Main card
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
                      if (_errorMessage != null) ...[
                        Container(
                          padding: const EdgeInsets.all(MaatramSpacing.md),
                          decoration: BoxDecoration(
                            color: MaatramColors.error.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                                color: MaatramColors.error.withOpacity(0.3)),
                          ),
                          child: Text(
                            _errorMessage!,
                            style: const TextStyle(
                              color: MaatramColors.errorDark,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],

                      // 6 Pin boxes visual
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: List.generate(6, (index) {
                          final text = _tokenController.text;
                          final char = index < text.length ? text[index] : '';
                          return Container(
                            width: 44,
                            height: 52,
                            decoration: BoxDecoration(
                              color: const Color(0xFFFAF8F5),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: char.isNotEmpty
                                    ? const Color(0xFFF5B817)
                                    : const Color(0xFFE5E0D8),
                                width: char.isNotEmpty ? 1.8 : 1.2,
                              ),
                            ),
                            alignment: Alignment.center,
                            child: Text(
                              char,
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: MaatramColors.deepNavy,
                              ),
                            ),
                          );
                        }),
                      ),
                      const SizedBox(height: 16),

                      // Hidden/overlay actual input for keyboard entry
                      TextField(
                        controller: _tokenController,
                        autofocus: true,
                        maxLength: 64, // supports 6 digits or token string
                        textAlign: TextAlign.center,
                        style: const TextStyle(letterSpacing: 2),
                        decoration: const InputDecoration(
                          counterText: '',
                          hintText: 'Or paste token here',
                          hintStyle: TextStyle(fontSize: 12, color: Color(0xFF827D73)),
                          contentPadding: EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.all(Radius.circular(12)),
                            borderSide: BorderSide(color: Color(0xFFE5E0D8)),
                          ),
                        ),
                        onChanged: (_) => setState(() {}),
                        onSubmitted: (_) => _verifyToken(),
                      ),
                      const SizedBox(height: 16),

                      // Resend countdown
                      const Center(
                        child: Text(
                          'Resend code in 00:45',
                          style: TextStyle(
                            fontSize: 13,
                            color: Color(0xFF827D73),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),

                      Center(
                        child: GestureDetector(
                          onTap: () {
                            setState(() {
                              _showDeliveryNotice = !_showDeliveryNotice;
                            });
                          },
                          child: const Text(
                            'Didn’t receive the email?',
                            style: TextStyle(
                              fontSize: 12,
                              color: Color(0xFF827D73),
                              decoration: TextDecoration.underline,
                            ),
                          ),
                        ),
                      ),
                      if (_showDeliveryNotice) ...[
                        const SizedBox(height: 8),
                        const Text(
                          'We couldn’t confirm email delivery yet. Please check your inbox and spam folder, then try again later.',
                          style: TextStyle(
                            fontSize: 12,
                            color: MaatramColors.charcoal600,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                      const SizedBox(height: 24),

                      MaatramButton(
                        label: 'Verify Email',
                        isLoading: isLoading,
                        isFullWidth: true,
                        size: MaatramButtonSize.lg,
                        onPressed: isLoading ? null : _verifyToken,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Back to Sign In
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
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
