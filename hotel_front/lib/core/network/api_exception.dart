import 'error_campo.dart';

/// Error de aplicacion producido por el cliente HTTP.
///
/// Unifica errores del backend (con `code` estable), errores de red y errores
/// de tiempo de espera. Nunca se lanza una excepcion cruda de `http`.
class ApiException implements Exception {
  const ApiException({
    required this.mensaje,
    this.statusCode,
    this.codigo,
    this.errores = const <ErrorCampo>[],
    this.esDeRed = false,
  });

  /// Mensaje legible para mostrar al usuario.
  final String mensaje;

  /// Codigo HTTP, o `null` si la falla ocurrio antes de recibir respuesta.
  final int? statusCode;

  /// Codigo estable del backend o codigo propio del cliente.
  final String? codigo;

  /// Detalle por campo (solo en errores de validacion 422).
  final List<ErrorCampo> errores;

  /// `true` si la falla es de conectividad o tiempo de espera.
  final bool esDeRed;

  /// `true` cuando el problema son los datos enviados (422).
  bool get esValidacion => codigo == 'VALIDACION';

  /// `true` cuando no hay permisos para la accion (401 sin token / 403).
  bool get esDeAutenticacion => statusCode == 401 || statusCode == 403;

  /// `true` cuando el recurso no existe (404).
  bool get esNoEncontrado => statusCode == 404;

  /// `true` cuando hay conflicto con el estado actual, incluida REGLA_NEGOCIO.
  bool get esConflicto => statusCode == 409;

  /// Devuelve los mensajes por campo, o vacio si no aplica.
  Map<String, String> get mensajesPorCampo {
    final resultado = <String, String>{};
    for (final error in errores) {
      final campo = error.campo;
      if (campo != null) {
        resultado[campo] = error.mensaje;
      }
    }
    return resultado;
  }

  @override
  String toString() {
    final partes = <String>[
      if (statusCode != null) 'HTTP $statusCode',
      ?codigo,
      mensaje,
    ];
    return 'ApiException(${partes.join(' | ')})';
  }
}
