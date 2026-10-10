import '../core/network/api_client.dart';
import '../core/network/api_exception.dart';
import '../core/network/codigos_error.dart';
import '../shared/utils/lectura_json.dart';
import 'models/habitacion.dart';

/// Consume los endpoints de `/api/habitaciones`.
class HabitacionesService {
  HabitacionesService(this.api);

  final ApiClient api;

  static const String _ruta = '/api/habitaciones';

  /// Tiempo extra para subir imagenes (los archivos pueden tardar mas).
  static const Duration _timeoutSubida = Duration(seconds: 60);

  /// Extensiones aceptadas por el backend (JPEG, PNG y WEBP).
  static const Set<String> _extensionesPermitidas = {
    'jpg',
    'jpeg',
    'png',
    'webp',
  };

  /// Tamanio maximo aceptado por el backend (5 MB).
  static const int _maxBytesImagen = 5 * 1024 * 1024;

  /// Resuelve una ruta relativa de medios contra la URL base de la API.
  ///
  /// Es el unico lugar donde las URLs de imagenes se convierten en absolutas.
  /// Si [ruta] ya es una URL absoluta `http`/`https`, se respeta tal cual.
  String resolverUrlMedia(String ruta) {
    final limpio = ruta.trim();
    if (limpio.isEmpty) return limpio;
    final uri = Uri.tryParse(limpio);
    if (uri != null &&
        uri.isAbsolute &&
        (uri.scheme == 'http' || uri.scheme == 'https')) {
      return limpio;
    }
    final base = api.config.baseUrl;
    return '$base${limpio.startsWith('/') ? limpio : '/$limpio'}';
  }

  /// Listado completo con filtros opcionales (el backend no pagina habitaciones).
  Future<List<Habitacion>> listar({
    String? estado,
    String? tipo,
    String? limpieza,
  }) async {
    final data = await api.get(
      _ruta,
      query: {'estado': ?estado, 'tipo': ?tipo, 'limpieza': ?limpieza},
    );
    return [
      for (final mapa in leerListaDeMapas(data)) Habitacion.fromJson(mapa),
    ];
  }

  Future<Habitacion> crear(HabitacionPayload datos) async {
    final data = await api.post(_ruta, body: datos.toJson());
    return Habitacion.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Habitacion> actualizar(int id, HabitacionPayload datos) async {
    final data = await api.put('$_ruta/$id', body: datos.toJson());
    return Habitacion.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Habitacion> cambiarEstado(int id, String estado) async {
    final data = await api.patch('$_ruta/$id/estado', body: {'estado': estado});
    return Habitacion.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Habitacion> cambiarLimpieza(int id, String limpieza) async {
    final data = await api.patch(
      '$_ruta/$id/limpieza',
      body: {'limpieza': limpieza},
    );
    return Habitacion.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<void> eliminar(int id) async {
    await api.delete('$_ruta/$id');
  }

  /// Sube una imagen a una habitacion.
  ///
  /// Valida de forma previa la extension y el tamanio (5 MB) para dar un
  /// mensaje claro antes de tocar la red. Los errores del backend se propagan
  /// como [ApiException] con su `code` estable.
  Future<HabitacionImagen> subirImagen(
    int habitacionId,
    List<int> bytes,
    String nombreArchivo,
  ) async {
    final extension = _extensionDe(nombreArchivo);
    if (extension == null || !_extensionesPermitidas.contains(extension)) {
      throw const ApiException(
        statusCode: 422,
        codigo: CodigosError.formatoImagenInvalido,
        mensaje: 'El archivo debe ser una imagen JPEG, PNG o WEBP.',
      );
    }
    if (bytes.length > _maxBytesImagen) {
      throw const ApiException(
        statusCode: 422,
        codigo: CodigosError.imagenMuyGrande,
        mensaje: 'La imagen supera el tamano maximo permitido (5 MB).',
      );
    }

    final data = await api.postMultipart(
      '$_ruta/$habitacionId/imagenes',
      campo: 'archivo',
      nombreArchivo: nombreArchivo,
      bytes: bytes,
      timeout: _timeoutSubida,
    );
    return HabitacionImagen.fromJson(
      leerMapa(data) ?? const <String, dynamic>{},
    );
  }

  /// Elimina una imagen de una habitacion.
  Future<void> eliminarImagen(int habitacionId, int imagenId) async {
    await api.delete('$_ruta/$habitacionId/imagenes/$imagenId');
  }

  /// Marca una imagen como principal.
  Future<HabitacionImagen> marcarPrincipal(
    int habitacionId,
    int imagenId,
  ) async {
    final data = await api.patch(
      '$_ruta/$habitacionId/imagenes/$imagenId/principal',
    );
    return HabitacionImagen.fromJson(
      leerMapa(data) ?? const <String, dynamic>{},
    );
  }

  static String? _extensionDe(String nombre) {
    final indice = nombre.lastIndexOf('.');
    if (indice == -1 || indice == nombre.length - 1) return null;
    return nombre.substring(indice + 1).toLowerCase();
  }
}
