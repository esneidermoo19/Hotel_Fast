import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/core/network/api_exception.dart';
import 'package:hotel_front/reservas/models/reserva.dart';
import 'package:hotel_front/reservas/reservas_service.dart';
import 'package:http/http.dart' as http;

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

void main() {
  test('listar parsea la pagina y envia filtros de estado y fechas', () async {
    Uri? uri;
    final servicio = ReservasService(
      crearApiSimulada((request) async {
        uri = request.url;
        return http.Response(_paginaJson(estado: 'CONFIRMADA'), 200);
      }),
    );

    final pagina = await servicio.listar(
      estado: 'CONFIRMADA',
      desde: DateTime(2026, 10, 1),
      hasta: DateTime(2026, 10, 31),
    );

    expect(pagina.items.first.codigo, 'RES-001');
    expect(pagina.items.first.estado, 'CONFIRMADA');
    expect(pagina.items.first.huesped.nombreCompleto, 'Ana Gomez');
    expect(pagina.items.first.fechaEntrada, DateTime(2026, 10, 10));
    expect(uri!.path, '/api/reservas');
    expect(uri!.queryParameters, {
      'pagina': '1',
      'tamano': '20',
      'estado': 'CONFIRMADA',
      'desde': '2026-10-01',
      'hasta': '2026-10-31',
    });
  });

  test('disponibilidad parsea las habitaciones y consulta el rango', () async {
    Uri? uri;
    final servicio = ReservasService(
      crearApiSimulada((request) async {
        uri = request.url;
        return http.Response(
          jsonEncode([
            {
              'id': 1,
              'numero': 101,
              'tipo': 'DOBLE',
              'capacidad': 2,
              'precioPorNoche': 120.5,
            },
          ]),
          200,
        );
      }),
    );

    final disponibles = await servicio.disponibilidad(
      DisponibilidadConsulta(
        entrada: DateTime(2026, 10, 10),
        salida: DateTime(2026, 10, 12),
        huespedes: 2,
      ),
    );

    expect(disponibles, hasLength(1));
    expect(disponibles.first.numero, 101);
    expect(uri!.path, '/api/reservas/disponibilidad');
    expect(uri!.queryParameters, {
      'entrada': '2026-10-10',
      'salida': '2026-10-12',
      'huespedes': '2',
    });
  });

  test('crear envia el cuerpo con las fechas formateadas', () async {
    http.Request? capturado;
    final servicio = ReservasService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(_reservaJson(), 201);
      }),
    );

    final creada = await servicio.crear(
      CrearReservaRequest(
        huespedId: 1,
        habitacionId: 1,
        fechaEntrada: DateTime(2026, 10, 10),
        fechaSalida: DateTime(2026, 10, 12),
        numeroHuespedes: 2,
      ),
    );

    expect(capturado!.url.path, '/api/reservas');
    final cuerpo = jsonDecode(capturado!.body) as Map<String, dynamic>;
    expect(cuerpo['fechaEntrada'], '2026-10-10');
    expect(cuerpo['fechaSalida'], '2026-10-12');
    expect(cuerpo['huespedId'], 1);
    expect(cuerpo['habitacionId'], 1);
    expect(creada.codigo, 'RES-001');
  });

  test('checkOut parsea el resultado economico', () async {
    final servicio = ReservasService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            ...jsonDecode(_reservaJson(estado: 'CHECK_OUT')),
            'totalCuenta': 300.0,
            'totalPagado': 100.0,
            'saldoPendiente': 200.0,
          }),
          200,
        ),
      ),
    );

    final resultado = await servicio.checkOut(1);

    expect(resultado.reserva.estado, 'CHECK_OUT');
    expect(resultado.totalCuenta, 300.0);
    expect(resultado.saldoPendiente, 200.0);
  });

  test('cancelar envia el motivo y extender la nueva fecha', () async {
    final rutas = <http.Request>[];
    final servicio = ReservasService(
      crearApiSimulada((request) async {
        rutas.add(request);
        return http.Response(_reservaJson(estado: 'CANCELADA'), 200);
      }),
    );

    final cancelada = await servicio.cancelar(1, 'Cambio de planes');
    final extendida = await servicio.extender(1, DateTime(2026, 10, 15));

    final cuerpoCancelar = jsonDecode(rutas[0].body) as Map<String, dynamic>;
    expect(rutas[0].url.path, '/api/reservas/1/cancelar');
    expect(cuerpoCancelar['motivo'], 'Cambio de planes');
    expect(cancelada.estado, 'CANCELADA');

    final cuerpoExtender = jsonDecode(rutas[1].body) as Map<String, dynamic>;
    expect(rutas[1].url.path, '/api/reservas/1/extender');
    expect(cuerpoExtender['nuevaFechaSalida'], '2026-10-15');
    expect(extendida.estado, 'CANCELADA');
  });

  test('un 409 REGLA_NEGOCIO se propaga como ApiException', () async {
    final servicio = ReservasService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            'detail': 'La habitacion no esta disponible en el rango',
            'code': 'REGLA_NEGOCIO',
          }),
          409,
        ),
      ),
    );

    await expectLater(
      servicio.crear(
        CrearReservaRequest(
          huespedId: 1,
          habitacionId: 1,
          fechaEntrada: DateTime(2026, 10, 10),
          fechaSalida: DateTime(2026, 10, 12),
          numeroHuespedes: 1,
        ),
      ),
      throwsA(
        isA<ApiException>()
            .having((e) => e.statusCode, 'statusCode', 409)
            .having((e) => e.codigo, 'codigo', 'REGLA_NEGOCIO'),
      ),
    );
  });
}
