import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../app/router/route_names.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/inputs/maatram_text_field.dart';
import '../../../core/widgets/layout/organic_background.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _passwordFocusNode = FocusNode();

  bool _obscurePassword = true;
  bool _isCapsLockOn = false;
  String? _emailError;
  String? _passwordError;
  String? _formError;

  @override
  void initState() {
    super.initState();
    HardwareKeyboard.instance.addHandler(_handleKeyEvent);
  }

  @override
  void dispose() {
    HardwareKeyboard.instance.removeHandler(_handleKeyEvent);
    _emailController.dispose();
    _passwordController.dispose();
    _passwordFocusNode.dispose();
    super.dispose();
  }

  bool _handleKeyEvent(KeyEvent event) {
    final capsLockActive = HardwareKeyboard.instance.lockModesEnabled
        .contains(KeyboardLockMode.capsLock);
    if (_isCapsLockOn != capsLockActive) {
      setState(() {
        _isCapsLockOn = capsLockActive;
      });
    }
    return false;
  }

  void _validateAndSubmit() async {
    setState(() {
      _emailError = null;
      _passwordError = null;
      _formError = null;
    });

    final email = _emailController.text.trim();
    final password = _passwordController.text;

    bool hasError = false;

    if (email.isEmpty) {
      _emailError = 'Enter your email address.';
      hasError = true;
    } else if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(email)) {
      _emailError = 'Enter a valid email address.';
      hasError = true;
    }

    if (password.isEmpty) {
      _passwordError = 'Enter your password.';
      hasError = true;
    }

    if (hasError) {
      setState(() {});
      return;
    }

    final authController = ref.read(authControllerProvider.notifier);
    final success =
        await authController.login(email: email, password: password);

    if (!mounted) return;

    if (success) {
      final authState = ref.read(authControllerProvider);
      final session = authState.user;

      if (session == null) {
        context.go(RouteNames.homePath);
        return;
      }

      // Admin access barrier in Volunteer Mobile App
      if (session.role.toUpperCase() == 'ADMIN' ||
          session.role.toUpperCase() == 'SUPER_ADMIN') {
        setState(() {
          _formError =
              "You don't have access to the Volunteer Mobile App. Please use the Admin Portal on web.";
        });
        await ref.read(authControllerProvider.notifier).logout();
        return;
      }

      // Exact 4-state post-login routing
      switch (session.status.toUpperCase()) {
        case 'PENDING_VERIFICATION':
          context.go(RouteNames.pendingVerificationPath);
          break;
        case 'PENDING_ADMIN_APPROVAL':
        case 'PENDING_APPROVAL':
        case 'PENDING':
          context.go(RouteNames.pendingApprovalPath);
          break;
        case 'REJECTED':
          context.go(RouteNames.rejectedPath);
          break;
        case 'APPROVED':
        default:
          if (session.status.toUpperCase().contains('PENDING')) {
            context.go(RouteNames.pendingApprovalPath);
            break;
          }
          if (authState.isFirstLaunch) {
            context.go(RouteNames.welcomePath);
          } else {
            context.go(RouteNames.homePath);
          }
          break;
      }
    } else {
      final authState = ref.read(authControllerProvider);
      final errMsg = authState.errorMessage ??
          'The email address or password is incorrect.';
      setState(() {
        _formError = errMsg;
      });
    }
  }

  bool _rememberMe = false;

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final isLoading = authState.isLoading;

    return Scaffold(
      backgroundColor: MaatramColors.background,
      body: MaatramOrganicBackground(
        showHeaderDecoration: true,
        child: SafeArea(
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: SingleChildScrollView(
                physics: const ClampingScrollPhysics(),
                padding: const EdgeInsets.symmetric(
                  horizontal: MaatramSpacing.lg,
                  vertical: MaatramSpacing.md,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 20),

                    // Official Maatram Foundation Centered Logo
                    Center(
                      child: Image.asset(
                        'assets/images/logo.png',
                        height: 70,
                        fit: BoxFit.contain,
                        semanticLabel: 'Maatram Foundation Logo',
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Editorial Serif Heading
                    Text(
                      'Together, We Make\na Difference.',
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontFamily: 'Georgia',
                        fontSize: 26,
                        fontWeight: FontWeight.bold,
                        color: MaatramColors.deepNavy,
                        height: 1.25,
                      ),
                    ),
                    const SizedBox(height: 28),

                    // Main Form Card Container
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(color: const Color(0xFFEFECE6)),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.04),
                            blurRadius: 16,
                            offset: const Offset(0, 6),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Server Error Banner
                          if (_formError != null) ...[
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: MaatramColors.error.withOpacity(0.1),
                                borderRadius: BorderRadius.circular(10),
                                border: Border.all(
                                    color: MaatramColors.error.withOpacity(0.3)),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.error_outline,
                                      size: 18, color: MaatramColors.errorDark),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _formError!,
                                      style: MaatramTypography.bodySmall.copyWith(
                                        color: MaatramColors.errorDark,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 16),
                          ],

                          // Email Address Field
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
                            hint: 'Enter your email',
                            keyboardType: TextInputType.emailAddress,
                            autofillHints: const [AutofillHints.email],
                            errorText: _emailError,
                            onSubmitted: (_) => _passwordFocusNode.requestFocus(),
                          ),
                          const SizedBox(height: 18),

                          // Password Field
                          const Text(
                            'Password',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w500,
                              color: MaatramColors.deepNavy,
                            ),
                          ),
                          const SizedBox(height: 6),
                          MaatramTextField(
                            controller: _passwordController,
                            focusNode: _passwordFocusNode,
                            hint: 'Enter your password',
                            obscureText: _obscurePassword,
                            autofillHints: const [AutofillHints.password],
                            suffixIcon: IconButton(
                              icon: Icon(
                                _obscurePassword
                                    ? Icons.visibility_off_outlined
                                    : Icons.visibility_outlined,
                                color: MaatramColors.charcoal500,
                                size: 20,
                              ),
                              onPressed: () => setState(
                                  () => _obscurePassword = !_obscurePassword),
                            ),
                            errorText: _passwordError,
                            onSubmitted: (_) => _validateAndSubmit(),
                          ),

                          // Caps Lock Warning
                          if (_isCapsLockOn) ...[
                            const SizedBox(height: 4),
                            const Row(
                              children: [
                                Icon(Icons.arrow_upward,
                                    size: 14, color: MaatramColors.warningDark),
                                SizedBox(width: 4),
                                Text(
                                  'Caps Lock is ON',
                                  style: TextStyle(
                                    color: MaatramColors.warningDark,
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ],
                          const SizedBox(height: 12),

                          // Remember Me & Forgot Password Row
                          Wrap(
                            alignment: WrapAlignment.spaceBetween,
                            crossAxisAlignment: WrapCrossAlignment.center,
                            runSpacing: 8,
                            children: [
                              GestureDetector(
                                onTap: () {
                                  setState(() {
                                    _rememberMe = !_rememberMe;
                                  });
                                },
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: Checkbox(
                                        value: _rememberMe,
                                        activeColor: MaatramColors.primaryGold,
                                        checkColor: MaatramColors.deepNavy,
                                        shape: RoundedRectangleBorder(
                                          borderRadius: BorderRadius.circular(4),
                                        ),
                                        side: const BorderSide(
                                          color: Color(0xFFD1CDC7),
                                          width: 1.5,
                                        ),
                                        onChanged: (val) {
                                          setState(() {
                                            _rememberMe = val ?? false;
                                          });
                                        },
                                      ),
                                    ),
                                    const SizedBox(width: 6),
                                    const Text(
                                      'Remember me',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: MaatramColors.charcoal700,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              GestureDetector(
                                onTap: () => context
                                    .push(RouteNames.forgotPasswordPath),
                                child: const Text(
                                  'Forgot Password?',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: MaatramColors.deepNavy,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 24),

                          // Sign In Primary Button
                          MaatramButton(
                            label: 'Sign In',
                            isLoading: isLoading,
                            isFullWidth: true,
                            size: MaatramButtonSize.lg,
                            onPressed: isLoading ? null : _validateAndSubmit,
                          ),
                          const SizedBox(height: 20),

                          // "or" Divider
                          Row(
                            children: [
                              Expanded(
                                child: Container(
                                  height: 1,
                                  color: const Color(0xFFE5E0D8),
                                ),
                              ),
                              const Padding(
                                padding: EdgeInsets.symmetric(horizontal: 14),
                                child: Text(
                                  'or',
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: Color(0xFF827D73),
                                  ),
                                ),
                              ),
                              Expanded(
                                child: Container(
                                  height: 1,
                                  color: const Color(0xFFE5E0D8),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),

                          // "Create a new account" Outline Button
                          OutlinedButton(
                            style: OutlinedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              side: const BorderSide(
                                  color: Color(0xFFD1CDC7), width: 1.2),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16),
                              ),
                            ),
                            onPressed: () =>
                                context.push(RouteNames.registerPath),
                            child: const Text(
                              'Create a new account',
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
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
