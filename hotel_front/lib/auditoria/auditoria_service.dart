import '../core/network/api_client.dart';
import '../shared/models/pagina.dart';
import '../shared/utils/fecha_hora.dart';
import '../shared/utils/lectura_json.dart';
import 'models/auditoria_registro.dart';

/// Consulta de logs de auditoria (`/api/auditoria`, solo ADMIN).
class AuditoriaService {
  AuditoriaService(this.api);

  final ApiClient api;

  Future<Pagina<AuditoriaRegistro>> listar({
    int pagina = 1,
    int tamano = 20,
    String? entidad,
    String? accion,
    int? usuarioId,
    DateTime? desde,
    DateTime? hasta,
  }) async {
    final desdeTexto = desde == null ? null : formatearFecha(desde);
    final hastaTexto = hasta == null ? null : formatearFecha(hasta);
    final data = await api.get(
      '/api/auditoria',
      query: {
        'pagina': pagina,
        'tamano': tamano,
        'entidad': ?entidad,
        'accion': ?accion,
        'usuarioId': ?usuarioId,
        'desde': ?desdeTexto,
        'hasta': ?hastaTexto,
      },
    );
    return Pagina.fromJson(
      leerMapa(data) ?? const <String, dynamic>{},
      AuditoriaRegistro.fromJson,
    );
  }
}
