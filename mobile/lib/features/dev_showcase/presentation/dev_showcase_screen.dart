import 'package:flutter/material.dart';
import '../../../core/animations/animated_counter.dart';
import '../../../core/animations/animated_progress.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/badges/category_badge.dart';
import '../../../core/widgets/badges/points_badge.dart';
import '../../../core/widgets/badges/status_badge.dart';
import '../../../core/widgets/buttons/maatram_button.dart';
import '../../../core/widgets/cards/maatram_card.dart';
import '../../../core/widgets/cards/maatram_event_card.dart';
import '../../../core/widgets/cards/maatram_stat_card.dart';
import '../../../core/widgets/feedback/bottom_sheet.dart';
import '../../../core/widgets/feedback/empty_state.dart';
import '../../../core/widgets/feedback/error_state.dart';
import '../../../core/widgets/feedback/skeleton_loader.dart';
import '../../../core/widgets/inputs/maatram_search_field.dart';
import '../../../core/widgets/inputs/maatram_text_field.dart';
import '../../../core/widgets/layout/organic_background.dart';
import '../../../core/widgets/navigation/section_header.dart';

/// Developer-facing Design Showcase route demonstrating all M1 foundation tokens,
/// components, motion primitives, and application states.
class DevShowcaseScreen extends StatefulWidget {
  const DevShowcaseScreen({super.key});

  @override
  State<DevShowcaseScreen> createState() => _DevShowcaseScreenState();
}

class _DevShowcaseScreenState extends State<DevShowcaseScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  final TextEditingController _textController = TextEditingController(text: 'Sneha Raman');
  final TextEditingController _searchController = TextEditingController();
  double _progressVal = 0.65;
  int _counterVal = 193;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 6, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _textController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaatramOrganicBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: MaatramColors.white,
          elevation: 0,
          title: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Design Showcase', style: MaatramTypography.headlineMedium),
              Text(
                'M1 Foundation, Tokens, Components & Motion',
                style: MaatramTypography.bodySmall,
              ),
            ],
          ),
          bottom: TabBar(
            controller: _tabController,
            isScrollable: true,
            labelColor: MaatramColors.deepNavy,
            unselectedLabelColor: MaatramColors.secondaryText,
            indicatorColor: MaatramColors.primaryGold,
            indicatorWeight: 3.0,
            labelStyle: MaatramTypography.labelSmall,
            tabAlignment: TabAlignment.start,
            tabs: const [
              Tab(text: 'Tokens & Palette'),
              Tab(text: 'Typography'),
              Tab(text: 'Buttons & Inputs'),
              Tab(text: 'Cards & Badges'),
              Tab(text: 'States & Skeletons'),
              Tab(text: 'Motion Primitives'),
            ],
          ),
        ),
        body: TabBarView(
          controller: _tabController,
          children: [
            _buildPaletteTab(),
            _buildTypographyTab(),
            _buildControlsTab(),
            _buildCardsAndBadgesTab(),
            _buildStatesTab(),
            _buildMotionTab(),
          ],
        ),
      ),
    );
  }

  // 1. PALETTE TAB
  Widget _buildPaletteTab() {
    return ListView(
      padding: MaatramSpacing.screenPadding,
      children: [
        const MaatramSectionHeader(
          title: 'Brand Initial Tokens',
          subtitle: 'Locked tokens forming the warm ivory editorial identity',
        ),
        _buildColorTile('Background (Ivory)', '#FAF8F5', MaatramColors.background),
        _buildColorTile('Primary Gold', '#F5B817', MaatramColors.primaryGold),
        _buildColorTile('Deep Navy (Typography)', '#1B2B48', MaatramColors.deepNavy),
        _buildColorTile('Card Surface (White)', '#FFFFFF', MaatramColors.white),
        _buildColorTile('Warm Border', '#EFECE6', MaatramColors.warmBorder),
        _buildColorTile('Secondary Text', '#827D73', MaatramColors.secondaryText),
        const SizedBox(height: MaatramSpacing.lg),
        const MaatramSectionHeader(
          title: 'Semantic & Category Tokens',
          subtitle: 'Status highlights, success emerald, and volunteer categories',
        ),
        _buildColorTile('Success Emerald', '#10B981', MaatramColors.success),
        _buildColorTile('Warning Amber', '#F59E0B', MaatramColors.warning),
        _buildColorTile('Error Rose', '#EF4444', MaatramColors.error),
        _buildColorTile('Student Category', '#2563EB', MaatramColors.categoryStudent),
        _buildColorTile('Alumni Category', '#7C3AED', MaatramColors.categoryAlumni),
        _buildColorTile('Corporate Category', '#D97706', MaatramColors.categoryCorporate),
      ],
    );
  }

  Widget _buildColorTile(String label, String hex, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: MaatramSpacing.sm),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: MaatramSpacing.md, vertical: MaatramSpacing.sm),
        decoration: BoxDecoration(
          color: MaatramColors.white,
          borderRadius: MaatramRadii.radiusMd,
          border: Border.all(color: MaatramColors.warmBorder),
        ),
        child: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: color,
                borderRadius: MaatramRadii.radiusSm,
                border: Border.all(color: MaatramColors.warmBorder),
              ),
            ),
            const SizedBox(width: MaatramSpacing.md),
            Expanded(
              child: Text(label, style: MaatramTypography.titleSmall),
            ),
            Text(hex, style: MaatramTypography.labelSmall.copyWith(color: MaatramColors.secondaryText)),
          ],
        ),
      ),
    );
  }

  // 2. TYPOGRAPHY TAB
  Widget _buildTypographyTab() {
    return ListView(
      padding: MaatramSpacing.screenPadding,
      children: const [
        MaatramSectionHeader(
          title: 'Editorial Display & Headings',
          subtitle: 'Georgia serif family delivering distinguished brand presence',
        ),
        MaatramCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Display Large 32pt', style: MaatramTypography.displayLarge),
              SizedBox(height: MaatramSpacing.sm),
              Text('Display Medium 26pt', style: MaatramTypography.displayMedium),
              SizedBox(height: MaatramSpacing.sm),
              Text('Display Small 22pt', style: MaatramTypography.displaySmall),
              SizedBox(height: MaatramSpacing.sm),
              Text('Headline Medium 20pt', style: MaatramTypography.headlineMedium),
            ],
          ),
        ),
        SizedBox(height: MaatramSpacing.lg),
        MaatramSectionHeader(
          title: 'Modern Sans Body & Labels',
          subtitle: 'Clean legible hierarchy for event descriptions and attributes',
        ),
        MaatramCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Title Large (16pt Bold)', style: MaatramTypography.titleLarge),
              SizedBox(height: MaatramSpacing.xs),
              Text('Title Medium (15pt Semi)', style: MaatramTypography.titleMedium),
              SizedBox(height: MaatramSpacing.xs),
              Text('Title Small (13pt Semi)', style: MaatramTypography.titleSmall),
              SizedBox(height: MaatramSpacing.md),
              Text(
                'Body Large (15pt): Maatram Foundation connects dedicated volunteers with rural school education and student career guidance.',
                style: MaatramTypography.bodyLarge,
              ),
              SizedBox(height: MaatramSpacing.xs),
              Text(
                'Body Medium (14pt): Attendance verification is recorded via GPS geolocation and validated by volunteer coordinators.',
                style: MaatramTypography.bodyMedium,
              ),
              SizedBox(height: MaatramSpacing.xs),
              Text(
                'Body Small (12pt): Formula P = 10E + 2H awards 10 points per event plus 2 points per completed hour.',
                style: MaatramTypography.bodySmall,
              ),
            ],
          ),
        ),
      ],
    );
  }

  // 3. CONTROLS TAB
  Widget _buildControlsTab() {
    return ListView(
      padding: MaatramSpacing.screenPadding,
      children: [
        const MaatramSectionHeader(title: 'Button Variants', subtitle: 'Primary gold, deep navy secondary, outline & danger'),
        MaatramCard(
          child: Column(
            children: [
              MaatramButton(
                label: 'Primary Button',
                isFullWidth: true,
                onPressed: () {},
              ),
              const SizedBox(height: MaatramSpacing.sm),
              MaatramButton(
                label: 'Secondary Button',
                variant: MaatramButtonVariant.secondary,
                isFullWidth: true,
                onPressed: () {},
              ),
              const SizedBox(height: MaatramSpacing.sm),
              MaatramButton(
                label: 'Outline Button',
                variant: MaatramButtonVariant.outline,
                isFullWidth: true,
                onPressed: () {},
              ),
              const SizedBox(height: MaatramSpacing.sm),
              MaatramButton(
                label: 'Danger Action',
                variant: MaatramButtonVariant.danger,
                size: MaatramButtonSize.sm,
                onPressed: () {},
              ),
              const SizedBox(height: MaatramSpacing.sm),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  MaatramButton(label: 'Small', size: MaatramButtonSize.sm),
                  MaatramButton(label: 'Medium', size: MaatramButtonSize.md),
                  MaatramButton(label: 'Loading', isLoading: true),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: MaatramSpacing.lg),
        const MaatramSectionHeader(title: 'Inputs & Search', subtitle: 'Floating field labels, gold focus states and clearable search'),
        MaatramCard(
          child: Column(
            children: [
              MaatramTextField(
                controller: _textController,
                label: 'Volunteer Full Name',
                hintText: 'Enter your legal name',
                prefixIcon: const Icon(Icons.person_outline, size: 20),
              ),
              const SizedBox(height: MaatramSpacing.md),
              const MaatramTextField(
                label: 'Email Address',
                hintText: 'volunteer@maatram.org',
                prefixIcon: Icon(Icons.mail_outline, size: 20),
                helperText: 'Verification link will be dispatched to this mailbox',
              ),
              const SizedBox(height: MaatramSpacing.md),
              const MaatramTextField(
                label: 'Validation Demo',
                hintText: 'Required field',
                errorText: 'This field cannot be left blank.',
              ),
              const SizedBox(height: MaatramSpacing.md),
              MaatramSearchField(
                controller: _searchController,
                hintText: 'Search mock interviews, webinars...',
              ),
            ],
          ),
        ),
      ],
    );
  }

  // 4. CARDS & BADGES TAB
  Widget _buildCardsAndBadgesTab() {
    return ListView(
      padding: MaatramSpacing.screenPadding,
      children: [
        const MaatramSectionHeader(title: 'Category & Status Badges'),
        const MaatramCard(
          child: Wrap(
            spacing: MaatramSpacing.sm,
            runSpacing: MaatramSpacing.sm,
            children: [
              MaatramCategoryBadge(category: VolunteerCategory.student),
              MaatramCategoryBadge(category: VolunteerCategory.alumni),
              MaatramCategoryBadge(category: VolunteerCategory.corporate),
              MaatramStatusBadge(status: MaatramStatus.approved),
              MaatramStatusBadge(status: MaatramStatus.pending),
              MaatramStatusBadge(status: MaatramStatus.live),
              MaatramStatusBadge(status: MaatramStatus.completed),
              MaatramPointsBadge(points: 10),
              MaatramPointsBadge(points: 25, isLarge: true),
            ],
          ),
        ),
        const SizedBox(height: MaatramSpacing.lg),
        const MaatramSectionHeader(title: 'Statistic Summary Cards'),
        Row(
          children: [
            Expanded(
              child: MaatramStatCard(
                label: 'Events Count',
                value: 12,
                icon: Icons.event_available_outlined,
                iconColor: MaatramColors.infoDark,
                iconBackgroundColor: MaatramColors.infoLight,
              ),
            ),
            const SizedBox(width: MaatramSpacing.md),
            Expanded(
              child: MaatramStatCard(
                label: 'Points Earned',
                value: 193,
                icon: Icons.stars_rounded,
                iconColor: MaatramColors.goldDark,
                iconBackgroundColor: MaatramColors.goldSurface,
              ),
            ),
          ],
        ),
        const SizedBox(height: MaatramSpacing.lg),
        const MaatramSectionHeader(title: 'Event Primitive Card'),
        const MaatramEventCard(
          title: 'Mock Interview & Aptitude Mentorship 2026',
          category: VolunteerCategory.student,
          dateText: 'Sat, Nov 22',
          timeText: '09:30 AM',
          locationText: 'Chennai Tech Park',
          points: 10,
          status: MaatramStatus.approved,
        ),
      ],
    );
  }

  // 5. STATES & SKELETONS TAB
  Widget _buildStatesTab() {
    return ListView(
      padding: MaatramSpacing.screenPadding,
      children: [
        const MaatramSectionHeader(title: 'Loading Shimmer Skeletons'),
        const MaatramEventCardSkeleton(),
        const SizedBox(height: MaatramSpacing.md),
        const Row(
          children: [
            Expanded(child: MaatramStatCardSkeleton()),
            SizedBox(width: MaatramSpacing.md),
            Expanded(child: MaatramStatCardSkeleton()),
          ],
        ),
        const SizedBox(height: MaatramSpacing.lg),
        const MaatramSectionHeader(title: 'Empty State Component'),
        const MaatramCard(
          padding: EdgeInsets.zero,
          child: MaatramEmptyState(
            title: 'No Upcoming Events Found',
            description: 'You are all caught up! New volunteering drives will appear here once published by coordinators.',
            actionLabel: 'Refresh Roster',
          ),
        ),
        const SizedBox(height: MaatramSpacing.lg),
        const MaatramSectionHeader(title: 'Error State Component'),
        MaatramCard(
          padding: EdgeInsets.zero,
          child: MaatramErrorState(
            message: 'Unable to reach the server. Please check your internet connection and retry.',
            onRetry: () {},
          ),
        ),
      ],
    );
  }

  // 6. MOTION TAB
  Widget _buildMotionTab() {
    return ListView(
      padding: MaatramSpacing.screenPadding,
      children: [
        const MaatramSectionHeader(
          title: 'Animated Counter & Numbers',
          subtitle: 'Smooth easing rolling numbers for gamification and ranks',
        ),
        MaatramCard(
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  MaatramAnimatedCounter(value: _counterVal, suffix: ' pts'),
                  MaatramAnimatedCounter(value: 8, prefix: '#', style: MaatramTypography.displayLarge),
                ],
              ),
              const SizedBox(height: MaatramSpacing.md),
              MaatramButton(
                label: 'Trigger Counter Increment (+15 pts)',
                size: MaatramButtonSize.sm,
                onPressed: () {
                  setState(() => _counterVal += 15);
                },
              ),
            ],
          ),
        ),
        const SizedBox(height: MaatramSpacing.lg),
        const MaatramSectionHeader(
          title: 'Animated Progress Bar',
          subtitle: 'Organic smoothed indicator for milestone and tier goals',
        ),
        MaatramCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Tier Progress: ${(_progressVal * 100).toInt()}% towards Gold Badge',
                style: MaatramTypography.bodySmall,
              ),
              const SizedBox(height: MaatramSpacing.sm),
              MaatramAnimatedProgress(progress: _progressVal, height: 10),
              const SizedBox(height: MaatramSpacing.md),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  MaatramButton(
                    label: '25%',
                    size: MaatramButtonSize.sm,
                    variant: MaatramButtonVariant.outline,
                    onPressed: () => setState(() => _progressVal = 0.25),
                  ),
                  MaatramButton(
                    label: '65%',
                    size: MaatramButtonSize.sm,
                    variant: MaatramButtonVariant.outline,
                    onPressed: () => setState(() => _progressVal = 0.65),
                  ),
                  MaatramButton(
                    label: '100%',
                    size: MaatramButtonSize.sm,
                    variant: MaatramButtonVariant.outline,
                    onPressed: () => setState(() => _progressVal = 1.0),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: MaatramSpacing.lg),
        const MaatramSectionHeader(
          title: 'Interactive Bottom Sheet Prompt',
          subtitle: 'Curved presentation with drag handle and dual actions',
        ),
        MaatramButton(
          label: 'Show Confirmation Bottom Sheet',
          variant: MaatramButtonVariant.secondary,
          isFullWidth: true,
          onPressed: () {
            MaatramBottomSheet.showConfirmation(
              context: context,
              title: 'Confirm Event Sign-up',
              message: 'Are you sure you want to register for Mock Interview Mentorship 2026? A confirmation notification will be enqueued.',
              confirmLabel: 'Register Now',
            );
          },
        ),
      ],
    );
  }
}
