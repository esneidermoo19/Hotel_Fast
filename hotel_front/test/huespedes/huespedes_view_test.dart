import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/catalogos/catalogos_service.dart';
import 'package:hotel_front/huespedes/huespedes_service.dart';
import 'package:hotel_front/huespedes/huespedes_view.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

String _huespedJson({
  int id = 1,
  String nombres = 'Ana',
  String apellidos = 'Gomez',
}) {
  return jsonEncode({
    'id': id,
    'tipoDocumento': 'CC',
    'numeroDocumento': '1234567$id',
    'nombres': nombres,
    'apellidos': apellidos,
    'email': 'ana@example.com',
    'telefono': null,
    'nacionalidad': null,
    'fechaNacimiento': null,
    'direccion': null,
    'observaciones': null,
  });
}

String _paginaJson(int total) {
  return jsonEncode({
    'items': [
      jsonDecode(_huespedJson()),
      jsonDecode(_huespedJson(id: 2, nombres: 'Luis', apellidos: 'Rojas')),
    ],
    'total': total,
    'pagina': 1,
    'tamano': 20,
  });
}

Future<CatalogosService> _catalogosCargados() async {
  final servicio = CatalogosService(
    crearApiSimulada(
      (request) async => http.Response(
        jsonEncode([
          {
            'nombre': 'tipos_documento',
            'etiqueta': 'Tipos de documento',
            'valores': ['CC', 'CE', 'PASAPORTE', 'TI'],
          },
        ]),
        200,
      ),
    ),
  );
  await servicio.asegurarCargado();
  return servicio;
}

Widget _envoltura(
  HuespedesService servicio,
  CatalogosService catalogos, {
  bool esAdmin = false,
}) {
  return MaterialApp(
    home: Scaffold(
      body: HuespedesView(
        service: servicio,
        catalogos: catalogos,
        esAdmin: esAdmin,
      ),
    ),
  );
}

void main() {
  testWidgets('lista paginada con los huespedes', (tester) async {
    final servicio = HuespedesService(
      crearApiSimulada((request) async => http.Response(_paginaJson(2), 200)),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();

    expect(find.text('Ana Gomez'), findsOneWidget);
    expect(find.text('Luis Rojas'), findsOneWidget);
    expect(find.textContaining('Pagina 1 de 1'), findsOneWidget);
  });

  testWidgets('la busqueda reconsulta con q', (tester) async {
    final busquedas = <String?>[];
    final servicio = HuespedesService(
      crearApiSimulada((request) async {
        busquedas.add(request.url.queryParameters['q']);
        return http.Response(_paginaJson(1), 200);
      }),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), 'ana');
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();

    expect(busquedas, [null, 'ana']);
  });

  testWidgets('muestra error y boton de reintentar', (tester) async {
    final servicio = HuespedesService(
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

    expect(find.text('Error de base de datos'), findsOneWidget);
    expect(find.text('Reintentar'), findsOneWidget);
  });

  testWidgets('admin abre el formulario de nuevo huesped', (tester) async {
    final servicio = HuespedesService(
      crearApiSimulada((request) async => http.Response(_paginaJson(0), 200)),
    );

    await tester.pumpWidget(
      _envoltura(servicio, await _catalogosCargados(), esAdmin: true),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Nuevo huesped'));
    await tester.pumpAndSettle();

    expect(find.text('Guardar'), findsOneWidget);
    expect(find.text('Tipo de documento'), findsOneWidget);
  });

  testWidgets('recepcion no ve el boton de nuevo huesped', (tester) async {
    final servicio = HuespedesService(
      crearApiSimulada((request) async => http.Response(_paginaJson(0), 200)),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();

    expect(find.text('Nuevo huesped'), findsNothing);
  });
}
