import '../../shared/utils/fecha_hora.dart';
import '../../shared/utils/lectura_json.dart';
import '../../shared/utils/moneda.dart';

/// Pago de una reserva (`PagoRead` / `CuentaDetallePago`).
class Pago {
  const Pago({
    required this.id,
    required this.monto,
    required this.metodo,
    required this.tipo,
    required this.anulado,
    this.referencia,
    this.motivoAnulacion,
    this.fechaPago,
  });

  final int id;
  final double monto;

  /// `MetodoPago`: EFECTIVO, TARJETA, TRANSFERENCIA, OTRO.
  final String metodo;

  /// `TipoPago`: ABONO, PAGO_FINAL, REEMBOLSO.
  final String tipo;
  final bool anulado;
  final String? referencia;
  final String? motivoAnulacion;
  final DateTime? fechaPago;

  factory Pago.fromJson(Map<String, dynamic> json) {
    return Pago(
      id: leerEntero(json['id']) ?? 0,
      monto: leerMonto(json['monto']) ?? 0,
      metodo: leerTexto(json['metodo']) ?? '',
      tipo: leerTexto(json['tipo']) ?? '',
      anulado: leerBooleano(json['anulado']) ?? false,
      referencia: leerTexto(json['referencia']),
      motivoAnulacion: leerTexto(json['motivoAnulacion']),
      fechaPago: leerFechaHora(json['fechaPago']),
    );
  }
}

/// Cuerpo para registrar un pago (`PagoCreate`).
class PagoRequest {
  const PagoRequest({
    required this.monto,
    required this.metodo,
    required this.tipo,
    this.referencia,
  });

  final double monto;
  final String metodo;
  final String tipo;
  final String? referencia;

  Map<String, dynamic> toJson() {
    return {
      'monto': monto,
      'metodo': metodo,
      'tipo': tipo,
      'referencia': ?referencia,
    };
  }
}