import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/core/network/api_exception.dart';
import 'package:hotel_front/habitaciones/habitaciones_service.dart';
import 'package:hotel_front/habitaciones/models/habitacion.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

String _habitacionJson({int id = 1, int numero = 101}) {
  return jsonEncode({
    'id': id,
    'numero': numero,
    'tipo': 'DOBLE',
    'capacidad': 2,
    'precioPorNoche': 120.5,
    'estado': 'DISPONIBLE',
    'limpieza': 'LIMPIA',
    'descripcion': null,
  });
}

void main() {
  test('listar parsea el arreglo y envia los filtros', () async {
    Uri? uri;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        uri = request.url;
        return http.Response(
          jsonEncode([
            jsonDecode(_habitacionJson()),
            jsonDecode(_habitacionJson(id: 2, numero: 102)),
          ]),
          200,
        );
      }),
    );

    final lista = await servicio.listar(estado: 'DISPONIBLE', tipo: 'DOBLE');

    expect(lista, hasLength(2));
    expect(lista.first.numero, 101);
    expect(lista.first.precioPorNoche, 120.5);
    expect(uri!.path, '/api/habitaciones');
    expect(uri!.queryParameters, {'estado': 'DISPONIBLE', 'tipo': 'DOBLE'});
  });

  test('crear envia el cuerpo y parsea la respuesta 201', () async {
    http.Request? capturado;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(_habitacionJson(), 201);
      }),
    );

    final creada = await servicio.crear(
      const HabitacionPayload(
        numero: 101,
        tipo: 'DOBLE',
        capacidad: 2,
        precioPorNoche: 120.5,
        estado: 'DISPONIBLE',
      ),
    );

    expect(capturado!.method, 'POST');
    expect(capturado!.url.path, '/api/habitaciones');
    expect(jsonDecode(capturado!.body), {
      'numero': 101,
      'tipo': 'DOBLE',
      'capacidad': 2,
      'precioPorNoche': 120.5,
      'estado': 'DISPONIBLE',
    });
    expect(creada.id, 1);
  });

  test('cambiarEstado usa PATCH con el cuerpo correcto', () async {
    http.Request? capturado;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(_habitacionJson(), 200);
      }),
    );

    await servicio.cambiarEstado(7, 'MANTENIMIENTO');

    expect(capturado!.method, 'PATCH');
    expect(capturado!.url.path, '/api/habitaciones/7/estado');
    expect(jsonDecode(capturado!.body), {'estado': 'MANTENIMIENTO'});
  });

  test('eliminar usa DELETE y no falla con 204', () async {
    http.Request? capturado;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response('', 204);
      }),
    );

    await servicio.eliminar(7);

    expect(capturado!.method, 'DELETE');
    expect(capturado!.url.path, '/api/habitaciones/7');
  });

  test('un 409 REGLA_NEGOCIO se propaga como ApiException', () async {
    final servicio = HabitacionesService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            'detail': 'El numero de habitacion ya existe',
            'code': 'CONFLICTO',
          }),
          409,
        ),
      ),
    );

    await expectLater(
      servicio.crear(
        const HabitacionPayload(
          numero: 101,
          tipo: 'DOBLE',
          capacidad: 2,
          precioPorNoche: 100,
          estado: 'DISPONIBLE',
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
