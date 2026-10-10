/// Codigos de error estables que devuelve el backend FastAPI.
///
/// El `code` es la referencia estable para el cliente (mas fiable que el HTTP).
/// Fuente: `app/core/errors.py` y `docs/API_CONTRACT.md`.
abstract final class CodigosError {
  static const String validacion = 'VALIDACION';
  static const String noAutorizado = 'NO_AUTORIZADO';
  static const String tokenInvalido = 'TOKEN_INVALIDO';
  static const String refreshTokenInvalido = 'REFRESH_TOKEN_INVALIDO';
  static const String sinPermisos = 'SIN_PERMISOS';
  static const String noEncontrado = 'NO_ENCONTRADO';
  static const String conflicto = 'CONFLICTO';
  static const String reglaNegocio = 'REGLA_NEGOCIO';
  static const String demasiadasSolicitudes = 'DEMASIADAS_SOLICITUDES';
  static const String noDisponible = 'NO_DISPONIBLE';
  static const String baseDatos = 'BASE_DATOS';

  /// Codigos del modulo de imagenes de habitaciones.
  static const String formatoImagenInvalido = 'FORMATO_IMAGEN_INVALIDO';
  static const String imagenMuyGrande = 'IMAGEN_MUY_GRANDE';
  static const String maximoImagenes = 'MAXIMO_IMAGENES';

  /// Codigos generados por el cliente (no por el backend).
  static const String errorInterno = 'ERROR_INTERNO';
  static const String errorDesconocido = 'ERROR_DESCONOCIDO';
  static const String errorDeRed = 'ERROR_DE_RED';
  static const String tiempoDeEspera = 'TIEMPO_DE_ESPERA';
}
