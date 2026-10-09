import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/consumos/consumos_service.dart';
import 'package:hotel_front/cuentas/models/consumo.dart';
import 'package:hotel_front/core/network/api_exception.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

void main() {
  test('registrar envia el cuerpo y parsea el consumo', () async {
    http.Request? capturado;
    final servicio = ConsumosService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(
          jsonEncode({
            'id': 1,
            'descripcion': 'Minibar',
            'cantidad': 2,
            'precioUnitario': 15.0,
            'anulado': false,
          }),
          201,
        );
      }),
    );

    final consumo = await servicio.registrar(
      7,
      const ConsumoRequest(
        descripcion: 'Minibar',
        cantidad: 2,
        precioUnitario: 15.0,
      ),
    );

    expect(capturado!.url.path, '/api/reservas/7/consumos');
    final cuerpo = jsonDecode(capturado!.body) as Map<String, dynamic>;
    expect(cuerpo['descripcion'], 'Minibar');
    expect(cuerpo['cantidad'], 2);
    expect(cuerpo['precioUnitario'], 15.0);
    expect(consumo.total, 30.0);
  });

  test('un 409 REGLA_NEGOCIO se propaga como ApiException', () async {
    final servicio = ConsumosService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            'detail': 'La reserva no admite consumos en su estado',
            'code': 'REGLA_NEGOCIO',
          }),
          409,
        ),
      ),
    );

    await expectLater(
      servicio.registrar(
        7,
        const ConsumoRequest(
          descripcion: 'Minibar',
          cantidad: 1,
          precioUnitario: 10,
        ),
      ),
      throwsA(
        isA<ApiException>()
            .having((e) => e.statusCode, 'statusCode', 409)
            .having((e) => e.codigo, 'codigo', 'REGLA_NEGOCIO'),
      ),
    );
  });
}
