import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/app.dart';
import 'package:hotel_front/auth/models/login_request.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../support/auth_test_utils.dart';

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
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => SharedPreferences.setMockInitialValues({}));

  const tamanos = [360.0, 800.0, 1400.0];

  void configurarVentana(WidgetTester tester, double ancho, Brightness brillo) {
    tester.view.physicalSize = Size(ancho, 800);
    tester.view.devicePixelRatio = 1.0;
    tester.platformDispatcher.platformBrightnessTestValue = brillo;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.platformDispatcher.clearPlatformBrightnessTestValue);
  }

  for (final ancho in tamanos) {
    for (final brillo in const [Brightness.light, Brightness.dark]) {
      final nombre = brillo == Brightness.light ? 'claro' : 'oscuro';
      final etiqueta = '${ancho.toInt()}px en $nombre';

      testWidgets('login sin overflow a $etiqueta', (tester) async {
        configurarVentana(tester, ancho, brillo);

        final controller = crearControladorAuth(
          (request) async => http.Response('{}', 200),
        );
        await controller.restaurar();
        await tester.pumpWidget(HotelApp(controller: controller));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
      });

      testWidgets('shell sin overflow a $etiqueta', (tester) async {
        configurarVentana(tester, ancho, brillo);

        final controller = crearControladorAuth((request) async {
          if (request.url.path == '/api/dashboard') {
            return http.Response(_dashboardJson(), 200);
          }
          return http.Response(loginJson(), 200);
        });
        await controller.iniciarSesion(
          const LoginRequest(username: 'usuario', password: 'secreto'),
        );
        await tester.pumpWidget(HotelApp(controller: controller));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
      });
    }
  }
}
