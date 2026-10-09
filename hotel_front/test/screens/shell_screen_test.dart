import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/app.dart';
import 'package:hotel_front/auth/models/login_request.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../support/auth_test_utils.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => SharedPreferences.setMockInitialValues({}));

  Future<void> abrirShell(WidgetTester tester, String role) async {
    tester.view.physicalSize = const Size(1400, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final controller = crearControladorAuth(
      (request) async => http.Response(loginJson(role: role), 200),
    );
    await controller.iniciarSesion(
      const LoginRequest(username: 'usuario', password: 'secreto'),
    );
    await tester.pumpWidget(HotelApp(controller: controller));
    await tester.pumpAndSettle();
  }

  testWidgets('ADMIN ve los modulos administrativos', (tester) async {
    await abrirShell(tester, 'ADMIN');

    expect(find.text('Usuarios'), findsOneWidget);
    expect(find.text('Auditoria'), findsOneWidget);
    expect(find.text('Habitaciones'), findsOneWidget);
    expect(find.byIcon(Icons.logout), findsOneWidget);
  });

  testWidgets('RECEPCION no ve los modulos administrativos', (tester) async {
    await abrirShell(tester, 'RECEPCION');

    expect(find.text('Habitaciones'), findsOneWidget);
    expect(find.text('Usuarios'), findsNothing);
    expect(find.text('Auditoria'), findsNothing);
  });
}
