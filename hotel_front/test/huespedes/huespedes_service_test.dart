import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/core/network/api_exception.dart';
import 'package:hotel_front/huespedes/huespedes_service.dart';
import 'package:hotel_front/huespedes/models/huesped.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

String _huespedJson({int id = 1}) {
  return jsonEncode({
    'id': id,
    'tipoDocumento': 'CC',
    'numeroDocumento': '12345678',
    'nombres': 'Ana',
    'apellidos': 'Gomez',
    'email': 'ana@example.com',
    'telefono': '+573001234567',
    'nacionalidad': 'Colombiana',
    'fechaNacimiento': null,
    'direccion': 'Calle 1',
    'observaciones': null,
  });
}

String _paginaJson() {
  return jsonEncode({
    'items': [jsonDecode(_huespedJson())],
    'total': 1,
    'pagina': 1,
    'tamano': 20,
  });
}

void main() {
  test('listar parsea la pagina y envia la busqueda', () async {
    Uri? uri;
    final servicio = HuespedesService(
      crearApiSimulada((request) async {
        uri = request.url;
        return http.Response(_paginaJson(), 200);
      }),
    );

    final pagina = await servicio.listar(pagina: 2, tamano: 20, q: 'ana');

    expect(pagina.total, 1);
    expect(pagina.items.first.nombreCompleto, 'Ana Gomez');
    expect(pagina.items.first.documento, 'CC 12345678');
    expect(uri!.path, '/api/huespedes');
    expect(uri!.queryParameters, {'pagina': '2', 'tamano': '20', 'q': 'ana'});
  });

  test('listar sin busqueda omite q', () async {
    Uri? uri;
    final servicio = HuespedesService(
      crearApiSimulada((request) async {
        uri = request.url;
        return http.Response(_paginaJson(), 200);
      }),
    );

    await servicio.listar();

    expect(uri!.queryParameters.containsKey('q'), isFalse);
  });

  test('crear envia el cuerpo y parsea la respuesta 201', () async {
    http.Request? capturado;
    final servicio = HuespedesService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(_huespedJson(), 201);
      }),
    );

    final creado = await servicio.crear(
      const HuespedPayload(
        tipoDocumento: 'CC',
        numeroDocumento: '12345678',
        nombres: 'Ana',
        apellidos: 'Gomez',
        email: 'ana@example.com',
      ),
    );

    expect(capturado!.method, 'POST');
    expect(capturado!.url.path, '/api/huespedes');
    expect(jsonDecode(capturado!.body)['tipoDocumento'], 'CC');
    expect(creado.id, 1);
  });

  test('un 409 de documento duplicado se propaga como ApiException', () async {
    final servicio = HuespedesService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            'detail': 'El documento ya esta registrado',
            'code': 'CONFLICTO',
          }),
          409,
        ),
      ),
    );

    await expectLater(
      servicio.crear(
        const HuespedPayload(
          tipoDocumento: 'CC',
          numeroDocumento: '12345678',
          nombres: 'Ana',
          apellidos: 'Gomez',
        ),
      ),
      throwsA(
        isA<ApiException>()
            .having((e) => e.statusCode, 'statusCode', 409)
            .having((e) => e.codigo, 'codigo', 'CONFLICTO'),
      ),
    );
  });
}
