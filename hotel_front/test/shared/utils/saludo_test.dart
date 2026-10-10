import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/shared/utils/saludo.dart';

void main() {
  group('saludoPorHora', () {
    test('por la manana', () {
      expect(saludoPorHora(DateTime(2026, 10, 10, 9)), 'Buenos días');
    });

    test('por la tarde', () {
      expect(saludoPorHora(DateTime(2026, 10, 10, 15)), 'Buenas tardes');
    });

    test('por la noche', () {
      expect(saludoPorHora(DateTime(2026, 10, 10, 21)), 'Buenas noches');
    });

    test('de madrugada', () {
      expect(saludoPorHora(DateTime(2026, 10, 10, 2)), 'Buenas noches');
    });
  });

  group('fechaLegible', () {
    test('formatea el dia y el mes en espanol', () {
      expect(fechaLegible(DateTime(2026, 10, 10)), 'sábado, 10 de octubre');
    });
  });

  group('saludoDelDia', () {
    test('combina saludo y fecha', () {
      expect(
        saludoDelDia(DateTime(2026, 10, 10, 15)),
        'Buenas tardes · sábado, 10 de octubre',
      );
    });
  });
}
