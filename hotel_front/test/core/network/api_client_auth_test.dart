import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/auth/auth_service.dart';
import 'package:hotel_front/auth/auth_storage.dart';
import 'package:hotel_front/auth/models/auth_token_response.dart';
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

Future<AuthService> _sesionConTokens(ApiClient api) async {
  final auth = AuthService(api: api, storage: AuthStorage());
  api.sesion = auth;
  await auth.storage.guardar(
    const AuthTokenResponse(accessToken: 'access-1', refreshToken: 'refresh-1'),
  );
  await auth.restaurarSesion();
  return auth;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => SharedPreferences.setMockInitialValues({}));

  test('adjunta la cabecera Bearer con el access token', () async {
    String? autorizacion;
    final api = _api((request) async {
      autorizacion = request.headers['Authorization'];
      return http.Response('{}', 200);
    });
    await _sesionConTokens(api);

    await api.get('/api/huespedes');

    expect(autorizacion, 'Bearer access-1');
  });

  test('ante 401 renueva y reintenta con el token nuevo', () async {
    var protegidas = 0;
    String? ultimaAutorizacion;
    final api = _api((request) async {
      if (request.url.path == '/api/auth/refresh') {
        return http.Response(
          jsonEncode({
            'token': 'access-2',
            'refreshToken': 'refresh-2',
            'tokenType': 'bearer',
            'expiresIn': 1800,
          }),
          200,
        );
      }
      protegidas++;
      ultimaAutorizacion = request.headers['Authorization'];
      if (ultimaAutorizacion == 'Bearer access-1') {
        return http.Response(
          jsonEncode({
            'detail': 'Token de acceso invalido',
            'code': 'TOKEN_INVALIDO',
          }),
          401,
        );
      }
      return http.Response(jsonEncode({'ok': true}), 200);
    });
    final auth = await _sesionConTokens(api);

    final data = await api.get('/api/huespedes');

    expect(data, {'ok': true});
    expect(protegidas, 2);
    expect(ultimaAutorizacion, 'Bearer access-2');
    expect((await auth.storage.leer())!.refreshToken, 'refresh-2');
  });

  test('si la renovacion falla limpia la sesion y relanza el 401', () async {
    final api = _api((request) async {
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
        jsonEncode({
          'detail': 'Token de acceso invalido',
          'code': 'TOKEN_INVALIDO',
        }),
        401,
      );
    });
    final auth = await _sesionConTokens(api);

    await expectLater(
      api.get('/api/huespedes'),
      throwsA(
        isA<ApiException>().having((e) => e.statusCode, 'statusCode', 401),
      ),
    );
    expect(await auth.storage.leer(), isNull);
    expect(auth.accessToken, isNull);
  });

  test('no intenta renovar en el propio endpoint de login', () async {
    var refrescos = 0;
    final api = _api((request) async {
      if (request.url.path == '/api/auth/refresh') {
        refrescos++;
      }
      return http.Response(
        jsonEncode({
          'detail': 'Credenciales incorrectas',
          'code': 'NO_AUTORIZADO',
        }),
        401,
      );
    });

    await expectLater(
      api.post(
        '/api/auth/login',
        body: const {'username': 'x', 'password': 'y'},
        renovarEn401: false,
      ),
      throwsA(isA<ApiException>()),
    );

    expect(refrescos, 0);
  });
}
