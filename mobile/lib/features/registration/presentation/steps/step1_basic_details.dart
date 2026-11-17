import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/spacing.dart';
import '../../../../core/theme/typography.dart';
import '../../../../core/widgets/inputs/maatram_text_field.dart';
import '../../state/registration_state.dart';

class Step1BasicDetails extends ConsumerWidget {
  const Step1BasicDetails({super.key});

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
            'Basic Details',
            style: MaatramTypography.headlineMedium
                .copyWith(color: MaatramColors.deepNavy),
          ),
          const SizedBox(height: MaatramSpacing.xs),
          Text(
            'Tell us a little bit about yourself to begin your volunteer journey.',
            style: MaatramTypography.bodyMedium
                .copyWith(color: MaatramColors.secondaryText),
          ),
          const SizedBox(height: MaatramSpacing.xl),

          // First Name
          MaatramTextField(
            label: 'First Name *',
            hint: 'e.g. Anand',
            initialValue: formState.firstName,
            errorText: formState.errors['firstName'],
            autofillHints: const [AutofillHints.givenName],
            onChanged: (val) => notifier.updateBasicDetails(firstName: val),
          ),
          const SizedBox(height: MaatramSpacing.md),

          // Last Name
          MaatramTextField(
            label: 'Last Name *',
            hint: 'e.g. Kumar',
            initialValue: formState.lastName,
            errorText: formState.errors['lastName'],
            autofillHints: const [AutofillHints.familyName],
            onChanged: (val) => notifier.updateBasicDetails(lastName: val),
          ),
          const SizedBox(height: MaatramSpacing.md),

          // Email
          MaatramTextField(
            label: 'Email Address *',
            hint: 'e.g. anand.kumar@example.com',
            initialValue: formState.email,
            keyboardType: TextInputType.emailAddress,
            errorText: formState.errors['email'],
            autofillHints: const [AutofillHints.email],
            onChanged: (val) => notifier.updateBasicDetails(email: val),
          ),
          const SizedBox(height: MaatramSpacing.md),

          // Mobile Number with Country Code
          MaatramTextField(
            label: 'Mobile Number (with Country Code) *',
            hint: '+919876543210',
            initialValue: formState.mobileNumber,
            keyboardType: TextInputType.phone,
            errorText: formState.errors['mobileNumber'],
            autofillHints: const [AutofillHints.telephoneNumber],
            onChanged: (val) => notifier.updateBasicDetails(mobileNumber: val),
          ),
          const SizedBox(height: MaatramSpacing.md),

          // Age & Gender in a row
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                flex: 2,
                child: MaatramTextField(
                  label: 'Age *',
                  hint: '21',
                  initialValue:
                      formState.age != null ? formState.age.toString() : '',
                  keyboardType: TextInputType.number,
                  onChanged: (val) {
                    final parsed = int.tryParse(val);
                    if (parsed != null) {
                      notifier.updateBasicDetails(age: parsed);
                    }
                  },
                ),
              ),
              const SizedBox(width: MaatramSpacing.md),
              Expanded(
                flex: 3,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Gender',
                      style: MaatramTypography.labelLarge
                          .copyWith(color: MaatramColors.deepNavy),
                    ),
                    const SizedBox(height: MaatramSpacing.xs),
                    DropdownButtonFormField<String>(
                      isExpanded: true,
                      value: formState.gender,
                      decoration: InputDecoration(
                        contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide:
                              const BorderSide(color: MaatramColors.warmBorder),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide:
                              const BorderSide(color: MaatramColors.warmBorder),
                        ),
                      ),
                      items: const [
                        DropdownMenuItem(
                            value: 'PREFER_NOT_TO_SAY',
                            child: Text('Prefer not to say')),
                        DropdownMenuItem(value: 'MALE', child: Text('Male')),
                        DropdownMenuItem(
                            value: 'FEMALE', child: Text('Female')),
                        DropdownMenuItem(value: 'OTHER', child: Text('Other')),
                      ],
                      onChanged: (val) {
                        if (val != null) {
                          notifier.updateBasicDetails(gender: val);
                        }
                      },
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: MaatramSpacing.huge),
        ],
      ),
    );
  }
}
