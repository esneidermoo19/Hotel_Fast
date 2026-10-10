import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/habitaciones/models/habitacion.dart';

void main() {
  group('Habitacion.fromJson', () {
    test('parsea una habitacion con imagenes', () {
      final habitacion = Habitacion.fromJson({
        'id': 1,
        'numero': 101,
        'tipo': 'DOBLE',
        'capacidad': 2,
        'precioPorNoche': 120.5,
        'estado': 'DISPONIBLE',
        'limpieza': 'LIMPIA',
        'descripcion': null,
        'imagenPrincipalUrl': '/media/abc.png',
        'imagenes': [
          {'id': 10, 'url': '/media/abc.png', 'orden': 1, 'esPrincipal': true},
          {'id': 11, 'url': '/media/def.png', 'orden': 2, 'esPrincipal': false},
        ],
      });

      expect(habitacion.imagenPrincipalUrl, '/media/abc.png');
      expect(habitacion.imagenes, hasLength(2));
      expect(habitacion.imagenes.first.id, 10);
      expect(habitacion.imagenes.first.esPrincipal, isTrue);
      expect(habitacion.imagenes.last.orden, 2);
      expect(habitacion.tieneImagenes, isTrue);
    });

    test('parsea una habitacion sin imagenes', () {
      final habitacion = Habitacion.fromJson({
        'id': 1,
        'numero': 101,
        'tipo': 'DOBLE',
        'capacidad': 2,
        'precioPorNoche': 120.5,
        'estado': 'DISPONIBLE',
        'limpieza': 'LIMPIA',
      });

      expect(habitacion.imagenPrincipalUrl, isNull);
      expect(habitacion.imagenes, isEmpty);
      expect(habitacion.tieneImagenes, isFalse);
    });

    test('ignora de forma tolerante campos mal tipados en las imagenes', () {
      final habitacion = Habitacion.fromJson({
        'id': 1,
        'numero': 101,
        'tipo': 'DOBLE',
        'capacidad': 2,
        'precioPorNoche': 120.5,
        'estado': 'DISPONIBLE',
        'limpieza': 'LIMPIA',
        'imagenes': [
          {'id': 'no-numero', 'url': 42, 'orden': null, 'esPrincipal': 'si'},
        ],
      });

      expect(habitacion.imagenes, hasLength(1));
      expect(habitacion.imagenes.first.id, 0);
      expect(habitacion.imagenes.first.url, '');
      expect(habitacion.imagenes.first.esPrincipal, isFalse);
    });
  });

  group('HabitacionImagen.copiarCon', () {
    test('cambia solo el campo esPrincipal', () {
      const imagen = HabitacionImagen(
        id: 5,
        url: '/media/x.png',
        orden: 1,
        esPrincipal: false,
      );

      final principal = imagen.copiarCon(esPrincipal: true);

      expect(principal.id, 5);
      expect(principal.url, '/media/x.png');
      expect(principal.orden, 1);
      expect(principal.esPrincipal, isTrue);
    });
  });
}
