import '../core/network/api_client.dart';
import '../shared/utils/lectura_json.dart';
import 'models/dashboard_resumen.dart';

/// Acceso a los indicadores del panel (`GET /api/dashboard`).
class DashboardService {
  DashboardService(this.api);

  final ApiClient api;

  Future<DashboardResumen> cargar() async {
    final data = await api.get('/api/dashboard');
    return DashboardResumen.fromJson(
      leerMapa(data) ?? const <String, dynamic>{},
    );
  }
}
