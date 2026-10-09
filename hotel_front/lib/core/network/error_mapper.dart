import 'api_exception.dart';
import 'codigos_error.dart';
import 'error_campo.dart';

/// Traduce las respuestas de error del backend al tipo [ApiException].
///
/// El backend responde siempre con el sobre
/// `{ "detail": "...", "code": "CODIGO", "errors": [...] }`, donde `errors`
/// solo aparece en errores de validacion (422). Se usa `code` como referencia
/// estable; el codigo HTTP es el respaldo cuando el cuerpo no trae `code`.
abstract final class ErrorMapper {
  static ApiException desdeRespuesta(int statusCode, Object? cuerpo) {
    String? codigo;
    String? detalle;
    List<ErrorCampo> errores = const <ErrorCampo>[];

    if (cuerpo is Map) {
      final mapa = cuerpo.cast<String, dynamic>();
      final code = mapa['code'];
      final detail = mapa['detail'];
      final lista = mapa['errors'];
      if (code is String && code.isNotEmpty) {
        codigo = code;
      }
      if (detail is String && detail.isNotEmpty) {
        detalle = detail;
      }
      if (lista is List) {
        errores = lista
            .whereType<Map>()
            .map((item) => ErrorCampo.fromJson(item.cast<String, dynamic>()))
            .toList(growable: false);
      }
    }

    return ApiException(
      statusCode: statusCode,
      codigo: codigo ?? codigoPorDefecto(statusCode),
      mensaje: detalle ?? mensajePorDefecto(statusCode),
      errores: errores,
    );
  }

  static ApiException deTiempoDeEspera(Duration timeout) {
    return ApiException(
      codigo: CodigosError.tiempoDeEspera,
      mensaje:
          'La solicitud tardo mas de ${timeout.inSeconds} segundos. '
          'Verifica tu conexion e intentalo de nuevo.',
      esDeRed: true,
    );
  }

  static ApiException deRed(String detalle) {
    return ApiException(
      codigo: CodigosError.errorDeRed,
      mensaje:
          'No se pudo conectar con el servidor. '
          'Verifica tu conexion e intentalo de nuevo.',
      esDeRed: true,
    );
  }

  /// Codigo HTTP por defecto si el cuerpo no trae `code`.
  static String codigoPorDefecto(int statusCode) {
    switch (statusCode) {
      case 400:
        return 'SOLICITUD_INVALIDA';
      case 401:
        return CodigosError.noAutorizado;
      case 403:
        return CodigosError.sinPermisos;
      case 404:
        return CodigosError.noEncontrado;
      case 409:
        // El backend distingue CONFLICTO y REGLA_NEGOCIO en el campo `code`;
        // si no llega, se asume el mas generico.
        return CodigosError.conflicto;
      case 422:
        return CodigosError.validacion;
      case 429:
        return CodigosError.demasiadasSolicitudes;
      case 500:
        return CodigosError.errorInterno;
      case 503:
        return CodigosError.noDisponible;
      default:
        return CodigosError.errorDesconocido;
    }
  }

  /// Mensaje por defecto si el cuerpo no trae `detail`.
  static String mensajePorDefecto(int statusCode) {
    switch (statusCode) {
      case 400:
        return 'La solicitud no es valida.';
      case 401:
        return 'Tu sesion no es valida o expiro. Inicia sesion de nuevo.';
      case 403:
        return 'No tienes permisos para realizar esta accion.';
      case 404:
        return 'No se encontro el recurso solicitado.';
      case 409:
        return 'La operacion entra en conflicto con el estado actual.';
      case 422:
        return 'Hay datos invalidos en la solicitud.';
      case 429:
        return 'Demasiadas solicitudes. Espera un momento e intentalo de nuevo.';
      case 500:
        return 'Ocurrio un error interno del servidor.';
      case 503:
        return 'El servicio no esta disponible en este momento.';
      default:
        return 'Ocurrio un error inesperado.';
    }
  }
}
