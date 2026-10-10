import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/catalogos/catalogos_service.dart';
import 'package:hotel_front/consumos/consumos_service.dart';
import 'package:hotel_front/cuentas/cuentas_service.dart';
import 'package:hotel_front/huespedes/huespedes_service.dart';
import 'package:hotel_front/pagos/pagos_service.dart';
import 'package:hotel_front/reservas/reservas_service.dart';
import 'package:hotel_front/reservas/reservas_view.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import '../support/auth_test_utils.dart';

String _reservaJson({String estado = 'PENDIENTE', String codigo = 'RES-001'}) {
  return jsonEncode({
    'id': 1,
    'codigo': codigo,
    'huesped': {
      'id': 1,
      'nombres': 'Ana',
      'apellidos': 'Gomez',
      'tipoDocumento': 'CC',
      'numeroDocumento': '12345678',
    },
    'habitacion': {
      'id': 1,
      'numero': 101,
      'tipo': 'DOBLE',
      'capacidad': 2,
      'precioPorNoche': 120.5,
    },
    'fechaEntrada': '2026-10-10',
    'fechaSalida': '2026-10-12',
    'numeroHuespedes': 2,
    'estado': estado,
    'precioNocheAplicado': 120.5,
    'totalEstimado': 241.0,
    'observaciones': null,
    'motivoCancelacion': null,
    'checkInReal': null,
    'checkOutReal': null,
    'creadaPor': 1,
  });
}

String _paginaJson({String estado = 'PENDIENTE'}) {
  return jsonEncode({
    'items': [jsonDecode(_reservaJson(estado: estado))],
    'total': 1,
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
            'nombre': 'estados_reserva',
            'etiqueta': 'Estados de reserva',
            'valores': [
              'PENDIENTE',
              'CONFIRMADA',
              'CHECK_IN',
              'CHECK_OUT',
              'CANCELADA',
              'NO_SHOW',
            ],
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
  ReservasService servicio,
  CatalogosService catalogos, {
  MockClientHandler? cuentaHandler,
}) {
  final huespedes = HuespedesService(
    crearApiSimulada((request) async {
      return http.Response(
        jsonEncode({
          'items': <dynamic>[],
          'total': 0,
          'pagina': 1,
          'tamano': 5,
        }),
        200,
      );
    }),
  );
  final cuentas = CuentasService(
    crearApiSimulada(
      cuentaHandler ?? (request) async => http.Response('{}', 200),
    ),
  );
  final consumos = ConsumosService(
    crearApiSimulada((request) async => http.Response('{}', 201)),
  );
  final pagos = PagosService(
    crearApiSimulada((request) async => http.Response('{}', 201)),
  );
  return MaterialApp(
    home: Scaffold(
      body: ReservasView(
        service: servicio,
        catalogos: catalogos,
        huespedes: huespedes,
        cuentas: cuentas,
        consumos: consumos,
        pagos: pagos,
      ),
    ),
  );
}

void main() {
  testWidgets('lista las reservas con codigo y huesped', (tester) async {
    final servicio = ReservasService(
      crearApiSimulada((request) async => http.Response(_paginaJson(), 200)),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();

    expect(find.text('RES-001'), findsOneWidget);
    expect(find.text('Ana Gomez'), findsOneWidget);
    expect(find.textContaining('Página 1 de 1'), findsOneWidget);
  });

  testWidgets('el filtro de estado re-consulta', (tester) async {
    final estados = <String?>[];
    final servicio = ReservasService(
      crearApiSimulada((request) async {
        estados.add(request.url.queryParameters['estado']);
        return http.Response(_paginaJson(), 200);
      }),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();
    await tester.tap(find.widgetWithText(ChoiceChip, 'Confirmada'));
    await tester.pumpAndSettle();

    expect(estados, [null, 'CONFIRMADA']);
  });

  testWidgets('muestra error y boton de reintentar', (tester) async {
    final servicio = ReservasService(
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

  testWidgets('el detalle muestra acciones segun el estado', (tester) async {
    final servicio = ReservasService(
      crearApiSimulada(
        (request) async => http.Response(_paginaJson(estado: 'PENDIENTE'), 200),
      ),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();
    await tester.tap(find.text('RES-001'));
    await tester.pumpAndSettle();

    expect(find.text('Confirmar'), findsOneWidget);
    expect(find.text('Cancelar'), findsOneWidget);
  });

  testWidgets('abre el dialogo de nueva reserva', (tester) async {
    final servicio = ReservasService(
      crearApiSimulada((request) async => http.Response(_paginaJson(), 200)),
    );

    await tester.pumpWidget(_envoltura(servicio, await _catalogosCargados()));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Nueva reserva'));
    await tester.pumpAndSettle();

    expect(find.text('Crear reserva'), findsOneWidget);
    expect(find.text('Ver disponibilidad'), findsOneWidget);
  });

  testWidgets('el detalle muestra la cuenta de la reserva', (tester) async {
    final servicio = ReservasService(
      crearApiSimulada(
        (request) async => http.Response(_paginaJson(estado: 'CHECK_IN'), 200),
      ),
    );

    await tester.pumpWidget(
      _envoltura(
        servicio,
        await _catalogosCargados(),
        cuentaHandler: _cuentaJson,
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('RES-001'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Cuenta y pagos'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Cuenta y pagos'));
    await tester.pumpAndSettle();

    expect(find.text('Total cuenta'), findsOneWidget);
    expect(find.text('Saldo pendiente'), findsOneWidget);
    expect(find.text('Registrar consumo'), findsOneWidget);
    expect(find.text('Registrar pago'), findsOneWidget);
    expect(find.text('Minibar'), findsOneWidget);
  });
}

Future<http.Response> _cuentaJson(http.Request request) async {
  return http.Response(
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
          'fechaPago': '2026-10-10T14:00:00Z',
        },
      ],
    }),
    200,
  );
}
