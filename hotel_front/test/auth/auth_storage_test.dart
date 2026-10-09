import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/auth/auth_storage.dart';
import 'package:hotel_front/auth/models/auth_token_response.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => SharedPreferences.setMockInitialValues({}));

  test('sin datos guardados devuelve null', () async {
    expect(await AuthStorage().leer(), isNull);
  });

  test('guarda y recupera los tokens', () async {
    final storage = AuthStorage();

    await storage.guardar(
      const AuthTokenResponse(
        accessToken: 'access-1',
        refreshToken: 'refresh-1',
        expiresIn: 1800,
      ),
    );
    final leidos = await storage.leer();

    expect(leidos, isNotNull);
    expect(leidos!.accessToken, 'access-1');
    expect(leidos.refreshToken, 'refresh-1');
    expect(leidos.expiresIn, 1800);
  });

  test('borrar limpia la sesion', () async {
    final storage = AuthStorage();
    await storage.guardar(
      const AuthTokenResponse(accessToken: 'a', refreshToken: 'r'),
    );

    await storage.borrar();

    expect(await storage.leer(), isNull);
  });
}
