import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/spacing.dart';
import '../../../../core/theme/typography.dart';
import '../../../../core/widgets/inputs/maatram_text_field.dart';
import '../../state/registration_state.dart';

class Step3CategoryDetails extends ConsumerWidget {
  const Step3CategoryDetails({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formState = ref.watch(registrationProvider);
    final notifier = ref.read(registrationProvider.notifier);

    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.symmetric(
          horizontal: MaatramSpacing.lg, vertical: MaatramSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            formState.category == 'STUDENT'
                ? 'Student Academic Details'
                : formState.category == 'ALUMNI'
                    ? 'Alumni & Professional Background'
                    : 'Corporate Panelist Profile',
            style: MaatramTypography.headlineMedium
                .copyWith(color: MaatramColors.deepNavy),
          ),
          const SizedBox(height: MaatramSpacing.xs),
          Text(
            formState.category == 'STUDENT'
                ? 'Please share details about your current educational institution.'
                : formState.category == 'ALUMNI'
                    ? 'Help us know your alma mater and current professional experience.'
                    : 'Share details of your corporate role and industry background.',
            style: MaatramTypography.bodyMedium
                .copyWith(color: MaatramColors.secondaryText),
          ),
          const SizedBox(height: MaatramSpacing.xl),

          // Render category-specific form fields
          if (formState.category == 'STUDENT') ...[
            // Student Fields
            MaatramTextField(
              label: 'College / University Name *',
              hint: 'e.g. Anna University, CEG Campus',
              initialValue: formState.studentCollegeName,
              errorText: formState.errors['studentCollegeName'],
              onChanged: (val) =>
                  notifier.updateStudentDetails(collegeName: val),
            ),
            const SizedBox(height: MaatramSpacing.md),

            Row(
              children: [
                Expanded(
                  flex: 3,
                  child: MaatramTextField(
                    label: 'Degree *',
                    hint: 'e.g. B.E / B.Tech',
                    initialValue: formState.studentDegree,
                    errorText: formState.errors['studentDegree'],
                    onChanged: (val) =>
                        notifier.updateStudentDetails(degree: val),
                  ),
                ),
                const SizedBox(width: MaatramSpacing.md),
                Expanded(
                  flex: 2,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Current Year *',
                        style: MaatramTypography.labelMedium
                            .copyWith(color: MaatramColors.charcoal800),
                      ),
                      const SizedBox(height: MaatramSpacing.xs),
                      DropdownButtonFormField<int>(
                        isExpanded: true,
                        value: formState.studentCurrentYear,
                        decoration: InputDecoration(
                          filled: true,
                          fillColor: MaatramColors.white,
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: MaatramSpacing.md,
                            vertical: MaatramSpacing.md,
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: const BorderSide(
                                color: MaatramColors.warmBorder),
                          ),
                        ),
                        items: const [
                          DropdownMenuItem(value: 1, child: Text('1st Year')),
                          DropdownMenuItem(value: 2, child: Text('2nd Year')),
                          DropdownMenuItem(value: 3, child: Text('3rd Year')),
                          DropdownMenuItem(value: 4, child: Text('4th Year')),
                          DropdownMenuItem(value: 5, child: Text('5th Year')),
                        ],
                        onChanged: (val) {
                          if (val != null) {
                            notifier.updateStudentDetails(currentYear: val);
                          }
                        },
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: MaatramSpacing.md),

            MaatramTextField(
              label: 'Department / Major *',
              hint: 'e.g. Computer Science and Engineering',
              initialValue: formState.studentDepartment,
              errorText: formState.errors['studentDepartment'],
              onChanged: (val) =>
                  notifier.updateStudentDetails(department: val),
            ),
            const SizedBox(height: MaatramSpacing.md),

            Row(
              children: [
                Expanded(
                  child: MaatramTextField(
                    label: 'Batch Year',
                    hint: 'e.g. 2024',
                    keyboardType: TextInputType.number,
                    initialValue: formState.studentBatchYear.toString(),
                    onChanged: (val) {
                      final parsed = int.tryParse(val);
                      if (parsed != null) {
                        notifier.updateStudentDetails(batchYear: parsed);
                      }
                    },
                  ),
                ),
                const SizedBox(width: MaatramSpacing.md),
                Expanded(
                  child: MaatramTextField(
                    label: 'Maatram Reg No (Optional)',
                    hint: 'e.g. MAT-24-301',
                    initialValue: formState.studentMaatramRegNo,
                    onChanged: (val) =>
                        notifier.updateStudentDetails(maatramRegNo: val),
                  ),
                ),
              ],
            ),
          ] else if (formState.category == 'ALUMNI') ...[
            // Alumni Fields
            MaatramTextField(
              label: 'Alma Mater / College Name *',
              hint: 'e.g. PSG College of Technology',
              initialValue: formState.alumniCollegeName,
              errorText: formState.errors['alumniCollegeName'],
              onChanged: (val) =>
                  notifier.updateAlumniDetails(collegeName: val),
            ),
            const SizedBox(height: MaatramSpacing.md),

            Row(
              children: [
                Expanded(
                  child: MaatramTextField(
                    label: 'Degree',
                    hint: 'e.g. B.Tech / M.Sc',
                    initialValue: formState.alumniDegree,
                    onChanged: (val) =>
                        notifier.updateAlumniDetails(degree: val),
                  ),
                ),
                const SizedBox(width: MaatramSpacing.md),
                Expanded(
                  child: MaatramTextField(
                    label: 'Graduation Year',
                    hint: 'e.g. 2022',
                    keyboardType: TextInputType.number,
                    initialValue: formState.alumniGraduationYear.toString(),
                    onChanged: (val) {
                      final parsed = int.tryParse(val);
                      if (parsed != null) {
                        notifier.updateAlumniDetails(graduationYear: parsed);
                      }
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: MaatramSpacing.md),

            MaatramTextField(
              label: 'Current Organisation / Company *',
              hint: 'e.g. Infosys, TCS, Zoho, Self-employed',
              initialValue: formState.alumniOrganisation,
              errorText: formState.errors['alumniOrganisation'],
              onChanged: (val) =>
                  notifier.updateAlumniDetails(organisation: val),
            ),
            const SizedBox(height: MaatramSpacing.md),

            Row(
              children: [
                Expanded(
                  flex: 3,
                  child: MaatramTextField(
                    label: 'Job Role / Title',
                    hint: 'e.g. Senior Software Engineer',
                    initialValue: formState.alumniJobRole,
                    onChanged: (val) =>
                        notifier.updateAlumniDetails(jobRole: val),
                  ),
                ),
                const SizedBox(width: MaatramSpacing.md),
                Expanded(
                  flex: 2,
                  child: MaatramTextField(
                    label: 'Years Exp',
                    hint: 'e.g. 3.5',
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                    initialValue: formState.alumniYearsOfExp.toString(),
                    onChanged: (val) {
                      final parsed = double.tryParse(val);
                      if (parsed != null) {
                        notifier.updateAlumniDetails(yearsOfExp: parsed);
                      }
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: MaatramSpacing.md),

            MaatramTextField(
              label: 'Location / City',
              hint: 'e.g. Chennai, Bengaluru, Coimbatore',
              initialValue: formState.alumniLocation,
              onChanged: (val) => notifier.updateAlumniDetails(location: val),
            ),
          ] else ...[
            // Corporate Panelist Fields
            MaatramTextField(
              label: 'Organisation / Company Name *',
              hint: 'e.g. Google, Microsoft, L&T, Tata Sons',
              initialValue: formState.corporateOrganisation,
              errorText: formState.errors['corporateOrganisation'],
              onChanged: (val) =>
                  notifier.updateCorporateDetails(organisation: val),
            ),
            const SizedBox(height: MaatramSpacing.md),

            MaatramTextField(
              label: 'Designation / Title *',
              hint: 'e.g. Vice President, HR Director, Staff Engineer',
              initialValue: formState.corporateDesignation,
              errorText: formState.errors['corporateDesignation'],
              onChanged: (val) =>
                  notifier.updateCorporateDetails(designation: val),
            ),
            const SizedBox(height: MaatramSpacing.md),

            Row(
              children: [
                Expanded(
                  child: MaatramTextField(
                    label: 'Years of Experience',
                    hint: 'e.g. 8.0',
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                    initialValue: formState.corporateYearsOfExp.toString(),
                    onChanged: (val) {
                      final parsed = double.tryParse(val);
                      if (parsed != null) {
                        notifier.updateCorporateDetails(yearsOfExp: parsed);
                      }
                    },
                  ),
                ),
                const SizedBox(width: MaatramSpacing.md),
                Expanded(
                  child: MaatramTextField(
                    label: 'Location / City',
                    hint: 'e.g. Chennai',
                    initialValue: formState.corporateLocation,
                    onChanged: (val) =>
                        notifier.updateCorporateDetails(location: val),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
