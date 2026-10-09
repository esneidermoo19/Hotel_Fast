import '../../shared/utils/fecha_hora.dart';
import '../../shared/utils/lectura_json.dart';
import '../../shared/utils/moneda.dart';

/// Reserva segun `ReservaRead` del contrato.
class Reserva {
  const Reserva({
    required this.id,
    required this.codigo,
    required this.huesped,
    required this.habitacion,
    required this.fechaEntrada,
    required this.fechaSalida,
    required this.numeroHuespedes,
    required this.estado,
    required this.precioNocheAplicado,
    required this.totalEstimado,
    this.observaciones,
    this.motivoCancelacion,
    this.checkInReal,
    this.checkOutReal,
    required this.creadaPor,
  });

  final int id;
  final String codigo;
  final ReservaHuesped huesped;
  final ReservaHabitacion habitacion;
  final DateTime fechaEntrada;
  final DateTime fechaSalida;
  final int numeroHuespedes;

  /// `PENDIENTE`, `CONFIRMADA`, `CHECK_IN`, `CHECK_OUT`, `CANCELADA`, `NO_SHOW`.
  final String estado;
  final double precioNocheAplicado;
  final double totalEstimado;
  final String? observaciones;
  final String? motivoCancelacion;
  final DateTime? checkInReal;
  final DateTime? checkOutReal;
  final int creadaPor;

  factory Reserva.fromJson(Map<String, dynamic> json) {
    return Reserva(
      id: leerEntero(json['id']) ?? 0,
      codigo: leerTexto(json['codigo']) ?? '',
      huesped: ReservaHuesped.fromJson(
        leerMapa(json['huesped']) ?? const <String, dynamic>{},
      ),
      habitacion: ReservaHabitacion.fromJson(
        leerMapa(json['habitacion']) ?? const <String, dynamic>{},
      ),
      fechaEntrada:
          leerFecha(json['fechaEntrada']) ??
          DateTime.fromMillisecondsSinceEpoch(0),
      fechaSalida:
          leerFecha(json['fechaSalida']) ??
          DateTime.fromMillisecondsSinceEpoch(0),
      numeroHuespedes: leerEntero(json['numeroHuespedes']) ?? 0,
      estado: leerTexto(json['estado']) ?? '',
      precioNocheAplicado: leerMonto(json['precioNocheAplicado']) ?? 0,
      totalEstimado: leerMonto(json['totalEstimado']) ?? 0,
      observaciones: leerTexto(json['observaciones']),
      motivoCancelacion: leerTexto(json['motivoCancelacion']),
      checkInReal: leerFechaHora(json['checkInReal']),
      checkOutReal: leerFechaHora(json['checkOutReal']),
      creadaPor: leerEntero(json['creadaPor']) ?? 0,
    );
  }
}

/// Resumen del huesped dentro de una reserva.
class ReservaHuesped {
  const ReservaHuesped({
    required this.id,
    required this.nombres,
    required this.apellidos,
    required this.tipoDocumento,
    required this.numeroDocumento,
  });

  final int id;
  final String nombres;
  final String apellidos;
  final String tipoDocumento;
  final String numeroDocumento;

  String get nombreCompleto => '$nombres $apellidos';

  factory ReservaHuesped.fromJson(Map<String, dynamic> json) {
    return ReservaHuesped(
      id: leerEntero(json['id']) ?? 0,
      nombres: leerTexto(json['nombres']) ?? '',
      apellidos: leerTexto(json['apellidos']) ?? '',
      tipoDocumento: leerTexto(json['tipoDocumento']) ?? '',
      numeroDocumento: leerTexto(json['numeroDocumento']) ?? '',
    );
  }
}

/// Resumen de la habitacion dentro de una reserva (tambien usado por
/// `GET /api/reservas/disponibilidad`).
class ReservaHabitacion {
  const ReservaHabitacion({
    required this.id,
    required this.numero,
    required this.tipo,
    required this.capacidad,
    required this.precioPorNoche,
  });

  final int id;
  final int numero;
  final String tipo;
  final int capacidad;
  final double precioPorNoche;

  factory ReservaHabitacion.fromJson(Map<String, dynamic> json) {
    return ReservaHabitacion(
      id: leerEntero(json['id']) ?? 0,
      numero: leerEntero(json['numero']) ?? 0,
      tipo: leerTexto(json['tipo']) ?? '',
      capacidad: leerEntero(json['capacidad']) ?? 0,
      precioPorNoche: leerMonto(json['precioPorNoche']) ?? 0,
    );
  }
}

/// Resultado del `Check-out` (`CheckOutRead`): reserva mas el resultado
/// economico de la cuenta.
class ReservaCheckOut {
  const ReservaCheckOut({
    required this.reserva,
    required this.totalCuenta,
    required this.totalPagado,
    required this.saldoPendiente,
  });

  final Reserva reserva;
  final double totalCuenta;
  final double totalPagado;
  final double saldoPendiente;

  factory ReservaCheckOut.fromJson(Map<String, dynamic> json) {
    return ReservaCheckOut(
      reserva: Reserva.fromJson(json),
      totalCuenta: leerMonto(json['totalCuenta']) ?? 0,
      totalPagado: leerMonto(json['totalPagado']) ?? 0,
      saldoPendiente: leerMonto(json['saldoPendiente']) ?? 0,
    );
  }
}

/// Cuerpo de creacion de reserva (`ReservaCreate`).
class CrearReservaRequest {
  const CrearReservaRequest({
    required this.huespedId,
    required this.habitacionId,
    required this.fechaEntrada,
    required this.fechaSalida,
    required this.numeroHuespedes,
    this.observaciones,
  });

  final int huespedId;
  final int habitacionId;
  final DateTime fechaEntrada;
  final DateTime fechaSalida;
  final int numeroHuespedes;
  final String? observaciones;

  Map<String, dynamic> toJson() {
    return {
      'huespedId': huespedId,
      'habitacionId': habitacionId,
      'fechaEntrada': formatearFecha(fechaEntrada),
      'fechaSalida': formatearFecha(fechaSalida),
      'numeroHuespedes': numeroHuespedes,
      'observaciones': ?observaciones,
    };
  }
}

/// Consulta de disponibilidad (`GET /api/reservas/disponibilidad`).
class DisponibilidadConsulta {
  const DisponibilidadConsulta({
    required this.entrada,
    required this.salida,
    this.huespedes = 1,
    this.tipo,
  });

  final DateTime entrada;
  final DateTime salida;
  final int huespedes;
  final String? tipo;

  Map<String, dynamic> toQuery() {
    return {
      'entrada': formatearFecha(entrada),
      'salida': formatearFecha(salida),
      'huespedes': huespedes,
      'tipo': ?tipo,
    };
  }
}
