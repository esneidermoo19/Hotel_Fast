/// Contrato minimo que el [ApiClient] necesita para autenticar solicitudes.
///
/// Vive en `core` para que el cliente HTTP no dependa de la capa de auth.
/// [AuthService] es su implementacion real.
abstract interface class SesionAutenticacion {
  /// Access token vigente, o `null` si no hay sesion.
  String? get accessToken;

  /// Intenta renovar la sesion con el refresh token almacenado.
  ///
  /// Devuelve `true` si se obtuvieron tokens nuevos.
  Future<bool> refrescar();

  /// Limpia la sesion local cuando la renovacion no es posible.
  Future<void> alExpirarSesion();
}
