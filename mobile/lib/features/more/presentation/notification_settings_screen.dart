import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/theme/colors.dart';
import '../../../core/theme/radii.dart';
import '../../../core/theme/spacing.dart';
import '../../../core/theme/typography.dart';
import '../../../core/widgets/layout/organic_background.dart';

class NotificationSettingsScreen extends StatefulWidget {
  const NotificationSettingsScreen({super.key});

  @override
  State<NotificationSettingsScreen> createState() =>
      _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState
    extends State<NotificationSettingsScreen> {
  bool _eventReminders = true;
  bool _pointsAlerts = true;
  bool _coordinatorAnnouncements = true;
  bool _quietHours = false;

  @override
  void initState() {
    super.initState();
    _loadDevicePreferences();
  }

  Future<void> _loadDevicePreferences() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _eventReminders = prefs.getBool('pref_device_event_reminders') ?? true;
      _pointsAlerts = prefs.getBool('pref_device_points_alerts') ?? true;
      _coordinatorAnnouncements =
          prefs.getBool('pref_device_announcements') ?? true;
      _quietHours = prefs.getBool('pref_device_quiet_hours') ?? false;
    });
  }

  Future<void> _updatePref(
      String key, bool value, void Function() update) async {
    update();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(key, value);
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
            'Notification Settings',
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
            // Notice distinguishing device-local preferences
            Container(
              padding: const EdgeInsets.all(MaatramSpacing.md),
              decoration: BoxDecoration(
                color: const Color(0xFFF3F4F6),
                borderRadius: MaatramRadii.cardRadius,
                border: Border.all(color: MaatramColors.warmBorder),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.smartphone_rounded,
                      color: MaatramColors.deepNavy, size: 22),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'These preferences apply locally to this device. Account-level privacy and directory visibility are managed under Privacy & Consents.',
                      style: MaatramTypography.bodySmall.copyWith(
                        color: MaatramColors.secondaryText,
                        height: 1.4,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: MaatramSpacing.md),

            // Toggle Card
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
                    value: _eventReminders,
                    activeColor: MaatramColors.primaryGold,
                    title: const Text('Event Reminders',
                        style: TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 14,
                            fontWeight: FontWeight.w600)),
                    subtitle: const Text(
                        'Push alerts 24 hours prior to registered events',
                        style: TextStyle(
                            fontSize: 12, color: MaatramColors.secondaryText)),
                    onChanged: (val) =>
                        _updatePref('pref_device_event_reminders', val, () {
                      setState(() => _eventReminders = val);
                    }),
                  ),
                  const Divider(height: 1, color: MaatramColors.warmBorder),
                  SwitchListTile(
                    value: _pointsAlerts,
                    activeColor: MaatramColors.primaryGold,
                    title: const Text('Karma & Milestone Alerts',
                        style: TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 14,
                            fontWeight: FontWeight.w600)),
                    subtitle: const Text(
                        'Notify when points are awarded or achievements unlocked',
                        style: TextStyle(
                            fontSize: 12, color: MaatramColors.secondaryText)),
                    onChanged: (val) =>
                        _updatePref('pref_device_points_alerts', val, () {
                      setState(() => _pointsAlerts = val);
                    }),
                  ),
                  const Divider(height: 1, color: MaatramColors.warmBorder),
                  SwitchListTile(
                    value: _coordinatorAnnouncements,
                    activeColor: MaatramColors.primaryGold,
                    title: const Text('Coordinator Announcements',
                        style: TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 14,
                            fontWeight: FontWeight.w600)),
                    subtitle: const Text(
                        'Urgent venue or schedule changes broadcast by staff',
                        style: TextStyle(
                            fontSize: 12, color: MaatramColors.secondaryText)),
                    onChanged: (val) =>
                        _updatePref('pref_device_announcements', val, () {
                      setState(() => _coordinatorAnnouncements = val);
                    }),
                  ),
                  const Divider(height: 1, color: MaatramColors.warmBorder),
                  SwitchListTile(
                    value: _quietHours,
                    activeColor: MaatramColors.primaryGold,
                    title: const Text('Quiet Hours (10 PM – 7 AM)',
                        style: TextStyle(
                            fontFamily: 'Roboto',
                            fontSize: 14,
                            fontWeight: FontWeight.w600)),
                    subtitle: const Text(
                        'Silence non-urgent notifications overnight',
                        style: TextStyle(
                            fontSize: 12, color: MaatramColors.secondaryText)),
                    onChanged: (val) =>
                        _updatePref('pref_device_quiet_hours', val, () {
                      setState(() => _quietHours = val);
                    }),
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
