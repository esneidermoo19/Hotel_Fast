import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/config/app_config.dart';

void main() {
  group('AppConfig', () {
    test('usa el valor por defecto de desarrollo', () {
      final config = AppConfig.fromEnvironment();

      expect(config.baseUrl, 'http://localhost:8000');
      expect(config.timeout, const Duration(seconds: 15));
    });

    test('elimina la barra final de la URL base', () {
      final config = AppConfig(baseUrl: 'http://localhost:8000/');

      expect(config.baseUrl, 'http://localhost:8000');
    });

    test('rechaza una URL vacia', () {
      expect(() => AppConfig(baseUrl: '  '), throwsArgumentError);
    });

    test('rechaza una URL relativa', () {
      expect(() => AppConfig(baseUrl: 'localhost:8000'), throwsArgumentError);
    });

    test('rechaza un esquema que no sea http o https', () {
      expect(
        () => AppConfig(baseUrl: 'ftp://localhost:8000'),
        throwsArgumentError,
      );
    });

    test('resolve construye la URL con query y omite valores nulos', () {
      final config = AppConfig(baseUrl: 'http://localhost:8000');

      final uri = config.resolve(
        '/api/usuarios',
        query: {'pagina': 1, 'q': null, 'activo': true},
      );

      expect(
        uri.toString(),
        'http://localhost:8000/api/usuarios?pagina=1&activo=true',
      );
    });

    test('resolve admite rutas sin barra inicial y conserva el prefijo', () {
      final config = AppConfig(baseUrl: 'https://hotel.example.com/pms');

      final uri = config.resolve('api/health');

      expect(uri.toString(), 'https://hotel.example.com/pms/api/health');
    });
  });
}
