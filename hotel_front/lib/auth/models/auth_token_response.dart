import '../../shared/utils/lectura_json.dart';

/// Par de tokens que devuelve el backend en login y refresh.
///
/// JSON de origen (`login` y `refresh`): `token`, `refreshToken`, `tokenType`,
/// `expiresIn` (segundos).
class AuthTokenResponse {
  const AuthTokenResponse({
    required this.accessToken,
    required this.refreshToken,
    this.tokenType = 'bearer',
    this.expiresIn = 0,
  });

  final String accessToken;
  final String refreshToken;
  final String tokenType;

  /// Vigencia del access token en segundos.
  final int expiresIn;

  factory AuthTokenResponse.fromJson(Map<String, dynamic> json) {
    return AuthTokenResponse(
      accessToken: leerTexto(json['token']) ?? '',
      refreshToken: leerTexto(json['refreshToken']) ?? '',
      tokenType: leerTexto(json['tokenType']) ?? 'bearer',
      expiresIn: leerEntero(json['expiresIn']) ?? 0,
    );
  }
}
