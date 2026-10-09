import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/shared/utils/moneda.dart';

void main() {
  group('leerMonto', () {
    test('acepta num y cadenas numericas', () {
      expect(leerMonto(120.5), 120.5);
      expect(leerMonto('120.50'), 120.5);
    });

    test('devuelve null para valores no numericos', () {
      expect(leerMonto(null), isNull);
      expect(leerMonto('abc'), isNull);
    });
  });

  group('formatearMonto', () {
    test('usa separador de miles y decimal es-CO', () {
      expect(formatearMonto(1234567.5), r'$ 1.234.567,50');
    });

    test('puede omitir los decimales', () {
      expect(formatearMonto(1234567, decimales: false), r'$ 1.234.567');
    });

    test('formatea negativos', () {
      expect(formatearMonto(-1500.0), r'-$ 1.500,00');
    });

    test('redondea centavos que completan una unidad', () {
      expect(formatearMonto(2.999), r'$ 3,00');
    });

    test('devuelve vacio si el valor no es numerico', () {
      expect(formatearMonto(null), '');
      expect(formatearMonto('n/a'), '');
    });
  });
}
