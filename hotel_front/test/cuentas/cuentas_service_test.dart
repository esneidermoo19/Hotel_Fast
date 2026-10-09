import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/cuentas/cuentas_service.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

void main() {
  test('obtener parsea la cuenta y sus movimientos', () async {
    final servicio = CuentasService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            'totalAlojamiento': 100.0,
            'totalConsumosVigentes': 30.0,
            'totalPagosVigentes': 50.0,
            'saldoPendiente': 80.0,
            'detalleConsumos': [
              {
                'id': 1,
                'descripcion': 'Minibar',
                'cantidad': 2,
                'precioUnitario': 15.0,
                'anulado': false,
              },
            ],
            'detallePagos': [
              {
                'id': 1,
                'monto': 50.0,
                'metodo': 'EFECTIVO',
                'tipo': 'ABONO',
                'anulado': false,
              },
            ],
          }),
          200,
        ),
      ),
    );

    final cuenta = await servicio.obtener(7);

    expect(cuenta.totalAlojamiento, 100.0);
    expect(cuenta.totalCuenta, 130.0);
    expect(cuenta.saldoPendiente, 80.0);
    expect(cuenta.detalleConsumos.single.descripcion, 'Minibar');
    expect(cuenta.detalleConsumos.single.total, 30.0);
    expect(cuenta.detallePagos.single.metodo, 'EFECTIVO');
  });

  test('una cuenta sin movimientos queda vacia', () async {
    final servicio = CuentasService(
      crearApiSimulada(
        (request) async => http.Response(
          '{"totalAlojamiento":100,"totalConsumosVigentes":0,'
          '"totalPagosVigentes":0,"saldoPendiente":100}',
          200,
        ),
      ),
    );

    final cuenta = await servicio.obtener(1);

    expect(cuenta.detalleConsumos, isEmpty);
    expect(cuenta.detallePagos, isEmpty);
  });
}
