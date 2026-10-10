import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/shared/utils/formato.dart';

void main() {
  group('iniciales', () {
    test('nombre vacio devuelve un signo', () {
      expect(iniciales(''), '?');
      expect(iniciales('   '), '?');
    });

    test('una sola palabra usa una inicial', () {
      expect(iniciales('Ana'), 'A');
    });

    test('dos palabras usan primera y ultima', () {
      expect(iniciales('Ana Pérez'), 'AP');
    });

    test('es tolerante a las tildes', () {
      expect(iniciales('José'), 'J');
      expect(iniciales('Álvaro Pérez'), 'ÁP');
    });

    test('mas de dos palabras usa primera y ultima', () {
      expect(iniciales('María José García'), 'MG');
    });
  });

  group('humanizar', () {
    test('convierte SNAKE_CASE a titulo', () {
      expect(humanizar('CHECK_IN'), 'Check In');
      expect(humanizar('PRESIDENCIAL'), 'Presidencial');
    });
  });
}
