import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/layout/organic_background.dart';

class HelpSupportScreen extends StatelessWidget {
  const HelpSupportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final faqs = [
      {
        'q': 'How are my volunteering hours verified?',
        'a':
            'After an event concludes, the assigned Event Coordinator logs attendance check-in and check-out timestamps. Verified hours are credited directly to your profile upon batch approval.',
      },
      {
        'q': 'How are Karma Points calculated?',
        'a':
            'Points follow the canonical formula: Points = (Events × 10) + (Hours × 2). Completing events awards 10 points per event plus 2 points for each verified hour.',
      },
      {
        'q': 'Can I withdraw from a confirmed event?',
        'a':
            'Yes, you can withdraw through the My Activity tab prior to the event start deadline. Early withdrawals allow waitlisted volunteers to fill available slots.',
      },
      {
        'q': 'How do I update my profile or institution?',
        'a':
            'You can edit contact information, city, and bio in Edit Profile. For legal name or category changes, please contact foundation administrators.',
      },
    ];

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
            'Help & Support',
            style: MaatramTypography.headlineMedium.copyWith(
              fontFamily: 'Georgia',
              fontWeight: FontWeight.bold,
              color: MaatramColors.deepNavy,
            ),
          ),
        ),
        body: ListView(
          padding: const EdgeInsets.all(MaatramSpacing.md),
          children: [
            // Contact Support Card (Configurable, No unverified phone numbers)
            Container(
              padding: const EdgeInsets.all(MaatramSpacing.lg),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFFFFBEB), Color(0xFFFEF3C7)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                    color: MaatramColors.primaryGold.withValues(alpha: 0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: const BoxDecoration(
                          color: MaatramColors.primaryGold,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.headset_mic_rounded,
                            color: MaatramColors.deepNavy, size: 24),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Coordinator Support',
                              style: MaatramTypography.titleSmall.copyWith(
                                fontWeight: FontWeight.bold,
                                color: MaatramColors.deepNavy,
                              ),
                            ),
                            Text(
                              'Have questions about upcoming events or your application?',
                              style: MaatramTypography.bodySmall.copyWith(
                                color: MaatramColors.secondaryText,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  MaatramButton(
                    label: 'Email Support Team',
                    leadingIcon:
                        const Icon(Icons.mail_outline_rounded, size: 18),
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text(
                              'Opening support correspondence composer...'),
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.lg),

            Text(
              'Frequently Asked Questions',
              style: MaatramTypography.titleMedium.copyWith(
                fontFamily: 'Georgia',
                fontWeight: FontWeight.bold,
                color: MaatramColors.deepNavy,
              ),
            ),
            const SizedBox(height: 10),

            // FAQ Expansion Tiles
            Material(
              color: Colors.white,
              clipBehavior: Clip.antiAlias,
              shape: RoundedRectangleBorder(
                borderRadius: MaatramRadii.cardRadius,
                side: const BorderSide(color: MaatramColors.warmBorder),
              ),
              child: Column(
                children: faqs.asMap().entries.map((entry) {
                  final index = entry.key;
                  final item = entry.value;
                  return Column(
                    children: [
                      if (index > 0)
                        const Divider(
                            height: 1, color: MaatramColors.warmBorder),
                      Theme(
                        data: Theme.of(context)
                            .copyWith(dividerColor: Colors.transparent),
                        child: ExpansionTile(
                          iconColor: MaatramColors.deepNavy,
                          collapsedIconColor: MaatramColors.secondaryText,
                          title: Text(
                            item['q']!,
                            style: const TextStyle(
                              fontFamily: 'Roboto',
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: MaatramColors.deepNavy,
                            ),
                          ),
                          children: [
                            Padding(
                              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                              child: Text(
                                item['a']!,
                                style: MaatramTypography.bodySmall.copyWith(
                                  color: MaatramColors.secondaryText,
                                  height: 1.4,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                }).toList(),
              ),
            ),
            const SizedBox(height: MaatramSpacing.lg),
          ],
        ),
      ),
    );
  }
}
