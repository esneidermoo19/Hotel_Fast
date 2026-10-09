import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/catalogos/catalogos_service.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

String _catalogosJson() {
  return jsonEncode([
    {
      'nombre': 'estados_reserva',
      'etiqueta': 'Estados de reserva',
      'valores': ['PENDIENTE', 'CONFIRMADA', 'CHECK_IN', 'CANCELADA'],
    },
    {
      'nombre': 'tipos_documento',
      'etiqueta': 'Tipos de documento',
      'valores': ['CC', 'CE', 'PASAPORTE'],
    },
  ]);
}

void main() {
  test('asegurarCargado carga, cachea y no repite la peticion', () async {
    var llamadas = 0;
    final servicio = CatalogosService(
      crearApiSimulada((request) async {
        llamadas++;
        return http.Response(_catalogosJson(), 200);
      }),
    );

    await servicio.asegurarCargado();
    expect(servicio.obtener('estados_reserva')!.valores, contains('CHECK_IN'));
    expect(servicio.valores('tipos_documento'), contains('CC'));

    await servicio.asegurarCargado();
    expect(llamadas, 1);
  });

  test('asegurarCargado comparte la carga concurrente', () async {
    var llamadas = 0;
    final servicio = CatalogosService(
      crearApiSimulada((request) async {
        llamadas++;
        await Future<void>.delayed(const Duration(milliseconds: 20));
        return http.Response(_catalogosJson(), 200);
      }),
    );

    await Future.wait([servicio.asegurarCargado(), servicio.asegurarCargado()]);

    expect(llamadas, 1);
  });

  test('precargar no lanza si la peticion falla', () async {
    final servicio = CatalogosService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({'detail': 'Error', 'code': 'ERROR_INTERNO'}),
          500,
        ),
      ),
    );

    await servicio.precargar();

    expect(servicio.cargado, isFalse);
  });
}
