import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/spacing.dart';
import '../../state/registration_state.dart';

class Step5PrivacyConsent extends ConsumerWidget {
  const Step5PrivacyConsent({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch(registrationProvider);
    final notifier = ref.read(registrationProvider.notifier);

    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.lg, vertical: MaatramSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Privacy & Consent',
            style: TextStyle(
              fontFamily: 'Georgia',
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'Your privacy matters. Please review and provide your consents.',
            style: TextStyle(
              fontSize: 13,
              color: Color(0xFF827D73),
              height: 1.35,
            ),
          ),
          const SizedBox(height: 20),

          // White Card Container matching Reference Screen 9
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
                _buildToggleRow(
                  'Show my name on leaderboard',
                  formState.leaderboardVisible,
                  (val) => notifier.updateConsent(leaderboardVisible: val),
                ),
                _buildDivider(),
                _buildToggleRow(
                  'Show my profile in volunteer directory',
                  formState.nameVisible,
                  (val) => notifier.updateConsent(nameVisible: val),
                ),
                _buildDivider(),
                _buildToggleRow(
                  'Allow my activity to be shared',
                  formState.linkedinContent,
                  (val) => notifier.updateConsent(linkedinContent: val),
                ),
                _buildDivider(),
                _buildToggleRow(
                  'Receive event notifications',
                  formState.thankYouEmails,
                  (val) => notifier.updateConsent(thankYouEmails: val),
                ),
                _buildDivider(),
                _buildToggleRow(
                  'Receive impact stories',
                  formState.contactAvailable,
                  (val) => notifier.updateConsent(contactAvailable: val),
                ),
                _buildDivider(),
                _buildToggleRow(
                  'Research & analytics (anonymous)',
                  true,
                  (_) {},
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildToggleRow(String label, bool value, ValueChanged<bool> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 13,
                color: MaatramColors.deepNavy,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Transform.scale(
            scale: 0.85,
            child: Switch(
              value: value,
              activeColor: Colors.white,
              activeTrackColor: const Color(0xFFF5B817),
              inactiveThumbColor: Colors.white,
              inactiveTrackColor: const Color(0xFFE5E0D8),
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return const Divider(height: 1, color: Color(0xFFF3EFEA));
  }
}
