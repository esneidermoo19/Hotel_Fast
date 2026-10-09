import '../core/network/api_client.dart';
import '../shared/models/pagina.dart';
import '../shared/utils/fecha_hora.dart';
import '../shared/utils/lectura_json.dart';
import 'models/reserva.dart';

/// Consume los endpoints de `/api/reservas` y las subrutas de ciclo de vida.
class ReservasService {
  ReservasService(this.api);

  final ApiClient api;

  static const String _ruta = '/api/reservas';

  Future<Pagina<Reserva>> listar({
    int pagina = 1,
    int tamano = 20,
    String? estado,
    DateTime? desde,
    DateTime? hasta,
  }) async {
    final desdeTexto = desde == null ? null : formatearFecha(desde);
    final hastaTexto = hasta == null ? null : formatearFecha(hasta);
    final data = await api.get(
      _ruta,
      query: {
        'pagina': pagina,
        'tamano': tamano,
        'estado': ?estado,
        'desde': ?desdeTexto,
        'hasta': ?hastaTexto,
      },
    );
    return Pagina.fromJson(
      leerMapa(data) ?? const <String, dynamic>{},
      Reserva.fromJson,
    );
  }

  Future<List<ReservaHabitacion>> disponibilidad(
    DisponibilidadConsulta consulta,
  ) async {
    final data = await api.get(
      '$_ruta/disponibilidad',
      query: consulta.toQuery(),
    );
    return [
      for (final mapa in leerListaDeMapas(data))
        ReservaHabitacion.fromJson(mapa),
    ];
  }

  Future<Reserva> crear(CrearReservaRequest request) async {
    final data = await api.post(_ruta, body: request.toJson());
    return Reserva.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Reserva> obtener(int id) async {
    final data = await api.get('$_ruta/$id');
    return Reserva.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Reserva> confirmar(int id) => _accion(id, 'confirmar');

  Future<Reserva> cancelar(int id, String motivo) async {
    final data = await api.post(
      '$_ruta/$id/cancelar',
      body: {'motivo': motivo},
    );
    return Reserva.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Reserva> marcarNoShow(int id) => _accion(id, 'no-show');

  Future<Reserva> checkIn(int id) => _accion(id, 'check-in');

  Future<ReservaCheckOut> checkOut(int id) async {
    final data = await api.post('$_ruta/$id/check-out');
    return ReservaCheckOut.fromJson(
      leerMapa(data) ?? const <String, dynamic>{},
    );
  }

  Future<Reserva> extender(int id, DateTime nuevaFechaSalida) async {
    final data = await api.post(
      '$_ruta/$id/extender',
      body: {'nuevaFechaSalida': formatearFecha(nuevaFechaSalida)},
    );
    return Reserva.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }

  Future<Reserva> _accion(int id, String accion) async {
    final data = await api.post('$_ruta/$id/$accion');
    return Reserva.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }
}
