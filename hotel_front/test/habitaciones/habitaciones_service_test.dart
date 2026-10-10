import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:hotel_front/core/network/api_exception.dart';
import 'package:hotel_front/core/network/codigos_error.dart';
import 'package:hotel_front/habitaciones/habitaciones_service.dart';
import 'package:hotel_front/habitaciones/models/habitacion.dart';
import 'package:http/http.dart' as http;

import '../support/auth_test_utils.dart';

String _habitacionJson({int id = 1, int numero = 101}) {
  return jsonEncode({
    'id': id,
    'numero': numero,
    'tipo': 'DOBLE',
    'capacidad': 2,
    'precioPorNoche': 120.5,
    'estado': 'DISPONIBLE',
    'limpieza': 'LIMPIA',
    'descripcion': null,
  });
}

void main() {
  test('listar parsea el arreglo y envia los filtros', () async {
    Uri? uri;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        uri = request.url;
        return http.Response(
          jsonEncode([
            jsonDecode(_habitacionJson()),
            jsonDecode(_habitacionJson(id: 2, numero: 102)),
          ]),
          200,
        );
      }),
    );

    final lista = await servicio.listar(estado: 'DISPONIBLE', tipo: 'DOBLE');

    expect(lista, hasLength(2));
    expect(lista.first.numero, 101);
    expect(lista.first.precioPorNoche, 120.5);
    expect(uri!.path, '/api/habitaciones');
    expect(uri!.queryParameters, {'estado': 'DISPONIBLE', 'tipo': 'DOBLE'});
  });

  test('crear envia el cuerpo y parsea la respuesta 201', () async {
    http.Request? capturado;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(_habitacionJson(), 201);
      }),
    );

    final creada = await servicio.crear(
      const HabitacionPayload(
        numero: 101,
        tipo: 'DOBLE',
        capacidad: 2,
        precioPorNoche: 120.5,
        estado: 'DISPONIBLE',
      ),
    );

    expect(capturado!.method, 'POST');
    expect(capturado!.url.path, '/api/habitaciones');
    expect(jsonDecode(capturado!.body), {
      'numero': 101,
      'tipo': 'DOBLE',
      'capacidad': 2,
      'precioPorNoche': 120.5,
      'estado': 'DISPONIBLE',
    });
    expect(creada.id, 1);
  });

  test('cambiarEstado usa PATCH con el cuerpo correcto', () async {
    http.Request? capturado;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(_habitacionJson(), 200);
      }),
    );

    await servicio.cambiarEstado(7, 'MANTENIMIENTO');

    expect(capturado!.method, 'PATCH');
    expect(capturado!.url.path, '/api/habitaciones/7/estado');
    expect(jsonDecode(capturado!.body), {'estado': 'MANTENIMIENTO'});
  });

  test('eliminar usa DELETE y no falla con 204', () async {
    http.Request? capturado;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response('', 204);
      }),
    );

    await servicio.eliminar(7);

    expect(capturado!.method, 'DELETE');
    expect(capturado!.url.path, '/api/habitaciones/7');
  });

  test('un 409 REGLA_NEGOCIO se propaga como ApiException', () async {
    final servicio = HabitacionesService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            'detail': 'El numero de habitacion ya existe',
            'code': 'CONFLICTO',
          }),
          409,
        ),
      ),
    );

    await expectLater(
      servicio.crear(
        const HabitacionPayload(
          numero: 101,
          tipo: 'DOBLE',
          capacidad: 2,
          precioPorNoche: 100,
          estado: 'DISPONIBLE',
        ),
      ),
      throwsA(
        isA<ApiException>()
            .having((e) => e.statusCode, 'statusCode', 409)
            .having((e) => e.codigo, 'codigo', 'CONFLICTO'),
      ),
    );
  });

  test('subirImagen envia multipart con el archivo', () async {
    http.Request? capturado;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(
          jsonEncode({
            'id': 10,
            'url': '/media/abc.png',
            'orden': 1,
            'esPrincipal': true,
          }),
          201,
        );
      }),
    );

    final imagen = await servicio.subirImagen(
      7,
      utf8.encode('contenido-de-imagen'),
      'foto.png',
    );

    expect(capturado!.method, 'POST');
    expect(capturado!.url.path, '/api/habitaciones/7/imagenes');
    expect(capturado!.headers['content-type'], contains('multipart/form-data'));
    expect(latin1.decode(capturado!.bodyBytes), contains('foto.png'));
    expect(imagen.id, 10);
    expect(imagen.esPrincipal, isTrue);
    expect(imagen.url, '/media/abc.png');
  });

  test('subirImagen rechaza extension no permitida sin tocar la red', () async {
    var llamoALaRed = false;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        llamoALaRed = true;
        return http.Response('', 200);
      }),
    );

    await expectLater(
      servicio.subirImagen(1, utf8.encode('x'), 'foto.gif'),
      throwsA(
        isA<ApiException>()
            .having(
              (e) => e.codigo,
              'codigo',
              CodigosError.formatoImagenInvalido,
            )
            .having((e) => e.statusCode, 'statusCode', 422),
      ),
    );
    expect(llamoALaRed, isFalse);
  });

  test('subirImagen rechaza un archivo mayor a 5 MB', () async {
    var llamoALaRed = false;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        llamoALaRed = true;
        return http.Response('', 200);
      }),
    );

    final grande = List<int>.filled(5 * 1024 * 1024 + 1, 0);

    await expectLater(
      servicio.subirImagen(1, grande, 'foto.png'),
      throwsA(
        isA<ApiException>().having(
          (e) => e.codigo,
          'codigo',
          CodigosError.imagenMuyGrande,
        ),
      ),
    );
    expect(llamoALaRed, isFalse);
  });

  test('subirImagen propaga el 409 MAXIMO_IMAGENES del backend', () async {
    final servicio = HabitacionesService(
      crearApiSimulada(
        (request) async => http.Response(
          jsonEncode({
            'detail': 'Maximo de imagenes',
            'code': 'MAXIMO_IMAGENES',
          }),
          409,
        ),
      ),
    );

    await expectLater(
      servicio.subirImagen(1, utf8.encode('x'), 'foto.png'),
      throwsA(
        isA<ApiException>()
            .having((e) => e.codigo, 'codigo', CodigosError.maximoImagenes)
            .having((e) => e.statusCode, 'statusCode', 409),
      ),
    );
  });

  test('eliminarImagen usa DELETE', () async {
    http.Request? capturado;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response('', 204);
      }),
    );

    await servicio.eliminarImagen(7, 3);

    expect(capturado!.method, 'DELETE');
    expect(capturado!.url.path, '/api/habitaciones/7/imagenes/3');
  });

  test('marcarPrincipal usa PATCH', () async {
    http.Request? capturado;
    final servicio = HabitacionesService(
      crearApiSimulada((request) async {
        capturado = request;
        return http.Response(
          jsonEncode({
            'id': 3,
            'url': '/media/x.png',
            'orden': 1,
            'esPrincipal': true,
          }),
          200,
        );
      }),
    );

    final imagen = await servicio.marcarPrincipal(7, 3);

    expect(capturado!.method, 'PATCH');
    expect(capturado!.url.path, '/api/habitaciones/7/imagenes/3/principal');
    expect(imagen.esPrincipal, isTrue);
  });

  test('resolverUrlMedia resuelve relativas y respeta absolutas', () {
    final servicio = HabitacionesService(
      crearApiSimulada((request) async => http.Response('', 200)),
    );

    expect(
      servicio.resolverUrlMedia('/media/abc.png'),
      'http://localhost:8000/media/abc.png',
    );
    expect(
      servicio.resolverUrlMedia('https://cdn.example.com/a.png'),
      'https://cdn.example.com/a.png',
    );
  });
}
