import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/constants/app_constants.dart';
import '../core/theme/theme.dart';
import 'router/app_router.dart';

/// Root application widget for Maatram Volunteer Mobile Application.
class MaatramApp extends ConsumerWidget {
  const MaatramApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,
      theme: MaatramTheme.lightTheme,
      routerConfig: router,
    );
  }
}

