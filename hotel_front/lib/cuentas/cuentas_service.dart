import '../core/network/api_client.dart';
import '../shared/utils/lectura_json.dart';
import 'models/cuenta.dart';

/// Acceso al estado de cuenta de una reserva (`GET /api/cuentas/{id}`).
class CuentasService {
  CuentasService(this.api);

  final ApiClient api;

  Future<CuentaReserva> obtener(int reservaId) async {
    final data = await api.get('/api/cuentas/$reservaId');
    return CuentaReserva.fromJson(leerMapa(data) ?? const <String, dynamic>{});
  }
}
