import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/app.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../support/auth_test_utils.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => SharedPreferences.setMockInitialValues({}));

  Future<void> abrirLogin(
    WidgetTester tester,
    MockClientHandler handler,
  ) async {
    final controller = crearControladorAuth(handler);
    await controller.restaurar();
    await tester.pumpWidget(HotelApp(controller: controller));
    await tester.pumpAndSettle();
  }

  testWidgets('muestra errores de validacion al enviar vacio', (tester) async {
    await abrirLogin(tester, (request) async => http.Response('{}', 200));

    await tester.tap(find.widgetWithText(FilledButton, 'Iniciar sesion'));
    await tester.pump();

    expect(find.text('Ingresa tu usuario o correo'), findsOneWidget);
    expect(find.text('Ingresa tu contrasena'), findsOneWidget);
  });

  testWidgets('muestra error de credenciales en 401', (tester) async {
    await abrirLogin(
      tester,
      (request) async => http.Response(
        jsonEncode({
          'detail': 'Credenciales incorrectas',
          'code': 'NO_AUTORIZADO',
        }),
        401,
      ),
    );

    await tester.enterText(find.byType(TextFormField).first, 'usuario');
    await tester.enterText(find.byType(TextFormField).last, 'clave');
    await tester.tap(find.widgetWithText(FilledButton, 'Iniciar sesion'));
    await tester.pumpAndSettle();

    expect(find.text('Usuario o contrasena incorrectos.'), findsOneWidget);
  });

  testWidgets('login exitoso muestra el shell', (tester) async {
    await abrirLogin(
      tester,
      (request) async => http.Response(loginJson(), 200),
    );

    await tester.enterText(find.byType(TextFormField).first, 'usuario');
    await tester.enterText(find.byType(TextFormField).last, 'clave');
    await tester.tap(find.widgetWithText(FilledButton, 'Iniciar sesion'));
    await tester.pumpAndSettle();

    expect(find.byIcon(Icons.logout), findsOneWidget);
    expect(find.text('Panel'), findsWidgets);
  });
}
