import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/models/consent_model.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/feedback/skeleton_loader.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../data/more_repository.dart';

class PrivacyScreen extends ConsumerStatefulWidget {
  const PrivacyScreen({super.key});

  @override
  ConsumerState<PrivacyScreen> createState() => _PrivacyScreenState();
}

class _PrivacyScreenState extends ConsumerState<PrivacyScreen> {
  ConsentModel? _consent;
  bool _isLoading = true;
  String? _statusMessage;

  @override
  void initState() {
    super.initState();
    _loadConsent();
  }

  Future<void> _loadConsent() async {
    final repo = ref.read(moreRepositoryProvider);
    final data = await repo.getConsent();
    if (mounted) {
      setState(() {
        _consent = data ??
            ConsentModel(
              id: '',
              volunteerProfileId: '',
              leaderboardVisible: true,
              nameVisible: true,
              thankYouEmails: true,
              linkedinContent: false,
              contactAvailable: false,
              mediaUsage: true,
              version: 1,
              updatedAt: DateTime.now(),
            );
        _isLoading = false;
      });
    }
  }

  Future<void> _updateConsent(ConsentModel updated) async {
    setState(() {
      _consent = updated;
      _statusMessage = 'Updating preferences...';
    });

    final repo = ref.read(moreRepositoryProvider);
    final result = await repo.updateConsent(updated);

    if (mounted) {
      setState(() {
        if (result != null) {
          _consent = result;
          _statusMessage = 'Privacy preferences saved.';
        } else {
          _statusMessage = 'Failed to update. Reverting changes.';
          _loadConsent();
        }
      });

      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          setState(() => _statusMessage = null);
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
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
            'Privacy & Consents',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
        ),
        body: _isLoading
            ? const Padding(
                padding: EdgeInsets.all(MaatramSpacing.md),
                child: Column(
                  children: [
                    MaatramSkeletonBox(
                        width: double.infinity,
                        height: 80,
                        borderRadius: BorderRadius.all(Radius.circular(20))),
                    SizedBox(height: 12),
                    MaatramSkeletonBox(
                        width: double.infinity,
                        height: 240,
                        borderRadius: BorderRadius.all(Radius.circular(20))),
                  ],
                ),
              )
            : ListView(
                padding: const EdgeInsets.all(MaatramSpacing.md),
                children: [
                  // Statutory Governance Note
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
                        Row(
                          children: [
                            const Icon(Icons.shield_outlined,
                                color: MaatramColors.primaryGold, size: 22),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'Account-Level Privacy',
                                style: MaatramTypography.titleSmall.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: MaatramColors.deepNavy,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'Your affirmative consent choices are securely stored in our canonical database and backed by an immutable audit trail. Changes take effect across all portal platforms.',
                          style: MaatramTypography.bodySmall.copyWith(
                            color: MaatramColors.secondaryText,
                            height: 1.4,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: MaatramSpacing.md),

                  if (_statusMessage != null) ...[
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 8),
                      decoration: BoxDecoration(
                        color: const Color(0xFFECFDF5),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFFA7F3D0)),
                      ),
                      child: Text(
                        _statusMessage!,
                        style: MaatramTypography.labelSmall.copyWith(
                          color: MaatramColors.success,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(height: MaatramSpacing.sm),
                  ],

                  // 6 Consent Dimensions Toggles
                  Material(
                    color: Colors.white,
                    clipBehavior: Clip.antiAlias,
                    shape: RoundedRectangleBorder(
                      borderRadius: MaatramRadii.cardRadius,
                      side: const BorderSide(color: MaatramColors.warmBorder),
                    ),
                    child: Column(
                      children: [
                        _buildConsentTile(
                          title: 'Public Leaderboard Visibility',
                          subtitle:
                              'Display your name and points on the volunteer leaderboard',
                          value: _consent!.leaderboardVisible,
                          onChanged: (val) => _updateConsent(
                              _consent!.copyWith(leaderboardVisible: val)),
                        ),
                        const Divider(
                            height: 1, color: MaatramColors.warmBorder),
                        _buildConsentTile(
                          title: 'Full Name Visibility',
                          subtitle:
                              'Show your full name instead of an anonymized identifier',
                          value: _consent!.nameVisible,
                          onChanged: (val) => _updateConsent(
                              _consent!.copyWith(nameVisible: val)),
                        ),
                        const Divider(
                            height: 1, color: MaatramColors.warmBorder),
                        _buildConsentTile(
                          title: 'Event Impact & Thank-You Emails',
                          subtitle:
                              'Receive post-event summaries and appreciation notes from beneficiaries',
                          value: _consent!.thankYouEmails,
                          onChanged: (val) => _updateConsent(
                              _consent!.copyWith(thankYouEmails: val)),
                        ),
                        const Divider(
                            height: 1, color: MaatramColors.warmBorder),
                        _buildConsentTile(
                          title: 'Social & LinkedIn Story Sharing',
                          subtitle:
                              'Permit featured highlights of your volunteering milestones on foundation social media',
                          value: _consent!.linkedinContent,
                          onChanged: (val) => _updateConsent(
                              _consent!.copyWith(linkedinContent: val)),
                        ),
                        const Divider(
                            height: 1, color: MaatramColors.warmBorder),
                        _buildConsentTile(
                          title: 'Volunteer Directory Availability',
                          subtitle:
                              'Allow fellow verified volunteers to view your profile contact for carpooling or coordination',
                          value: _consent!.contactAvailable,
                          onChanged: (val) => _updateConsent(
                              _consent!.copyWith(contactAvailable: val)),
                        ),
                        const Divider(
                            height: 1, color: MaatramColors.warmBorder),
                        _buildConsentTile(
                          title: 'Event Photography & Media Usage',
                          subtitle:
                              'Consent to appearance in official foundation event photo galleries',
                          value: _consent!.mediaUsage,
                          onChanged: (val) => _updateConsent(
                              _consent!.copyWith(mediaUsage: val)),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: MaatramSpacing.lg),
                ],
              ),
      ),
    );
  }

  Widget _buildConsentTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontFamily: 'Roboto',
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: MaatramColors.deepNavy,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontSize: 12,
                    color: MaatramColors.secondaryText,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Switch(
            value: value,
            activeColor: MaatramColors.primaryGold,
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }
}
