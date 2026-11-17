import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/spacing.dart';
import '../../../../core/theme/typography.dart';
import '../../state/registration_state.dart';

class Step4SkillsAvailability extends ConsumerWidget {
  const Step4SkillsAvailability({super.key});

  static const List<String> availableSkills = [
    'Mentoring',
    'Communication',
    'Event Support',
    'Content',
    'School Visits',
    'Mock Interviews',
    'Career Guidance',
    'Event Coordination',
    'Public Speaking',
    'Technical Training',
    'Panel Review',
    'Documentation',
    'Photography & Media',
    'Logistics & Operations',
  ];

  static const List<String> availabilityOptions = [
    'Weekends',
    'Weekdays & Weekends',
    'Flexible / On-call',
    'Evenings',
  ];

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
            'Skills & Availability',
            style: MaatramTypography.headlineMedium
                .copyWith(color: MaatramColors.deepNavy),
          ),
          const SizedBox(height: MaatramSpacing.xs),
          Text(
            'Select your areas of interest and how you would like to contribute.',
            style: MaatramTypography.bodyMedium
                .copyWith(color: MaatramColors.secondaryText),
          ),
          const SizedBox(height: MaatramSpacing.xl),
          Text(
            'Areas of Interest / Skills',
            style: MaatramTypography.labelLarge
                .copyWith(color: MaatramColors.charcoal900),
          ),
          const SizedBox(height: MaatramSpacing.xs),
          Text(
            'Choose all that match your strengths (tap to select):',
            style: MaatramTypography.caption
                .copyWith(color: MaatramColors.charcoal600),
          ),
          const SizedBox(height: MaatramSpacing.md),
          Wrap(
            spacing: MaatramSpacing.sm,
            runSpacing: MaatramSpacing.sm,
            children: availableSkills.map((skill) {
              final isSelected = formState.selectedSkills.contains(skill);
              return FilterChip(
                label: Text(skill),
                selected: isSelected,
                selectedColor:
                    MaatramColors.primaryGold.withValues(alpha: 0.25),
                backgroundColor: MaatramColors.stone100,
                checkmarkColor: MaatramColors.deepNavy,
                labelStyle: MaatramTypography.bodySmall.copyWith(
                  color: isSelected
                      ? MaatramColors.deepNavy
                      : MaatramColors.charcoal800,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                  side: BorderSide(
                    color: isSelected
                        ? MaatramColors.primaryGold
                        : MaatramColors.warmBorder,
                  ),
                ),
                onSelected: (selected) {
                  final current = List<String>.from(formState.selectedSkills);
                  if (selected) {
                    current.add(skill);
                  } else {
                    current.remove(skill);
                  }
                  notifier.updateSkillsAndAvailability(skills: current);
                },
              );
            }).toList(),
          ),
          const SizedBox(height: MaatramSpacing.xxl),
          Text(
            'General Availability',
            style: MaatramTypography.labelLarge
                .copyWith(color: MaatramColors.charcoal900),
          ),
          const SizedBox(height: MaatramSpacing.xs),
          Text(
            'When are you most available for volunteering events and initiatives?',
            style: MaatramTypography.caption
                .copyWith(color: MaatramColors.charcoal600),
          ),
          const SizedBox(height: MaatramSpacing.md),
          Column(
            children: availabilityOptions.map((opt) {
              final isSelected = formState.availability == opt;
              return Container(
                margin: const EdgeInsets.only(bottom: MaatramSpacing.sm),
                child: Material(
                  color: isSelected
                      ? MaatramColors.primaryGold.withValues(alpha: 0.1)
                      : MaatramColors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(
                      color: isSelected
                          ? MaatramColors.primaryGold
                          : MaatramColors.warmBorder,
                      width: isSelected ? 1.5 : 1.0,
                    ),
                  ),
                  child: RadioListTile<String>(
                    title: Text(
                      opt,
                      style: MaatramTypography.bodyMedium.copyWith(
                        color: MaatramColors.charcoal900,
                        fontWeight:
                            isSelected ? FontWeight.w600 : FontWeight.normal,
                      ),
                    ),
                    value: opt,
                    groupValue: formState.availability,
                    activeColor: MaatramColors.primaryGold,
                    onChanged: (val) {
                      if (val != null) {
                        notifier.updateSkillsAndAvailability(availability: val);
                      }
                    },
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}
