import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/auditoria/auditoria_service.dart';
import 'package:hotel_front/auditoria/auditoria_view.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

String _registro({int id = 1, String accion = 'CREATE'}) {
  return jsonEncode({
    'id': id,
    'usuarioId': 2,
    'accion': accion,
    'entidad': 'Reserva',
    'entidadId': 9,
    'ip': '127.0.0.1',
    'detalle': {'codigo': 'RES-1'},
    'createdAt': '2026-10-09T14:30:00Z',
  });
}

Widget _envoltura(AuditoriaService servicio) {
  return MaterialApp(
    home: Scaffold(body: AuditoriaView(service: servicio)),
  );
}

void main() {
  testWidgets('lista los registros de auditoria', (tester) async {
    final servicio = AuditoriaService(
      crearApiSimulada((request) async {
        return http.Response(
          jsonEncode({
            'items': [
              jsonDecode(_registro()),
              jsonDecode(_registro(id: 2, accion: 'LOGIN')),
            ],
            'total': 2,
            'pagina': 1,
            'tamano': 20,
          }),
          200,
        );
      }),
    );

    await tester.pumpWidget(_envoltura(servicio));
    await tester.pumpAndSettle();

    expect(find.text('CREATE · Reserva'), findsOneWidget);
    expect(find.text('LOGIN · Reserva'), findsOneWidget);
  });

  testWidgets('muestra error y boton de reintentar', (tester) async {
    final servicio = AuditoriaService(
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

    expect(find.text('Reintentar'), findsOneWidget);
  });

  testWidgets('el detalle muestra los campos del registro', (tester) async {
    final servicio = AuditoriaService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            'items': [jsonDecode(_registro())],
            'total': 1,
            'pagina': 1,
            'tamano': 20,
          }),
          200,
        ),
      ),
    );

    await tester.pumpWidget(_envoltura(servicio));
    await tester.pumpAndSettle();
    await tester.tap(find.text('CREATE · Reserva'));
    await tester.pumpAndSettle();

    expect(find.text('Fecha'), findsOneWidget);
    expect(find.text('codigo'), findsOneWidget);
    expect(find.text('RES-1'), findsOneWidget);
  });
}
