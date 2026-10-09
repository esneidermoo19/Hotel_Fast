import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/shared/utils/lectura_json.dart';

void main() {
  group('lectura_json', () {
    test('leerEntero acepta int, num y cadena', () {
      expect(leerEntero(7), 7);
      expect(leerEntero(7.9), 7);
      expect(leerEntero('42'), 42);
      expect(leerEntero(null), isNull);
      expect(leerEntero('abc'), isNull);
    });

    test('leerDecimal acepta num y cadena', () {
      expect(leerDecimal(120.5), 120.5);
      expect(leerDecimal('120.50'), 120.5);
      expect(leerDecimal(null), isNull);
    });

    test('leerTexto devuelve null para vacio o no-cadena', () {
      expect(leerTexto('hola'), 'hola');
      expect(leerTexto(''), isNull);
      expect(leerTexto(5), isNull);
    });

    test('leerBooleano acepta bool y cadenas', () {
      expect(leerBooleano(true), isTrue);
      expect(leerBooleano('false'), isFalse);
      expect(leerBooleano('TRUE'), isTrue);
      expect(leerBooleano('si'), isNull);
    });

    test('leerMapa convierte objetos y descarta otros tipos', () {
      expect(leerMapa({'a': 1}), {'a': 1});
      expect(leerMapa([1, 2]), isNull);
      expect(leerMapa(null), isNull);
    });

    test('leerListaDeMapas filtra los elementos que no son objetos', () {
      final lista = leerListaDeMapas([
        {'id': 1},
        'texto',
        {'id': 2},
      ]);

      expect(lista, hasLength(2));
      expect(lista.first['id'], 1);
      expect(lista.last['id'], 2);
    });
  });
}
