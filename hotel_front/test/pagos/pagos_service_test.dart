import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/cuentas/models/pago.dart';
import 'package:hotel_front/pagos/pagos_service.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

void main() {
  test('registrar envia el cuerpo y parsea el pago', () async {
    http.Request? capturado;
    final servicio = PagosService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(
          jsonEncode({
            'id': 1,
            'monto': 50.0,
            'metodo': 'EFECTIVO',
            'tipo': 'ABONO',
            'anulado': false,
            'referencia': null,
          }),
          201,
        );
      }),
    );

    final pago = await servicio.registrar(
      7,
      const PagoRequest(monto: 50, metodo: 'EFECTIVO', tipo: 'ABONO'),
    );

    expect(capturado!.url.path, '/api/reservas/7/pagos');
    final cuerpo = jsonDecode(capturado!.body) as Map<String, dynamic>;
    expect(cuerpo['monto'], 50.0);
    expect(cuerpo['metodo'], 'EFECTIVO');
    expect(cuerpo['tipo'], 'ABONO');
    expect(pago.monto, 50.0);
    expect(pago.metodo, 'EFECTIVO');
  });

  test('la referencia opcional se omite si es null', () async {
    http.Request? capturado;
    final servicio = PagosService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(
          jsonEncode({
            'id': 1,
            'monto': 30.0,
            'metodo': 'TARJETA',
            'tipo': 'PAGO_FINAL',
            'anulado': false,
          }),
          201,
        );
      }),
    );

    await servicio.registrar(
      7,
      const PagoRequest(monto: 30, metodo: 'TARJETA', tipo: 'PAGO_FINAL'),
    );

    final cuerpo = jsonDecode(capturado!.body) as Map<String, dynamic>;
    expect(cuerpo.containsKey('referencia'), isFalse);
  });
}
