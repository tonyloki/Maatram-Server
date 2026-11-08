import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/config/env_config.dart';
import 'core/network/api_client.dart';
import 'core/storage/token_storage.dart';

// Dependency injection providers
final envConfigProvider = Provider<EnvConfig>((ref) => EnvConfig.development());
final tokenStorageProvider = Provider<TokenStorage>((ref) => TokenStorage());
final apiClientProvider = Provider<ApiClient>((ref) {
  final storage = ref.watch(tokenStorageProvider);
  final config = ref.watch(envConfigProvider);
  return ApiClient(tokenStorage: storage, envConfig: config);
});

// Authentication state provider
final authStateProvider = FutureProvider<bool>((ref) async {
  final storage = ref.watch(tokenStorageProvider);
  return storage.hasValidSession();
});

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    const ProviderScope(
      child: MaatramApp(),
    ),
  );
}

class MaatramApp extends StatelessWidget {
  const MaatramApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Maatram Volunteering & Gamification',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0F766E), // Teal primary brand
          primary: const Color(0xFF0F766E),
          secondary: const Color(0xFFF59E0B), // Amber accent
          surface: Colors.white,
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: const AuthGateScreen(),
    );
  }
}

class AuthGateScreen extends ConsumerWidget {
  const AuthGateScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);

    return authState.when(
      loading: () => const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      ),
      error: (_, __) => const LoginScreen(),
      data: (isAuthenticated) {
        if (isAuthenticated) {
          return const DashboardScreen();
        }
        return const LoginScreen();
      },
    );
  }
}

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(
                Icons.volunteer_activism,
                size: 72,
                color: Color(0xFF0F766E),
              ),
              const SizedBox(height: 16),
              const Text(
                'Maatram Foundation',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF0F172A),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Volunteering & Gamification Portal',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: Color(0xFF64748B),
                ),
              ),
              const SizedBox(height: 48),
              ElevatedButton(
                onPressed: () {},
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0F766E),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Log In with Credentials',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Maatram Portal'),
        backgroundColor: const Color(0xFF0F766E),
        foregroundColor: Colors.white,
      ),
      body: const Center(
        child: Text(
          'Welcome to Maatram Volunteering',
          style: TextStyle(fontSize: 18, color: Color(0xFF334155)),
        ),
      ),
    );
  }
}
