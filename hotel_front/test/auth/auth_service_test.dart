import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/auth/auth_service.dart';
import 'package:hotel_front/auth/auth_storage.dart';
import 'package:hotel_front/auth/models/auth_token_response.dart';
import 'package:hotel_front/auth/models/login_request.dart';
import 'package:hotel_front/config/app_config.dart';
import 'package:hotel_front/core/network/api_client.dart';
import 'package:hotel_front/core/network/api_exception.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

ApiClient _api(MockClientHandler handler) {
  return ApiClient(
    config: AppConfig(baseUrl: 'http://localhost:8000'),
    cliente: MockClient(handler),
  );
}

AuthService _servicio(ApiClient api) {
  final auth = AuthService(api: api, storage: AuthStorage());
  api.sesion = auth;
  return auth;
}

String _tokensJson({String access = 'access-1', String refresh = 'refresh-1'}) {
  return jsonEncode({
    'token': access,
    'refreshToken': refresh,
    'tokenType': 'bearer',
    'expiresIn': 1800,
  });
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => SharedPreferences.setMockInitialValues({}));

  test('iniciarSesion guarda tokens y devuelve el usuario', () async {
    final api = _api(
      (request) async => http.Response(
        jsonEncode({
          'token': 'access-1',
          'refreshToken': 'refresh-1',
          'tokenType': 'bearer',
          'expiresIn': 1800,
          'id': 1,
          'username': 'admin',
          'email': 'admin@example.com',
          'nombre': 'Admin',
          'role': 'ADMIN',
          'activo': true,
        }),
        200,
      ),
    );
    final auth = _servicio(api);

    final usuario = await auth.iniciarSesion(
      const LoginRequest(username: 'admin', password: 'secreto'),
    );

    expect(usuario.id, 1);
    expect(usuario.esAdministrador, isTrue);
    expect(auth.accessToken, 'access-1');
    final guardado = await auth.storage.leer();
    expect(guardado!.refreshToken, 'refresh-1');
  });

  test('iniciarSesion fallido no persiste tokens', () async {
    final api = _api(
      (request) async => http.Response(
        jsonEncode({
          'detail': 'Credenciales incorrectas',
          'code': 'NO_AUTORIZADO',
        }),
        401,
      ),
    );
    final auth = _servicio(api);

    await expectLater(
      auth.iniciarSesion(const LoginRequest(email: 'a@a.com', password: 'x')),
      throwsA(isA<ApiException>()),
    );
    expect(await auth.storage.leer(), isNull);
    expect(auth.accessToken, isNull);
  });

  test('refresh rota y persiste el nuevo par de tokens', () async {
    final api = _api(
      (request) async => http.Response(
        _tokensJson(access: 'access-2', refresh: 'refresh-2'),
        200,
      ),
    );
    final auth = _servicio(api);
    await auth.storage.guardar(
      const AuthTokenResponse(
        accessToken: 'access-1',
        refreshToken: 'refresh-1',
      ),
    );
    await auth.restaurarSesion();

    final renovado = await auth.refrescar();

    expect(renovado, isTrue);
    expect(auth.accessToken, 'access-2');
    expect((await auth.storage.leer())!.refreshToken, 'refresh-2');
  });

  test('restaurarSesion carga los tokens persistidos', () async {
    final api = _api((request) async => http.Response('{}', 200));
    final auth = _servicio(api);
    await auth.storage.guardar(
      const AuthTokenResponse(
        accessToken: 'access-1',
        refreshToken: 'refresh-1',
      ),
    );

    final habia = await auth.restaurarSesion();

    expect(habia, isTrue);
    expect(auth.accessToken, 'access-1');
  });

  test('usuarioActual consulta /api/auth/me', () async {
    final api = _api(
      (request) async => http.Response(
        jsonEncode({
          'id': 2,
          'username': 'recepcion',
          'email': 'recepcion@example.com',
          'nombre': 'Recepcion',
          'role': 'RECEPCION',
          'activo': true,
        }),
        200,
      ),
    );
    final auth = _servicio(api);

    final usuario = await auth.usuarioActual();

    expect(usuario.role, 'RECEPCION');
    expect(usuario.esAdministrador, isFalse);
  });

  test('cerrarSesion revoca y limpia la sesion local', () async {
    String? refreshEnviado;
    final api = _api((request) async {
      if (request.url.path == '/api/auth/logout') {
        refreshEnviado = jsonDecode(request.body)['refreshToken'] as String?;
        return http.Response('', 204);
      }
      return http.Response('', 500);
    });
    final auth = _servicio(api);
    await auth.storage.guardar(
      const AuthTokenResponse(accessToken: 'a', refreshToken: 'refresh-1'),
    );
    await auth.restaurarSesion();

    await auth.cerrarSesion();

    expect(refreshEnviado, 'refresh-1');
    expect(await auth.storage.leer(), isNull);
    expect(auth.accessToken, isNull);
  });

  test('cerrarSesion limpia la sesion local aunque el logout falle', () async {
    final api = _api(
      (request) async => http.Response(
        jsonEncode({
          'detail': 'Refresh token invalido',
          'code': 'REFRESH_TOKEN_INVALIDO',
        }),
        401,
      ),
    );
    final auth = _servicio(api);
    await auth.storage.guardar(
      const AuthTokenResponse(accessToken: 'a', refreshToken: 'r'),
    );
    await auth.restaurarSesion();

    await auth.cerrarSesion();

    expect(await auth.storage.leer(), isNull);
  });
}
