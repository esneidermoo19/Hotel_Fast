import '../../shared/utils/lectura_json.dart';
import '../../shared/utils/moneda.dart';

/// Consumo de una reserva (`ConsumoRead` / `CuentaDetalleConsumo`).
class Consumo {
  const Consumo({
    required this.id,
    required this.descripcion,
    required this.cantidad,
    required this.precioUnitario,
    required this.anulado,
    this.motivoAnulacion,
  });

  final int id;
  final String descripcion;
  final int cantidad;
  final double precioUnitario;
  final bool anulado;
  final String? motivoAnulacion;

  /// Total del consumo (precio unitario x cantidad).
  double get total => precioUnitario * cantidad;

  factory Consumo.fromJson(Map<String, dynamic> json) {
    return Consumo(
      id: leerEntero(json['id']) ?? 0,
      descripcion: leerTexto(json['descripcion']) ?? '',
      cantidad: leerEntero(json['cantidad']) ?? 0,
      precioUnitario: leerMonto(json['precioUnitario']) ?? 0,
      anulado: leerBooleano(json['anulado']) ?? false,
      motivoAnulacion: leerTexto(json['motivoAnulacion']),
    );
  }
}

/// Cuerpo para registrar un consumo (`ConsumoCreate`).
class ConsumoRequest {
  const ConsumoRequest({
    required this.descripcion,
    required this.cantidad,
    required this.precioUnitario,
  });

  final String descripcion;
  final int cantidad;
  final double precioUnitario;

  Map<String, dynamic> toJson() {
    return {
      'descripcion': descripcion,
      'cantidad': cantidad,
      'precioUnitario': precioUnitario,
    };
  }
}
