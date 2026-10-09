import '../../shared/utils/lectura_json.dart';
import '../../shared/utils/moneda.dart';
import 'consumo.dart';
import 'pago.dart';

/// Estado de cuenta de una reserva (`CuentaRead`).
class CuentaReserva {
  const CuentaReserva({
    required this.totalAlojamiento,
    required this.totalConsumosVigentes,
    required this.totalPagosVigentes,
    required this.saldoPendiente,
    required this.detalleConsumos,
    required this.detallePagos,
  });

  /// Noches x precio por noche aplicado.
  final double totalAlojamiento;

  /// Suma de consumos no anulados.
  final double totalConsumosVigentes;

  /// Suma de pagos vigentes (excluye reembolsos).
  final double totalPagosVigentes;

  /// Alojamiento + consumos - pagos.
  final double saldoPendiente;

  final List<Consumo> detalleConsumos;
  final List<Pago> detallePagos;

  double get totalCuenta => totalAlojamiento + totalConsumosVigentes;

  factory CuentaReserva.fromJson(Map<String, dynamic> json) {
    return CuentaReserva(
      totalAlojamiento: leerMonto(json['totalAlojamiento']) ?? 0,
      totalConsumosVigentes: leerMonto(json['totalConsumosVigentes']) ?? 0,
      totalPagosVigentes: leerMonto(json['totalPagosVigentes']) ?? 0,
      saldoPendiente: leerMonto(json['saldoPendiente']) ?? 0,
      detalleConsumos: [
        for (final mapa in leerListaDeMapas(json['detalleConsumos']))
          Consumo.fromJson(mapa),
      ],
      detallePagos: [
        for (final mapa in leerListaDeMapas(json['detallePagos']))
          Pago.fromJson(mapa),
      ],
    );
  }
}