import '../core/network/api_client.dart';
import '../cuentas/models/consumo.dart';
import '../shared/utils/lectura_json.dart';

/// Registro de consumos de una reserva.
class ConsumosService {
  ConsumosService(this.api);

  final ApiClient api;

  Future<Consumo> registrar(int reservaId, ConsumoRequest request) async {
    final data = await api.post(
      '/api/reservas/$reservaId/consumos',
      body: request.toJson(),
    );
    return Consumo.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }
}
