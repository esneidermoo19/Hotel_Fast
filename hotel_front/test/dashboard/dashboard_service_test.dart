import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/dashboard/dashboard_service.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

void main() {
  test('cargar parsea los ocho indicadores', () async {
    final servicio = DashboardService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            'reservasActivas': 5,
            'reservasPendientesCheckIn': 2,
            'huespedesAlojados': 7,
            'checkOutsDelDia': 1,
            'habitacionesDisponibles': 10,
            'habitacionesOcupadas': 4,
            'habitacionesEnMantenimiento': 2,
            'cuentasConSaldoPendiente': 3,
          }),
          200,
        ),
      ),
    );

    final resumen = await servicio.cargar();

    expect(resumen.reservasActivas, 5);
    expect(resumen.habitacionesOcupadas, 4);
    expect(resumen.habitacionesDisponibles, 10);
    expect(resumen.cuentasConSaldoPendiente, 3);
  });

  test('los campos faltantes quedan en cero', () async {
    final servicio = DashboardService(
      crearApiSimulada((request) async => http.Response('{}', 200)),
    );

    final resumen = await servicio.cargar();

    expect(resumen.reservasActivas, 0);
    expect(resumen.checkOutsDelDia, 0);
  });
}
