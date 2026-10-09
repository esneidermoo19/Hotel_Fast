import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/auditoria/auditoria_service.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

String _registro() {
  return jsonEncode({
    'id': 1,
    'usuarioId': 2,
    'accion': 'CREATE',
    'entidad': 'Reserva',
    'entidadId': 9,
    'ip': '127.0.0.1',
    'detalle': {'codigo': 'RES-1'},
    'createdAt': '2026-10-09T14:30:00Z',
  });
}

void main() {
  test('listar parsea los registros y envia los filtros', () async {
    Uri? uri;
    final servicio = AuditoriaService(
      crearApiSimulada((request) async {
        uri = request.url;
        return http.Response(
          jsonEncode({
            'items': [jsonDecode(_registro())],
            'total': 1,
            'pagina': 1,
            'tamano': 20,
          }),
          200,
        );
      }),
    );

    final pagina = await servicio.listar(
      entidad: 'Reserva',
      desde: DateTime(2026, 10, 1),
    );

    final registro = pagina.items.single;
    expect(registro.accion, 'CREATE');
    expect(registro.entidad, 'Reserva');
    expect(registro.usuarioId, 2);
    expect(registro.detalle?['codigo'], 'RES-1');
    expect(registro.createdAt, DateTime.utc(2026, 10, 9, 14, 30));
    expect(uri!.path, '/api/auditoria');
    expect(uri!.queryParameters, {
      'pagina': '1',
      'tamano': '20',
      'entidad': 'Reserva',
      'desde': '2026-10-01',
    });
  });

  test(
    'un registro sin usuario ni detalle se parsea con valores nulos',
    () async {
      final servicio = AuditoriaService(
        crearApiSimulada(
          (request) async => http.Response(
            jsonEncode({
              'items': [
                {
                  'id': 2,
                  'accion': 'LOGIN',
                  'entidad': 'auth',
                  'createdAt': '2026-10-09T14:30:00Z',
                },
              ],
              'total': 1,
              'pagina': 1,
              'tamano': 20,
            }),
            200,
          ),
        ),
      );

      final pagina = await servicio.listar();

      expect(pagina.items.single.usuarioId, isNull);
      expect(pagina.items.single.detalle, isNull);
      expect(pagina.items.single.resumenDetalle, isEmpty);
    },
  );
}
