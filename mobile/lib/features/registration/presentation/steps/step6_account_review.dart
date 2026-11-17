import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/radii.dart';
import '../../../../core/theme/spacing.dart';
import '../../../../core/theme/typography.dart';
import '../../../../core/widgets/inputs/maatram_text_field.dart';
import '../../state/registration_state.dart';

class Step6AccountReview extends ConsumerStatefulWidget {
  const Step6AccountReview({super.key});

  @override
  ConsumerState<Step6AccountReview> createState() => _Step6AccountReviewState();
}

class _Step6AccountReviewState extends ConsumerState<Step6AccountReview> {
  bool _obscurePassword = true;
  bool _obscureConfirm = true;

  @override
  Widget build(BuildContext context) {
    final formState = ref.watch(registrationProvider);
    final notifier = ref.read(registrationProvider.notifier);

    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.lg, vertical: MaatramSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Review & Submit',
            style: TextStyle(
              fontFamily: 'Georgia',
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'Please review your details before submitting.',
            style: TextStyle(
              fontSize: 13,
              color: Color(0xFF827D73),
              height: 1.35,
            ),
          ),
          const SizedBox(height: MaatramSpacing.xl),

          // Password Field
          MaatramTextField(
            label: 'Password *',
            hint: 'At least 8 characters',
            obscureText: _obscurePassword,
            initialValue: formState.password,
            errorText: formState.errors['password'],
            prefixIcon: const Icon(Icons.lock_outline,
                color: MaatramColors.charcoal500),
            suffixIcon: IconButton(
              icon: Icon(
                _obscurePassword
                    ? Icons.visibility_off_outlined
                    : Icons.visibility_outlined,
                color: MaatramColors.charcoal500,
              ),
              onPressed: () =>
                  setState(() => _obscurePassword = !_obscurePassword),
            ),
            onChanged: (val) => notifier.updateCredentials(password: val),
          ),
          const SizedBox(height: MaatramSpacing.md),

          // Confirm Password Field
          MaatramTextField(
            label: 'Confirm Password *',
            hint: 'Re-enter your password',
            obscureText: _obscureConfirm,
            initialValue: formState.confirmPassword,
            errorText: formState.errors['confirmPassword'],
            prefixIcon: const Icon(Icons.lock_outline,
                color: MaatramColors.charcoal500),
            suffixIcon: IconButton(
              icon: Icon(
                _obscureConfirm
                    ? Icons.visibility_off_outlined
                    : Icons.visibility_outlined,
                color: MaatramColors.charcoal500,
              ),
              onPressed: () =>
                  setState(() => _obscureConfirm = !_obscureConfirm),
            ),
            onChanged: (val) =>
                notifier.updateCredentials(confirmPassword: val),
          ),
          const SizedBox(height: MaatramSpacing.xl),

          // Summary Review Card
          Container(
            padding: const EdgeInsets.all(MaatramSpacing.lg),
            decoration: BoxDecoration(
              color: MaatramColors.white,
              borderRadius: MaatramRadii.cardRadius,
              border: Border.all(color: MaatramColors.warmBorder),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.04),
                  blurRadius: 10,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        'Application Summary',
                        style: MaatramTypography.titleMedium.copyWith(
                          color: MaatramColors.deepNavy,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(width: MaatramSpacing.sm),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color:
                            MaatramColors.primaryGold.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        formState.category,
                        style: MaatramTypography.caption.copyWith(
                          color: MaatramColors.deepNavy,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: MaatramSpacing.md),
                const Divider(color: MaatramColors.stone200),
                const SizedBox(height: MaatramSpacing.sm),
                _buildSummaryRow(
                    'Name', '${formState.firstName} ${formState.lastName}'),
                _buildSummaryRow('Email', formState.email),
                _buildSummaryRow('Mobile', formState.mobileNumber),
                _buildSummaryRow('Age / Gender',
                    '${formState.age ?? '-'} • ${formState.gender}'),
                if (formState.category == 'STUDENT') ...[
                  _buildSummaryRow('College', formState.studentCollegeName),
                  _buildSummaryRow('Program',
                      '${formState.studentDegree} (${formState.studentDepartment})'),
                  _buildSummaryRow(
                      'Current Year', 'Year ${formState.studentCurrentYear}'),
                ] else if (formState.category == 'ALUMNI') ...[
                  _buildSummaryRow('Alma Mater', formState.alumniCollegeName),
                  _buildSummaryRow('Company', formState.alumniOrganisation),
                  _buildSummaryRow('Role', formState.alumniJobRole),
                ] else ...[
                  _buildSummaryRow(
                      'Organisation', formState.corporateOrganisation),
                  _buildSummaryRow(
                      'Designation', formState.corporateDesignation),
                ],
                _buildSummaryRow('Availability', formState.availability),
                _buildSummaryRow(
                  'Selected Skills',
                  formState.selectedSkills.isEmpty
                      ? 'General Support'
                      : formState.selectedSkills.join(', '),
                ),
              ],
            ),
          ),

          const SizedBox(height: MaatramSpacing.lg),
          Container(
            padding: const EdgeInsets.all(MaatramSpacing.md),
            decoration: BoxDecoration(
              color: MaatramColors.primaryGold.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                  color: MaatramColors.primaryGold.withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                const Icon(Icons.verified_user_outlined,
                    color: MaatramColors.deepNavy, size: 22),
                const SizedBox(width: MaatramSpacing.sm),
                Expanded(
                  child: Text(
                    'Upon submission, an email verification token will be dispatched to confirm your address.',
                    style: MaatramTypography.bodySmall
                        .copyWith(color: MaatramColors.charcoal800),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 110,
            child: Text(
              label,
              style: MaatramTypography.caption
                  .copyWith(color: MaatramColors.charcoal500),
            ),
          ),
          Expanded(
            child: Text(
              value.isNotEmpty ? value : '-',
              style: MaatramTypography.bodySmall.copyWith(
                color: MaatramColors.charcoal900,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
