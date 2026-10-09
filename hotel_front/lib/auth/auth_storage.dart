import 'package:shared_preferences/shared_preferences.dart';

import 'models/auth_token_response.dart';

/// Persistencia de los tokens de sesion.
///
/// Usa `shared_preferences`, disponible en Web, Android y Windows. En Web el
/// respaldo es `localStorage` (legible por scripts), un riesgo aceptado en esta
/// fase: el access token es de vida corta (30 min) y el refresh rota en cada
/// uso, lo que limita la ventana de exposicion. Evaluar almacenamiento seguro
/// por plataforma antes de produccion.
class AuthStorage {
  static const String _claveAccess = 'auth.accessToken';
  static const String _claveRefresh = 'auth.refreshToken';
  static const String _claveExpira = 'auth.expiresIn';

  Future<AuthTokenResponse?> leer() async {
    final prefs = await SharedPreferences.getInstance();
    final access = prefs.getString(_claveAccess);
    final refresh = prefs.getString(_claveRefresh);
    if (access == null || refresh == null) {
      return null;
    }
    return AuthTokenResponse(
      accessToken: access,
      refreshToken: refresh,
      expiresIn: prefs.getInt(_claveExpira) ?? 0,
    );
  }

  Future<void> guardar(AuthTokenResponse tokens) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_claveAccess, tokens.accessToken);
    await prefs.setString(_claveRefresh, tokens.refreshToken);
    await prefs.setInt(_claveExpira, tokens.expiresIn);
  }

  Future<void> borrar() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_claveAccess);
    await prefs.remove(_claveRefresh);
    await prefs.remove(_claveExpira);
  }
}
