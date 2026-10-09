import '../core/network/api_client.dart';
import '../core/network/api_exception.dart';
import '../shared/utils/lectura_json.dart';
import 'models/catalogo.dart';

/// Obtiene y cachea en memoria los catalogos del sistema.
///
/// Se crea una sola instancia en el arranque (via `AppScope`) para que las
/// pantallas consulten [obtener] o [valores] sin repetir peticiones.
class CatalogosService {
  CatalogosService(this.api);

  final ApiClient api;
  final Map<String, Catalogo> _cache = <String, Catalogo>{};
  Future<void>? _cargaEnCurso;

  bool get cargado => _cache.isNotEmpty;

  Catalogo? obtener(String nombre) => _cache[nombre];

  List<String> valores(String nombre) =>
      _cache[nombre]?.valores ?? const <String>[];

  /// Carga los catalogos una sola vez. Las llamadas concurrentes comparten la
  /// misma carga en curso.
  Future<void> asegurarCargado() {
    if (cargado) return Future.value();
    return _cargaEnCurso ??= _cargar().whenComplete(() => _cargaEnCurso = null);
  }

  /// Precarga best-effort: si falla, se reintentara cuando se use.
  Future<void> precargar() async {
    try {
      await asegurarCargado();
    } on ApiException {
      // Sin conexion: la pantalla que necesite el catalogo reintentara.
    }
  }

  Future<void> _cargar() async {
    final data = await api.get('/api/catalogos');
    for (final mapa in leerListaDeMapas(data)) {
      final catalogo = Catalogo.fromJson(mapa);
      if (catalogo.nombre.isNotEmpty) {
        _cache[catalogo.nombre] = catalogo;
      }
    }
  }
}
