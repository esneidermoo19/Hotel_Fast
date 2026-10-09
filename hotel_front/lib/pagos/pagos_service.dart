import '../core/network/api_client.dart';
import '../cuentas/models/pago.dart';
import '../shared/utils/lectura_json.dart';

/// Registro de pagos de una reserva.
class PagosService {
  PagosService(this.api);

  final ApiClient api;

  Future<Pago> registrar(int reservaId, PagoRequest request) async {
    final data = await api.post(
      '/api/reservas/$reservaId/pagos',
      body: request.toJson(),
    );
    return Pago.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }
}
