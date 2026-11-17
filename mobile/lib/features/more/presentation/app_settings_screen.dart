import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../app/router/route_names.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/layout/organic_background.dart';

class AppSettingsScreen extends StatefulWidget {
  const AppSettingsScreen({super.key});

  @override
  State<AppSettingsScreen> createState() => _AppSettingsScreenState();
}

class _AppSettingsScreenState extends State<AppSettingsScreen> {
  bool _biometricsEnabled = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _biometricsEnabled = prefs.getBool('pref_biometrics_enabled') ?? false;
    });
  }

  Future<void> _toggleBiometrics(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('pref_biometrics_enabled', value);
    setState(() => _biometricsEnabled = value);
  }

  @override
  Widget build(BuildContext context) {
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
            'Settings',
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
            // Preferences Group
            Material(
              color: Colors.white,
              clipBehavior: Clip.antiAlias,
              shape: RoundedRectangleBorder(
                borderRadius: MaatramRadii.cardRadius,
                side: const BorderSide(color: MaatramColors.warmBorder),
              ),
              child: Column(
                children: [
                  SwitchListTile(
                    value: _biometricsEnabled,
                    activeColor: MaatramColors.primaryGold,
                    secondary: const Icon(Icons.fingerprint_rounded,
                        color: MaatramColors.deepNavy),
                    title: const Text('Biometric Authentication',
                        style: TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 14,
                            fontWeight: FontWeight.w600)),
                    subtitle: const Text(
                        'Unlock app using fingerprint or face ID',
                        style: TextStyle(
                            fontSize: 12, color: MaatramColors.secondaryText)),
                    onChanged: _toggleBiometrics,
                  ),
                  const Divider(height: 1, color: MaatramColors.warmBorder),
                  ListTile(
                    leading: const Icon(Icons.notifications_outlined,
                        color: MaatramColors.deepNavy),
                    title: const Text('Notification Preferences',
                        style: TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 14,
                            fontWeight: FontWeight.w600)),
                    subtitle: const Text('Configure device-local push triggers',
                        style: TextStyle(
                            fontSize: 12, color: MaatramColors.secondaryText)),
                    trailing: const Icon(Icons.chevron_right_rounded,
                        color: MaatramColors.secondaryText),
                    onTap: () =>
                        context.push(RouteNames.notificationSettingsPath),
                  ),
                  const Divider(height: 1, color: MaatramColors.warmBorder),
                  ListTile(
                    leading: const Icon(Icons.privacy_tip_outlined,
                        color: MaatramColors.deepNavy),
                    title: const Text('Privacy & Consent Governance',
                        style: TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 14,
                            fontWeight: FontWeight.w600)),
                    subtitle: const Text(
                        'Manage statutory directory and leaderboard visibility',
                        style: TextStyle(
                            fontSize: 12, color: MaatramColors.secondaryText)),
                    trailing: const Icon(Icons.chevron_right_rounded,
                        color: MaatramColors.secondaryText),
                    onTap: () => context.push(RouteNames.privacyPath),
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.md),

            // About & System Info Card
            Material(
              color: Colors.white,
              clipBehavior: Clip.antiAlias,
              shape: RoundedRectangleBorder(
                borderRadius: MaatramRadii.cardRadius,
                side: const BorderSide(color: MaatramColors.warmBorder),
              ),
              child: Column(
                children: [
                  ListTile(
                    leading: const Icon(Icons.info_outline_rounded,
                        color: MaatramColors.deepNavy),
                    title: const Text('About Maatram Foundation',
                        style: TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 14,
                            fontWeight: FontWeight.w600)),
                    trailing: const Icon(Icons.chevron_right_rounded,
                        color: MaatramColors.secondaryText),
                    onTap: () => context.push(RouteNames.aboutMaatramPath),
                  ),
                  const Divider(height: 1, color: MaatramColors.warmBorder),
                  ListTile(
                    leading: const Icon(Icons.help_outline_rounded,
                        color: MaatramColors.deepNavy),
                    title: const Text('Help & Support',
                        style: TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 14,
                            fontWeight: FontWeight.w600)),
                    trailing: const Icon(Icons.chevron_right_rounded,
                        color: MaatramColors.secondaryText),
                    onTap: () => context.push(RouteNames.helpSupportPath),
                  ),
                  const Divider(height: 1, color: MaatramColors.warmBorder),
                  Padding(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 14),
                    child: Row(
                      children: [
                        const Icon(Icons.verified_outlined,
                            color: MaatramColors.secondaryText, size: 22),
                        const SizedBox(width: 14),
                        const Expanded(
                          child: Text(
                            'Application Version',
                            style: TextStyle(
                                fontFamily: 'Roboto',
                                fontSize: 14,
                                fontWeight: FontWeight.w600),
                          ),
                        ),
                        const Text(
                          '1.0.0 (Phase 13)',
                          style: TextStyle(
                            fontSize: 12,
                            color: MaatramColors.secondaryText,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
