export 'volunteer_summary_card.dart';

import 'package:flutter/material.dart';
import '../../../../core/models/gamification_summary_model.dart';
import '../../../../core/models/volunteer_profile_model.dart';
import 'volunteer_summary_card.dart';

/// Backward-compatible alias for VolunteerSummaryCard
class VolunteerProfilePointsCard extends StatelessWidget {
  final VolunteerProfileModel? profile;
  final GamificationSummaryModel? gamification;
  final bool isLoading;
  final VoidCallback? onEditProfile;

  const VolunteerProfilePointsCard({
    super.key,
    this.profile,
    this.gamification,
    this.isLoading = false,
    this.onEditProfile,
  });

  @override
  Widget build(BuildContext context) {
    return VolunteerSummaryCard(
      profile: profile,
      gamification: gamification,
      isLoading: isLoading,
      onEditProfile: onEditProfile,
    );
  }
}
