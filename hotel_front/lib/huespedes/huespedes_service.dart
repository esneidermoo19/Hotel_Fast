import '../core/network/api_client.dart';
import '../shared/models/pagina.dart';
import '../shared/utils/lectura_json.dart';
import 'models/huesped.dart';

/// Consume los endpoints de `/api/huespedes` (listado paginado).
class HuespedesService {
  HuespedesService(this.api);

  final ApiClient api;

  static const String _ruta = '/api/huespedes';

  Future<Pagina<Huesped>> listar({
    int pagina = 1,
    int tamano = 20,
    String? q,
    String? tipoDocumento,
    String? numeroDocumento,
  }) async {
    final data = await api.get(
      _ruta,
      query: {
        'pagina': pagina,
        'tamano': tamano,
        'q': ?q,
        'tipoDocumento': ?tipoDocumento,
        'numeroDocumento': ?numeroDocumento,
      },
    );
    return Pagina.fromJson(
      leerMapa(data) ?? const <String, dynamic>{},
      Huesped.fromJson,
    );
  }

  Future<Huesped> crear(HuespedPayload datos) async {
    final data = await api.post(_ruta, body: datos.toJson());
    return Huesped.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Huesped> actualizar(int id, HuespedPayload datos) async {
    final data = await api.put('$_ruta/$id', body: datos.toJson());
    return Huesped.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<void> eliminar(int id) async {
    await api.delete('$_ruta/$id');
  }
}
