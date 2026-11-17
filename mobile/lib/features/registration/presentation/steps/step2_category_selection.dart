import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/colors.dart';
import '../../../../core/theme/spacing.dart';
import '../../../../core/theme/typography.dart';
import '../../state/registration_state.dart';
import '../widgets/category_card.dart';

class Step2CategorySelection extends ConsumerWidget {
  const Step2CategorySelection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final registrationState = ref.watch(registrationNotifierProvider);
    final notifier = ref.read(registrationNotifierProvider.notifier);
    final selectedCategory = registrationState.category;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(MaatramSpacing.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Select Category',
            style: MaatramTypography.headlineMedium.copyWith(
              color: MaatramColors.deepNavy,
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: MaatramSpacing.xs),
          Text(
            'Choose the category that best describes you.',
            style: MaatramTypography.bodyMedium.copyWith(
              color: MaatramColors.secondaryText,
            ),
          ),
          const SizedBox(height: MaatramSpacing.xl),

          // 1. Student
          CategorySelectionCard(
            title: 'Student',
            description:
                'Currently enrolled in college or university, eager to participate in ground events and develop skills.',
            icon: Icons.school_rounded,
            accentColor: const Color(0xFF2563EB),
            isSelected: selectedCategory == 'STUDENT',
            onTap: () => notifier.setCategory('STUDENT'),
          ),

          // 2. Alumni
          CategorySelectionCard(
            title: 'Alumni',
            description:
                'Graduated alumni ready to guide students, share industry experience, and give back.',
            icon: Icons.workspace_premium_rounded,
            accentColor: const Color(0xFF7C3AED),
            isSelected: selectedCategory == 'ALUMNI',
            onTap: () => notifier.setCategory('ALUMNI'),
          ),

          // 3. Corporate Panelist
          CategorySelectionCard(
            title: 'Corporate Panelist',
            description:
                'Working professional participating in scholarship interviews, panel evaluations, and mentoring.',
            icon: Icons.business_center_rounded,
            accentColor: const Color(0xFFD97706),
            isSelected: selectedCategory == 'CORPORATE',
            onTap: () => notifier.setCategory('CORPORATE'),
          ),
        ],
      ),
    );
  }
}
