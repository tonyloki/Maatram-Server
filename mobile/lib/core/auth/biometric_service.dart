import '../storage/token_storage.dart';

/// Service managing optional biometric (fingerprint/face) unlock for existing sessions.
class BiometricService {
  final TokenStorage _storage;

  BiometricService({required TokenStorage storage}) : _storage = storage;

  /// Check whether biometric unlock is enabled by volunteer.
  Future<bool> isBiometricEnabled() async {
    return _storage.isBiometricEnabled();
  }

  /// Toggle biometric unlock preference.
  Future<void> setBiometricEnabled(bool enabled) async {
    await _storage.setBiometricEnabled(enabled);
  }

  /// Authenticate user via biometric hardware.
  /// Unlocks the existing securely stored session tokens.
  Future<bool> authenticateBiometric() async {
    final enabled = await isBiometricEnabled();
    if (!enabled) return false;
    final hasSession = await _storage.hasValidSession();
    return hasSession;
  }
}
