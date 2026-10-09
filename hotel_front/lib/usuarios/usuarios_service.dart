import '../auth/models/usuario.dart';
import '../core/network/api_client.dart';
import '../shared/models/pagina.dart';
import '../shared/utils/lectura_json.dart';
import 'models/usuario_payload.dart';

/// Administracion de usuarios (`/api/usuarios`, solo ADMIN).
class UsuariosService {
  UsuariosService(this.api);

  final ApiClient api;

  static const String _ruta = '/api/usuarios';

  Future<Pagina<Usuario>> listar({
    int pagina = 1,
    int tamano = 20,
    String? rol,
    String? q,
    bool soloActivos = false,
  }) async {
    final data = await api.get(
      _ruta,
      query: {
        'pagina': pagina,
        'tamano': tamano,
        'rol': ?rol,
        'q': ?q,
        if (soloActivos) 'soloActivos': true,
      },
    );
    return Pagina.fromJson(
      leerMapa(data) ?? const <String, dynamic>{},
      Usuario.fromJson,
    );
  }

  Future<Usuario> crear(UsuarioCrear datos) async {
    final data = await api.post(_ruta, body: datos.toJson());
    return Usuario.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Usuario> actualizar(int id, UsuarioActualizar datos) async {
    final data = await api.put('$_ruta/$id', body: datos.toJson());
    return Usuario.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Usuario> desactivar(int id) async {
    final data = await api.post('$_ruta/$id/desactivar');
    return Usuario.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Usuario> reactivar(int id) async {
    final data = await api.post('$_ruta/$id/reactivar');
    return Usuario.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<void> eliminar(int id) async {
    await api.delete('$_ruta/$id');
  }
}
