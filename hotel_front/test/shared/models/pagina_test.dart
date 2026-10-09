import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/shared/models/pagina.dart';

class _Habitacion {
  const _Habitacion({required this.id, required this.numero});

  final int id;
  final int numero;

  factory _Habitacion.fromJson(Map<String, dynamic> json) {
    return _Habitacion(id: json['id'] as int, numero: json['numero'] as int);
  }
}

void main() {
  group('Pagina', () {
    test('parsea items, total, pagina y tamano', () {
      final pagina = Pagina<_Habitacion>.fromJson({
        'items': [
          {'id': 1, 'numero': 101},
          {'id': 2, 'numero': 102},
        ],
        'total': 42,
        'pagina': 1,
        'tamano': 2,
      }, _Habitacion.fromJson);

      expect(pagina.items, hasLength(2));
      expect(pagina.items.first.numero, 101);
      expect(pagina.total, 42);
      expect(pagina.pagina, 1);
      expect(pagina.tamano, 2);
    });

    test('usa valores por defecto cuando faltan metadatos', () {
      final pagina = Pagina<_Habitacion>.fromJson({
        'items': [
          {'id': 1, 'numero': 101},
        ],
      }, _Habitacion.fromJson);

      expect(pagina.total, 1);
      expect(pagina.pagina, 1);
      expect(pagina.tamano, 1);
    });

    test('tienePaginaSiguiente segun total y tamano', () {
      final conSiguiente = Pagina<int>(
        items: const [1, 2],
        total: 10,
        pagina: 1,
        tamano: 2,
      );
      final ultima = Pagina<int>(
        items: const [9, 10],
        total: 10,
        pagina: 5,
        tamano: 2,
      );

      expect(conSiguiente.tienePaginaSiguiente, isTrue);
      expect(ultima.tienePaginaSiguiente, isFalse);
    });

    test('items vacio cuando el arreglo no es una lista', () {
      final pagina = Pagina<_Habitacion>.fromJson({
        'items': 'no-es-lista',
        'total': 0,
        'pagina': 1,
        'tamano': 20,
      }, _Habitacion.fromJson);

      expect(pagina.items, isEmpty);
    });
  });
}
