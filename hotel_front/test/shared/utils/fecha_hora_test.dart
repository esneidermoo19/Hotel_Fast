import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/shared/utils/fecha_hora.dart';

void main() {
  group('leerFecha', () {
    test('parsea YYYY-MM-DD sin hora', () {
      expect(leerFecha('2026-10-08'), DateTime(2026, 10, 8));
    });

    test('de una marca ISO toma solo la fecha', () {
      expect(leerFecha('2026-10-08T14:30:00Z'), DateTime(2026, 10, 8));
    });

    test('devuelve null para valores invalidos o vacios', () {
      expect(leerFecha(null), isNull);
      expect(leerFecha(''), isNull);
      expect(leerFecha('no-es-fecha'), isNull);
    });
  });

  group('leerFechaHora', () {
    test('respeta el offset Z y normaliza a UTC', () {
      expect(
        leerFechaHora('2026-10-08T14:30:00Z'),
        DateTime.utc(2026, 10, 8, 14, 30),
      );
    });

    test('sin offset se interpreta como UTC', () {
      expect(
        leerFechaHora('2026-10-08T14:30:00'),
        DateTime.utc(2026, 10, 8, 14, 30),
      );
    });

    test('convierte un offset explicito a UTC', () {
      expect(
        leerFechaHora('2026-10-08T14:30:00-05:00'),
        DateTime.utc(2026, 10, 8, 19, 30),
      );
    });

    test('devuelve null para valores invalidos', () {
      expect(leerFechaHora(null), isNull);
      expect(leerFechaHora('xyz'), isNull);
    });
  });

  group('formateo', () {
    test('formatearFecha rellena con ceros', () {
      expect(formatearFecha(DateTime(2026, 1, 5)), '2026-01-05');
    });

    test('formatearFechaHoraUtc usa formato ISO en UTC', () {
      expect(
        formatearFechaHoraUtc(DateTime.utc(2026, 10, 8, 14, 30, 5)),
        '2026-10-08T14:30:05Z',
      );
    });
  });
}
