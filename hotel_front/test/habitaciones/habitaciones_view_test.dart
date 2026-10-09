import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/catalogos/catalogos_service.dart';
import 'package:hotel_front/habitaciones/habitaciones_service.dart';
import 'package:hotel_front/habitaciones/habitaciones_view.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

const _catalogosJson = [
  {
    'nombre': 'estados_habitacion',
    'etiqueta': 'Estados de habitacion',
    'valores': ['DISPONIBLE', 'OCUPADA', 'MANTENIMIENTO'],
  },
  {
    'nombre': 'tipos_habitacion',
    'etiqueta': 'Tipos de habitacion',
    'valores': ['SIMPLE', 'DOBLE', 'SUITE'],
  },
];

String _habitacionJson({
  int id = 1,
  int numero = 101,
  String estado = 'DISPONIBLE',
}) {
  return jsonEncode({
    'id': id,
    'numero': numero,
    'tipo': 'DOBLE',
    'capacidad': 2,
    'precioPorNoche': 120.5,
    'estado': estado,
    'limpieza': 'LIMPIA',
    'descripcion': null,
  });
}

Future<CatalogosService> _catalogosCargados() async {
  final servicio = CatalogosService(
    crearApiSimulada(
      (request) async => http.Response(jsonEncode(_catalogosJson), 200),
    ),
  );
  await servicio.asegurarCargado();
  return servicio;
}

Widget _envoltura(
  HabitacionesService servicio,
  CatalogosService catalogos, {
  bool esAdmin = false,
}) {
  return MaterialApp(
    home: Scaffold(
      body: HabitacionesView(
        service: servicio,
        catalogos: catalogos,
        esAdmin: esAdmin,
      ),
    ),
  );
}

void main() {
  testWidgets('lista las habitaciones en tarjetas', (tester) async {
    final servicio = HabitacionesService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode([
            jsonDecode(_habitacionJson()),
            jsonDecode(_habitacionJson(id: 2, numero: 102, estado: 'OCUPADA')),
          ]),
          200,
        ),
      ),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();

    expect(find.text('#101'), findsOneWidget);
    expect(find.text('#102'), findsOneWidget);
    expect(find.text('Habitaciones'), findsOneWidget);
  });

  testWidgets('muestra error y boton de reintentar', (tester) async {
    final servicio = HabitacionesService(
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

  testWidgets('admin abre el formulario de nueva habitacion', (tester) async {
    final servicio = HabitacionesService(
      crearApiSimulada((request) async => http.Response('[]', 200)),
    );

    await tester.pumpWidget(
      _envoltura(servicio, await _catalogosCargados(), esAdmin: true),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Nueva habitacion'));
    await tester.pumpAndSettle();

    expect(find.text('Guardar'), findsOneWidget);
    expect(find.text('Numero'), findsOneWidget);
  });

  testWidgets('recepcion no ve el boton de nueva habitacion', (tester) async {
    final servicio = HabitacionesService(
      crearApiSimulada((request) async => http.Response('[]', 200)),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();

    expect(find.text('Nueva habitacion'), findsNothing);
  });
}
