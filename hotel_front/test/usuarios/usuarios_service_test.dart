import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/core/network/api_exception.dart';
import 'package:hotel_front/usuarios/models/usuario_payload.dart';
import 'package:hotel_front/usuarios/usuarios_service.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

String _usuarioJson({
  int id = 1,
  String username = 'admin',
  bool activo = true,
}) {
  return jsonEncode({
    'id': id,
    'username': username,
    'email': '$username@example.com',
    'nombre': 'Administrador',
    'role': 'ADMIN',
    'activo': activo,
  });
}

void main() {
  test(
    'listar parsea la pagina y envia soloActivos solo cuando se pide',
    () async {
      final consultas = <Uri>[];
      final servicio = UsuariosService(
        crearApiSimulada((request) async {
          consultas.add(request.url);
          return http.Response(
            jsonEncode({
              'items': [jsonDecode(_usuarioJson())],
              'total': 1,
              'pagina': 1,
              'tamano': 20,
            }),
            200,
          );
        }),
      );

      final pagina = await servicio.listar(q: 'admin', soloActivos: true);

      expect(pagina.items.first.username, 'admin');
      expect(consultas.last.path, '/api/usuarios');
      expect(consultas.last.queryParameters['soloActivos'], 'true');

      await servicio.listar();
      expect(
        consultas.last.queryParameters.containsKey('soloActivos'),
        isFalse,
      );
    },
  );

  test('crear envia el cuerpo con la contrasena', () async {
    http.Request? capturado;
    final servicio = UsuariosService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(_usuarioJson(), 201);
      }),
    );

    await servicio.crear(
      const UsuarioCrear(
        username: 'recepcion1',
        email: 'rec@example.com',
        nombre: 'Recepcion',
        password: 'clave-fuerte-1',
        role: 'RECEPCION',
      ),
    );

    final cuerpo = jsonDecode(capturado!.body) as Map<String, dynamic>;
    expect(cuerpo['username'], 'recepcion1');
    expect(cuerpo['password'], 'clave-fuerte-1');
    expect(cuerpo['role'], 'RECEPCION');
  });

  test('desactivar y reactivar usan los subendpoints correctos', () async {
    final rutas = <String>[];
    final servicio = UsuariosService(
      crearApiSimulada((request) async {
        rutas.add('${request.method} ${request.url.path}');
        return http.Response(_usuarioJson(activo: rutas.length == 1), 200);
      }),
    );

    await servicio.desactivar(3);
    await servicio.reactivar(3);

    expect(rutas, [
      'POST /api/usuarios/3/desactivar',
      'POST /api/usuarios/3/reactivar',
    ]);
  });

  test(
    'un 409 de username/email duplicado se propaga como ApiException',
    () async {
      final servicio = UsuariosService(
        crearApiSimulada(
          (request) async => http.Response(
            jsonEncode({
              'detail': 'El username ya existe',
              'code': 'CONFLICTO',
            }),
            409,
          ),
        ),
      );

      await expectLater(
        servicio.crear(
          const UsuarioCrear(
            username: 'admin',
            email: 'a@a.com',
            nombre: 'A',
            password: 'clave-fuerte-1',
            role: 'ADMIN',
          ),
        ),
        throwsA(
          isA<ApiException>()
              .having((e) => e.statusCode, 'statusCode', 409)
              .having((e) => e.codigo, 'codigo', 'CONFLICTO'),
        ),
      );
    },
  );
}
