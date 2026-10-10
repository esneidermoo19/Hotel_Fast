import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/dashboard/dashboard_service.dart';
import 'package:hotel_front/dashboard/dashboard_view.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

Widget _envoltura(DashboardService servicio) {
  return MaterialApp(
    home: Scaffold(body: DashboardView(service: servicio)),
  );
}

String _dashboardJson() {
  return jsonEncode({
    'reservasActivas': 5,
    'reservasPendientesCheckIn': 2,
    'huespedesAlojados': 7,
    'checkOutsDelDia': 1,
    'habitacionesDisponibles': 10,
    'habitacionesOcupadas': 4,
    'habitacionesEnMantenimiento': 2,
    'cuentasConSaldoPendiente': 3,
  });
}

void main() {
  testWidgets('muestra las tarjetas con los indicadores', (tester) async {
    tester.view.physicalSize = const Size(1400, 1200);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final servicio = DashboardService(
      crearApiSimulada((request) async => http.Response(_dashboardJson(), 200)),
    );

    await tester.pumpWidget(_envoltura(servicio));
    await tester.pumpAndSettle();

    expect(find.text('Resumen operativo'), findsOneWidget);
    expect(find.text('Habitaciones ocupadas'), findsOneWidget);
    expect(find.text('Habitaciones disponibles'), findsOneWidget);
    expect(find.text('4'), findsOneWidget);
  });

  testWidgets('muestra error y boton de reintentar', (tester) async {
    final servicio = DashboardService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            'detail': 'Error de base de datos',
            'code': 'BASE_DATOS',
          }),
          500,
        ),
      ),
    );

    await tester.pumpWidget(_envoltura(servicio));
    await tester.pumpAndSettle();

    expect(find.text('Error de base de datos'), findsOneWidget);
    expect(find.text('Reintentar'), findsOneWidget);
  });
}
