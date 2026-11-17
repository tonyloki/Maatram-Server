import 'package:flutter/foundation.dart';

/// Environment configuration for the Maatram mobile client.
class EnvConfig {
  final String apiBaseUrl;
  final Duration connectTimeout;
  final Duration receiveTimeout;

  const EnvConfig({
    required this.apiBaseUrl,
    this.connectTimeout = const Duration(seconds: 10),
    this.receiveTimeout = const Duration(seconds: 30),
  });

  /// Default local development configuration targeting Android emulator, iOS simulator, or Web.
  factory EnvConfig.development() {
    // 10.0.2.2 maps to host machine localhost in Android emulator.
    // localhost maps to host machine in Web browser and iOS simulator.
    const envUrl = String.fromEnvironment('API_BASE_URL');
    final baseUrl = envUrl.isNotEmpty
        ? envUrl
        : (kIsWeb
            ? 'http://127.0.0.1:8000/api/v1'
            : 'http://10.0.2.2:8000/api/v1');
    const connectSec =
        int.fromEnvironment('API_CONNECT_TIMEOUT_SEC', defaultValue: 10);
    const receiveSec =
        int.fromEnvironment('API_RECEIVE_TIMEOUT_SEC', defaultValue: 30);
    return EnvConfig(
      apiBaseUrl: baseUrl,
      connectTimeout: Duration(seconds: connectSec),
      receiveTimeout: Duration(seconds: receiveSec),
    );
  }

  /// Production configuration
  factory EnvConfig.production() {
    const baseUrl = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'https://api.maatram.org/api/v1',
    );
    const connectSec =
        int.fromEnvironment('API_CONNECT_TIMEOUT_SEC', defaultValue: 10);
    const receiveSec =
        int.fromEnvironment('API_RECEIVE_TIMEOUT_SEC', defaultValue: 30);
    return const EnvConfig(
      apiBaseUrl: baseUrl,
      connectTimeout: Duration(seconds: connectSec),
      receiveTimeout: Duration(seconds: receiveSec),
    );
  }
}
