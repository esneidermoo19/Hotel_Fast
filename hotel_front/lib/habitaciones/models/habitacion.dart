import '../../shared/utils/lectura_json.dart';
import '../../shared/utils/moneda.dart';

/// Habitacion segun `HabitacionRead` del contrato.
class Habitacion {
  const Habitacion({
    required this.id,
    required this.numero,
    required this.tipo,
    required this.capacidad,
    required this.precioPorNoche,
    required this.estado,
    required this.limpieza,
    this.descripcion,
  });

  final int id;
  final int numero;
  final String tipo;
  final int capacidad;

  /// Monto en COP (el backend lo envia como numero).
  final double precioPorNoche;

  /// `DISPONIBLE`, `OCUPADA` o `MANTENIMIENTO`.
  final String estado;

  /// `LIMPIA` o `SUCIA`.
  final String limpieza;
  final String? descripcion;

  factory Habitacion.fromJson(Map<String, dynamic> json) {
    return Habitacion(
      id: leerEntero(json['id']) ?? 0,
      numero: leerEntero(json['numero']) ?? 0,
      tipo: leerTexto(json['tipo']) ?? '',
      capacidad: leerEntero(json['capacidad']) ?? 0,
      precioPorNoche: leerMonto(json['precioPorNoche']) ?? 0,
      estado: leerTexto(json['estado']) ?? '',
      limpieza: leerTexto(json['limpieza']) ?? '',
      descripcion: leerTexto(json['descripcion']),
    );
  }
}

/// Cuerpo de creacion y actualizacion (`HabitacionCreate`/`Update`).
class HabitacionPayload {
  const HabitacionPayload({
    required this.numero,
    required this.tipo,
    required this.capacidad,
    required this.precioPorNoche,
    required this.estado,
    this.descripcion,
  });

  final int numero;
  final String tipo;
  final int capacidad;
  final double precioPorNoche;
  final String estado;
  final String? descripcion;

  Map<String, dynamic> toJson() {
    return {
      'numero': numero,
      'tipo': tipo,
      'capacidad': capacidad,
      'precioPorNoche': precioPorNoche,
      'estado': estado,
      if (descripcion != null) 'descripcion': descripcion,
    };
  }
}
