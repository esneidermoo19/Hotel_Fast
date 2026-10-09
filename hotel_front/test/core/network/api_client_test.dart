import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/config/app_config.dart';
import 'package:hotel_front/core/network/api_client.dart';
import 'package:hotel_front/core/network/api_exception.dart';
import 'package:hotel_front/core/network/codigos_error.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

ApiClient _clienteCon(MockClientHandler handler, {Duration? timeout}) {
  return ApiClient(
    config: AppConfig(
      baseUrl: 'http://localhost:8000',
      timeout: timeout ?? const Duration(seconds: 5),
    ),
    cliente: MockClient(handler),
  );
}

void main() {
  group('ApiClient exitos', () {
    test('GET devuelve el JSON decodificado y arma la URL', () async {
      Uri? capturada;
      final client = _clienteCon((request) async {
        capturada = request.url;
        return http.Response('{"status":"ok"}', 200);
      });

      final data = await client.get('/api/health');

      expect(capturada.toString(), 'http://localhost:8000/api/health');
      expect(data, {'status': 'ok'});
    });

    test('GET agrega query params y omite nulos', () async {
      Uri? capturada;
      final client = _clienteCon((request) async {
        capturada = request.url;
        return http.Response('[]', 200);
      });

      await client.get('/api/reservas', query: {'pagina': 1, 'q': null});

      expect(capturada!.queryParameters, {'pagina': '1'});
    });

    test('POST envia JSON con content-type', () async {
      http.Request? capturada;
      final client = _clienteCon((request) async {
        capturada = request;
        return http.Response('{"id":1}', 201);
      });

      final data = await client.post(
        '/api/habitaciones',
        body: {'numero': 101, 'tipo': 'DOBLE'},
      );

      expect(capturada!.method, 'POST');
      expect(capturada!.headers['Content-Type'], contains('application/json'));
      expect(jsonDecode(capturada!.body), {'numero': 101, 'tipo': 'DOBLE'});
      expect(data, {'id': 1});
    });

    test('204 sin cuerpo devuelve null', () async {
      final client = _clienteCon((request) async => http.Response('', 204));

      await expectLater(client.delete('/api/habitaciones/1'), completes);
      final data = await client.get('/api/habitaciones/1');

      expect(data, isNull);
    });

    test('decodifica UTF-8 con acentos', () async {
      final client = _clienteCon(
        (request) async => http.Response.bytes(
          utf8.encode('{"nombre":"Habitación doble"}'),
          200,
        ),
      );

      final data = (await client.get('/api/x')) as Map<String, dynamic>;

      expect(data['nombre'], 'Habitación doble');
    });
  });

  group('ApiClient errores', () {
    test('409 REGLA_NEGOCIO se convierte en ApiException', () async {
      final client = _clienteCon(
        (request) async => http.Response(
          '{"detail":"La reserva no esta en CHECK_IN","code":"REGLA_NEGOCIO"}',
          409,
        ),
      );

      await expectLater(
        client.post('/api/reservas/1/check-out', body: const {}),
        throwsA(
          isA<ApiException>()
              .having((e) => e.statusCode, 'statusCode', 409)
              .having((e) => e.codigo, 'codigo', CodigosError.reglaNegocio)
              .having((e) => e.esConflicto, 'esConflicto', isTrue),
        ),
      );
    });

    test('422 VALIDACION incluye errores por campo', () async {
      final client = _clienteCon(
        (request) async => http.Response(
          '{"detail":"Datos invalidos","code":"VALIDACION",'
          '"errors":[{"campo":"fechaSalida","mensaje":"posterior a entrada"}]}',
          422,
        ),
      );

      await expectLater(
        client.post('/api/reservas', body: const {}),
        throwsA(
          isA<ApiException>()
              .having((e) => e.esValidacion, 'esValidacion', isTrue)
              .having(
                (e) => e.mensajesPorCampo['fechaSalida'],
                'mensaje campo',
                'posterior a entrada',
              ),
        ),
      );
    });

    test('error HTTP con cuerpo no-JSON usa valores por defecto', () async {
      final client = _clienteCon(
        (request) async => http.Response('Servicio caido', 503),
      );

      await expectLater(
        client.get('/api/health'),
        throwsA(
          isA<ApiException>().having(
            (e) => e.codigo,
            'codigo',
            CodigosError.noDisponible,
          ),
        ),
      );
    });

    test('tiempo de espera produce ApiException de red', () async {
      final client = _clienteCon((request) async {
        await Future<void>.delayed(const Duration(milliseconds: 300));
        return http.Response('{}', 200);
      }, timeout: const Duration(milliseconds: 40));

      await expectLater(
        client.get('/api/health'),
        throwsA(
          isA<ApiException>()
              .having((e) => e.esDeRed, 'esDeRed', isTrue)
              .having((e) => e.codigo, 'codigo', CodigosError.tiempoDeEspera),
        ),
      );
    });

    test('fallo de conexion produce ApiException de red', () async {
      final client = _clienteCon(
        (request) async => throw http.ClientException('Connection refused'),
      );

      await expectLater(
        client.get('/api/health'),
        throwsA(
          isA<ApiException>()
              .having((e) => e.esDeRed, 'esDeRed', isTrue)
              .having((e) => e.codigo, 'codigo', CodigosError.errorDeRed),
        ),
      );
    });
  });
}
