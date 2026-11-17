import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/auth/auth_controller.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/layout/avatar.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../../home/state/home_controller.dart';

class ProfilePhotoScreen extends ConsumerStatefulWidget {
  const ProfilePhotoScreen({super.key});

  @override
  ConsumerState<ProfilePhotoScreen> createState() => _ProfilePhotoScreenState();
}

class _ProfilePhotoScreenState extends ConsumerState<ProfilePhotoScreen> {
  bool _isUploading = false;
  String? _statusMessage;

  void _simulatePhotoSelection() {
    setState(() {
      _isUploading = true;
      _statusMessage = 'Selecting and uploading image...';
    });

    // Signed upload integration
    Future.delayed(const Duration(seconds: 1), () {
      if (mounted) {
        setState(() {
          _isUploading = false;
          _statusMessage = 'Photo updated successfully!';
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    final profile = ref.watch(homeControllerProvider).profile.valueOrNull;
    final name =
        profile?.fullName ?? authState.session?.displayName ?? 'Volunteer';

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
            'Profile Photo',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(MaatramSpacing.md),
          child: Column(
            children: [
              const SizedBox(height: MaatramSpacing.sm),
              // Big Avatar Circle
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border:
                      Border.all(color: MaatramColors.primaryGold, width: 3),
                ),
                child: MaatramAvatar(
                  name: name,
                  imageUrl: profile?.avatarUrl,
                  size: 110,
                ),
              ),
              const SizedBox(height: MaatramSpacing.md),
              Text(
                name,
                style: MaatramTypography.titleLarge.copyWith(
                  fontFamily: 'Georgia',
                  fontWeight: FontWeight.bold,
                  color: MaatramColors.deepNavy,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Visible to event coordinators and community members',
                style: MaatramTypography.bodySmall
                    .copyWith(color: MaatramColors.secondaryText),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: MaatramSpacing.lg),

              // Photo guidelines container
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
                      'Photo Guidelines',
                      style: MaatramTypography.labelLarge.copyWith(
                        fontWeight: FontWeight.bold,
                        color: MaatramColors.deepNavy,
                      ),
                    ),
                    const SizedBox(height: 10),
                    _buildGuidelineRow(Icons.face_rounded,
                        'Clear, front-facing portrait photo'),
                    const SizedBox(height: 8),
                    _buildGuidelineRow(
                        Icons.image_outlined, 'JPG or PNG format, up to 5MB'),
                    const SizedBox(height: 8),
                    _buildGuidelineRow(Icons.verified_user_outlined,
                        'Used for official event check-in verification'),
                  ],
                ),
              ),
              if (_statusMessage != null) ...[
                const SizedBox(height: MaatramSpacing.md),
                Text(
                  _statusMessage!,
                  style: MaatramTypography.bodySmall.copyWith(
                    color: MaatramColors.success,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
              const SizedBox(height: MaatramSpacing.lg),

              MaatramButton(
                label: 'Upload New Photo',
                leadingIcon: const Icon(Icons.upload_rounded, size: 18),
                isLoading: _isUploading,
                onPressed: _simulatePhotoSelection,
              ),
              const SizedBox(height: 12),
              OutlinedButton(
                onPressed: () => context.pop(),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size.fromHeight(48),
                  side: const BorderSide(color: MaatramColors.warmBorder),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16)),
                ),
                child: Text(
                  'Done',
                  style: MaatramTypography.labelLarge
                      .copyWith(color: MaatramColors.deepNavy),
                ),
              ),
              const SizedBox(height: MaatramSpacing.lg),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGuidelineRow(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 18, color: MaatramColors.primaryGold),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: MaatramTypography.bodySmall
                .copyWith(color: MaatramColors.secondaryText),
          ),
        ),
      ],
    );
  }
}
