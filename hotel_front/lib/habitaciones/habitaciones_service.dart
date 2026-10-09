import '../core/network/api_client.dart';
import '../shared/utils/lectura_json.dart';
import 'models/habitacion.dart';

/// Consume los endpoints de `/api/habitaciones`.
class HabitacionesService {
  HabitacionesService(this.api);

  final ApiClient api;

  static const String _ruta = '/api/habitaciones';

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
}
