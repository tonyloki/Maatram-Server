/// Environment configuration for the Maatram mobile client.
class EnvConfig {
  final String apiBaseUrl;
  final Duration connectTimeout;
  final Duration receiveTimeout;

  const EnvConfig({
    required this.apiBaseUrl,
    this.connectTimeout = const Duration(seconds: 15),
    this.receiveTimeout = const Duration(seconds: 15),
  });

  /// Default local development configuration targeting Android emulator or iOS simulator.
  factory EnvConfig.development() {
    // 10.0.2.2 maps to host machine localhost in Android emulator.
    // localhost maps to host machine in iOS simulator.
    const baseUrl = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://10.0.2.2:8000/api/v1',
    );
    return const EnvConfig(apiBaseUrl: baseUrl);
  }

  /// Production configuration
  factory EnvConfig.production() {
    const baseUrl = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'https://api.maatram.org/api/v1',
    );
    return const EnvConfig(apiBaseUrl: baseUrl);
  }
}
