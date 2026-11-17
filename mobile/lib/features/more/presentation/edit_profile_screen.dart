import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/inputs/maatram_text_field.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../../home/state/home_controller.dart';
import '../data/more_repository.dart';

class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({super.key});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _phoneController;
  late TextEditingController _cityController;
  late TextEditingController _bioController;
  bool _isSaving = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void initState() {
    super.initState();
    final profile = ref.read(homeControllerProvider).profile.valueOrNull;
    _phoneController = TextEditingController(text: profile?.mobileNumber ?? '');
    _cityController = TextEditingController(text: profile?.city ?? '');
    _bioController =
        TextEditingController(text: profile?.organizationOrCollege ?? '');
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _cityController.dispose();
    _bioController.dispose();
    super.dispose();
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSaving = true;
      _errorMessage = null;
      _successMessage = null;
    });

    final repo = ref.read(moreRepositoryProvider);
    final updateData = <String, dynamic>{
      'mobile_number': _phoneController.text.trim(),
      'city': _cityController.text.trim(),
      'bio': _bioController.text.trim(),
    };

    final result = await repo.updateProfile(updateData);

    if (mounted) {
      setState(() {
        _isSaving = false;
        if (result != null) {
          _successMessage = 'Profile updated successfully!';
          // Refresh home and profile state
          ref.invalidate(homeControllerProvider);
        } else {
          _errorMessage = 'Failed to update profile. Please try again.';
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final profile = ref.watch(homeControllerProvider).profile.valueOrNull;
    final fullName =
        profile?.fullName ?? authState.user?.displayName ?? 'Volunteer';
    final email = authState.user?.email ?? '—';

    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_rounded,
                color: MaatramColors.deepNavy),
            onPressed: () => context.pop(),
          ),
          title: Text(
            'Edit Profile',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
        ),
        body: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.all(MaatramSpacing.md),
            children: [
              if (_successMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(MaatramSpacing.md),
                  decoration: BoxDecoration(
                    color: const Color(0xFFECFDF5),
                    borderRadius: MaatramRadii.cardRadius,
                    border: Border.all(color: const Color(0xFFA7F3D0)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.check_circle_outline_rounded,
                          color: MaatramColors.success, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(_successMessage!,
                            style: MaatramTypography.bodySmall
                                .copyWith(color: MaatramColors.success)),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: MaatramSpacing.md),
              ],
              if (_errorMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(MaatramSpacing.md),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFEF2F2),
                    borderRadius: MaatramRadii.cardRadius,
                    border: Border.all(color: const Color(0xFFFCA5A5)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline_rounded,
                          color: MaatramColors.error, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(_errorMessage!,
                            style: MaatramTypography.bodySmall
                                .copyWith(color: MaatramColors.error)),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: MaatramSpacing.md),
              ],

              // Read-only Account Identity Card
              Container(
                padding: const EdgeInsets.all(MaatramSpacing.md),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: MaatramRadii.cardRadius,
                  border: Border.all(color: MaatramColors.warmBorder),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Verified Identity',
                      style: MaatramTypography.labelLarge.copyWith(
                        fontWeight: FontWeight.bold,
                        color: MaatramColors.deepNavy,
                      ),
                    ),
                    const SizedBox(height: 10),
                    _buildReadOnlyRow('Full Name', fullName),
                    const Divider(height: 16, color: MaatramColors.warmBorder),
                    _buildReadOnlyRow('Registered Email', email),
                    const SizedBox(height: 6),
                    Text(
                      'Legal name and email changes require administrative verification.',
                      style: MaatramTypography.labelSmall
                          .copyWith(color: MaatramColors.secondaryText),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: MaatramSpacing.md),

              // Editable fields
              Container(
                padding: const EdgeInsets.all(MaatramSpacing.md),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: MaatramRadii.cardRadius,
                  border: Border.all(color: MaatramColors.warmBorder),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Contact & Bio Details',
                      style: MaatramTypography.labelLarge.copyWith(
                        fontWeight: FontWeight.bold,
                        color: MaatramColors.deepNavy,
                      ),
                    ),
                    const SizedBox(height: 16),
                    MaatramTextField(
                      label: 'Mobile Number',
                      hintText: '+91 XXXXX XXXXX',
                      controller: _phoneController,
                      keyboardType: TextInputType.phone,
                    ),
                    const SizedBox(height: 16),
                    MaatramTextField(
                      label: 'Current City',
                      hintText: 'e.g. Chennai, Coimbatore, Bengaluru',
                      controller: _cityController,
                    ),
                    const SizedBox(height: 16),
                    MaatramTextField(
                      label: 'Bio / Volunteering Interests',
                      hintText:
                          'Share a brief summary of your skills and passion',
                      controller: _bioController,
                      maxLines: 3,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: MaatramSpacing.lg),

              MaatramButton(
                label: 'Save Changes',
                isLoading: _isSaving,
                onPressed: _saveProfile,
              ),
              const SizedBox(height: 12),
              Center(
                child: TextButton(
                  onPressed: () => context.pop(),
                  child: Text(
                    'Cancel',
                    style: MaatramTypography.labelLarge.copyWith(
                      color: MaatramColors.secondaryText,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildReadOnlyRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style: MaatramTypography.bodySmall
                .copyWith(color: MaatramColors.secondaryText)),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            value,
            style: MaatramTypography.bodySmall.copyWith(
                fontWeight: FontWeight.bold, color: MaatramColors.deepNavy),
            textAlign: TextAlign.end,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}
