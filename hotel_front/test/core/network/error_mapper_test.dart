import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/core/network/codigos_error.dart';
import 'package:hotel_front/core/network/error_mapper.dart';

void main() {
  group('ErrorMapper.desdeRespuesta', () {
    test('422 usa el codigo de validacion y parsea errors[]', () {
      final error = ErrorMapper.desdeRespuesta(422, {
        'detail': 'Datos invalidos: mayor que 0',
        'code': 'VALIDACION',
        'errors': [
          {
            'campo': 'precioPorNoche',
            'mensaje': 'mayor que 0',
            'tipo': 'greater_than',
          },
        ],
      });

      expect(error.statusCode, 422);
      expect(error.codigo, CodigosError.validacion);
      expect(error.esValidacion, isTrue);
      expect(error.errores, hasLength(1));
      expect(error.errores.first.campo, 'precioPorNoche');
      expect(error.mensajesPorCampo['precioPorNoche'], 'mayor que 0');
    });

    test('409 conserva REGLA_NEGOCIO enviado por el backend', () {
      final error = ErrorMapper.desdeRespuesta(409, {
        'detail': 'La reserva no esta en CHECK_IN',
        'code': 'REGLA_NEGOCIO',
      });

      expect(error.statusCode, 409);
      expect(error.codigo, CodigosError.reglaNegocio);
      expect(error.esConflicto, isTrue);
      expect(error.esDeRed, isFalse);
    });

    test('409 sin code usa CONFLICTO por defecto', () {
      final error = ErrorMapper.desdeRespuesta(409, {'detail': 'Conflicto'});

      expect(error.codigo, CodigosError.conflicto);
    });

    test('401 conserva TOKEN_INVALIDO', () {
      final error = ErrorMapper.desdeRespuesta(401, {
        'detail': 'Token de acceso invalido',
        'code': 'TOKEN_INVALIDO',
        'errors': [],
      });

      expect(error.codigo, CodigosError.tokenInvalido);
      expect(error.esDeAutenticacion, isTrue);
    });

    test('403 usa SIN_PERMISOS', () {
      final error = ErrorMapper.desdeRespuesta(403, {
        'detail': 'No tienes permisos',
        'code': 'SIN_PERMISOS',
      });

      expect(error.codigo, CodigosError.sinPermisos);
      expect(error.esDeAutenticacion, isTrue);
    });

    test('404 usa NO_ENCONTRADO', () {
      final error = ErrorMapper.desdeRespuesta(404, {
        'detail': 'Habitacion no encontrada',
        'code': 'NO_ENCONTRADO',
      });

      expect(error.esNoEncontrado, isTrue);
      expect(error.codigo, CodigosError.noEncontrado);
    });

    test('429 usa DEMASIADAS_SOLICITUDES', () {
      final error = ErrorMapper.desdeRespuesta(429, {
        'detail': 'Demasiados intentos',
        'code': 'DEMASIADAS_SOLICITUDES',
      });

      expect(error.codigo, CodigosError.demasiadasSolicitudes);
    });

    test('cuerpo no-JSON usa codigo y mensaje por defecto del HTTP', () {
      final error = ErrorMapper.desdeRespuesta(500, '<html>error</html>');

      expect(error.codigo, CodigosError.errorInterno);
      expect(error.mensaje, isNotEmpty);
      expect(error.errores, isEmpty);
    });

    test('cuerpo nulo usa codigo y mensaje por defecto', () {
      final error = ErrorMapper.desdeRespuesta(503, null);

      expect(error.codigo, CodigosError.noDisponible);
      expect(error.statusCode, 503);
    });
  });

  group('ErrorMapper de red', () {
    test('tiempo de espera marca esDeRed', () {
      final error = ErrorMapper.deTiempoDeEspera(const Duration(seconds: 15));

      expect(error.codigo, CodigosError.tiempoDeEspera);
      expect(error.esDeRed, isTrue);
      expect(error.mensaje, contains('15'));
    });

    test('error de red marca esDeRed', () {
      final error = ErrorMapper.deRed('Connection refused');

      expect(error.codigo, CodigosError.errorDeRed);
      expect(error.esDeRed, isTrue);
    });
  });
}
