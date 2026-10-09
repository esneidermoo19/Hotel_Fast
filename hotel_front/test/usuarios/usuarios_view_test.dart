import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/catalogos/catalogos_service.dart';
import 'package:hotel_front/usuarios/usuarios_service.dart';
import 'package:hotel_front/usuarios/usuarios_view.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

String _usuarioJson({int id = 1, String username = 'admin'}) {
  return jsonEncode({
    'id': id,
    'username': username,
    'email': '$username@example.com',
    'nombre': 'Usuario',
    'role': 'ADMIN',
    'activo': true,
  });
}

Future<CatalogosService> _catalogosCargados() async {
  final servicio = CatalogosService(
    crearApiSimulada(
      (request) async => http.Response(
        jsonEncode([
          {
            'nombre': 'roles',
            'etiqueta': 'Roles de usuario',
            'valores': ['ADMIN', 'RECEPCION'],
          },
        ]),
        200,
      ),
    ),
  );
  await servicio.asegurarCargado();
  return servicio;
}

Widget _envoltura(UsuariosService servicio, CatalogosService catalogos) {
  return MaterialApp(
    home: Scaffold(
      body: UsuariosView(service: servicio, catalogos: catalogos),
    ),
  );
}

void main() {
  testWidgets('lista los usuarios', (tester) async {
    final servicio = UsuariosService(
      crearApiSimulada((request) async {
        return http.Response(
          jsonEncode({
            'items': [
              jsonDecode(_usuarioJson()),
              jsonDecode(_usuarioJson(id: 2, username: 'recepcion')),
            ],
            'total': 2,
            'pagina': 1,
            'tamano': 20,
          }),
          200,
        );
      }),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();

    expect(find.text('admin'), findsOneWidget);
    expect(find.text('recepcion'), findsOneWidget);
    expect(find.text('ACTIVO'), findsNWidgets(2));
  });

  testWidgets('el filtro solo activos se envia correctamente', (tester) async {
    final consultas = <String?>[];
    final servicio = UsuariosService(
      crearApiSimulada((request) async {
        consultas.add(request.url.queryParameters['soloActivos']);
        return http.Response(
          jsonEncode({
            'items': <dynamic>[],
            'total': 0,
            'pagina': 1,
            'tamano': 20,
          }),
          200,
        );
      }),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Solo activos'));
    await tester.pumpAndSettle();

    expect(consultas, [null, 'true']);
  });

  testWidgets('muestra error y boton de reintentar', (tester) async {
    final servicio = UsuariosService(
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

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();

    expect(find.text('Reintentar'), findsOneWidget);
  });

  testWidgets('abre el dialogo de nuevo usuario', (tester) async {
    final servicio = UsuariosService(
      crearApiSimulada((request) async {
        return http.Response(
          jsonEncode({
            'items': <dynamic>[],
            'total': 0,
            'pagina': 1,
            'tamano': 20,
          }),
          200,
        );
      }),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Nuevo usuario'));
    await tester.pumpAndSettle();

    expect(find.text('Guardar'), findsOneWidget);
    expect(find.text('Username'), findsOneWidget);
  });
}
