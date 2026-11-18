export 'welcome_banner.dart';

import 'package:flutter/material.dart';
import 'welcome_banner.dart';

/// Backward-compatible alias for WelcomeBanner
class IllustratedWelcomeBanner extends StatelessWidget {
  final String volunteerName;
  final bool isLoading;

  const IllustratedWelcomeBanner({
    super.key,
    required this.volunteerName,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return WelcomeBanner(
      volunteerName: volunteerName,
      isLoading: isLoading,
    );
  }
}
