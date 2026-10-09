import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/auth/auth_controller.dart';
import 'package:hotel_front/auth/models/auth_token_response.dart';
import 'package:hotel_front/auth/models/login_request.dart';
import 'package:hotel_front/core/network/api_exception.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../support/auth_test_utils.dart';

const _credenciales = LoginRequest(username: 'usuario', password: 'secreto');

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => SharedPreferences.setMockInitialValues({}));

  test('restaurar sin tokens queda en sinSesion', () async {
    final controller = crearControladorAuth(
      (request) async => http.Response('{}', 200),
    );

    await controller.restaurar();

    expect(controller.estado, EstadoAuth.sinSesion);
    expect(controller.usuario, isNull);
  });

  test('restaurar con tokens persistidos carga el usuario', () async {
    final controller = crearControladorAuth(
      (request) async => http.Response(loginJson(), 200),
    );
    await controller.auth.storage.guardar(
      const AuthTokenResponse(accessToken: 'a', refreshToken: 'r'),
    );

    await controller.restaurar();

    expect(controller.estado, EstadoAuth.autenticado);
    expect(controller.usuario!.esAdministrador, isTrue);
  });

  test('iniciarSesion exitoso autentica al usuario', () async {
    final controller = crearControladorAuth(
      (request) async => http.Response(loginJson(), 200),
    );

    await controller.iniciarSesion(_credenciales);

    expect(controller.estado, EstadoAuth.autenticado);
    expect(controller.usuario!.nombre, 'Usuario Prueba');
    expect(controller.error, isNull);
    expect(controller.enviando, isFalse);
  });

  test('iniciarSesion con 401 expone error y no autentica', () async {
    final controller = crearControladorAuth(
      (request) async => http.Response(
        jsonEncode({
          'detail': 'Credenciales incorrectas',
          'code': 'NO_AUTORIZADO',
        }),
        401,
      ),
    );

    await controller.iniciarSesion(_credenciales);

    expect(controller.estado, EstadoAuth.sinSesion);
    expect(controller.error!.statusCode, 401);
    expect(controller.enviando, isFalse);
  });

  test('cerrarSesion vuelve a sinSesion y limpia los tokens', () async {
    final controller = crearControladorAuth((request) async {
      if (request.url.path == '/api/auth/logout') {
        return http.Response('', 204);
      }
      return http.Response(loginJson(role: 'RECEPCION'), 200);
    });
    await controller.iniciarSesion(_credenciales);
    expect(controller.estado, EstadoAuth.autenticado);

    await controller.cerrarSesion();

    expect(controller.estado, EstadoAuth.sinSesion);
    expect(await controller.auth.storage.leer(), isNull);
  });

  test(
    'si el refresco falla durante una llamada, vuelve a sinSesion',
    () async {
      final controller = crearControladorAuth((request) async {
        if (request.url.path == '/api/auth/login') {
          return http.Response(loginJson(), 200);
        }
        if (request.url.path == '/api/auth/refresh') {
          return http.Response(
            jsonEncode({
              'detail': 'Refresh token invalido',
              'code': 'REFRESH_TOKEN_INVALIDO',
            }),
            401,
          );
        }
        return http.Response(
          jsonEncode({'detail': 'Token invalido', 'code': 'TOKEN_INVALIDO'}),
          401,
        );
      });
      await controller.iniciarSesion(_credenciales);
      expect(controller.estado, EstadoAuth.autenticado);

      await expectLater(
        controller.auth.usuarioActual(),
        throwsA(isA<ApiException>()),
      );

      expect(controller.estado, EstadoAuth.sinSesion);
      expect(await controller.auth.storage.leer(), isNull);
    },
  );
}
