import '../../shared/utils/fecha_hora.dart';
import '../../shared/utils/lectura_json.dart';

/// Huesped segun `HuespedRead` del contrato.
class Huesped {
  const Huesped({
    required this.id,
    required this.tipoDocumento,
    required this.numeroDocumento,
    required this.nombres,
    required this.apellidos,
    this.email,
    this.telefono,
    this.nacionalidad,
    this.fechaNacimiento,
    this.direccion,
    this.observaciones,
  });

  final int id;
  final String tipoDocumento;
  final String numeroDocumento;
  final String nombres;
  final String apellidos;
  final String? email;
  final String? telefono;
  final String? nacionalidad;
  final DateTime? fechaNacimiento;
  final String? direccion;
  final String? observaciones;

  String get nombreCompleto => '$nombres $apellidos';

  String get documento => '$tipoDocumento $numeroDocumento';

  factory Huesped.fromJson(Map<String, dynamic> json) {
    return Huesped(
      id: leerEntero(json['id']) ?? 0,
      tipoDocumento: leerTexto(json['tipoDocumento']) ?? '',
      numeroDocumento: leerTexto(json['numeroDocumento']) ?? '',
      nombres: leerTexto(json['nombres']) ?? '',
      apellidos: leerTexto(json['apellidos']) ?? '',
      email: leerTexto(json['email']),
      telefono: leerTexto(json['telefono']),
      nacionalidad: leerTexto(json['nacionalidad']),
      fechaNacimiento: leerFecha(json['fechaNacimiento']),
      direccion: leerTexto(json['direccion']),
      observaciones: leerTexto(json['observaciones']),
    );
  }
}

/// Cuerpo de creacion y actualizacion (`HuespedCreate`/`Update`).
class HuespedPayload {
  const HuespedPayload({
    required this.tipoDocumento,
    required this.numeroDocumento,
    required this.nombres,
    required this.apellidos,
    this.email,
    this.telefono,
    this.nacionalidad,
    this.fechaNacimiento,
    this.direccion,
    this.observaciones,
  });

  final String tipoDocumento;
  final String numeroDocumento;
  final String nombres;
  final String apellidos;
  final String? email;
  final String? telefono;
  final String? nacionalidad;
  final DateTime? fechaNacimiento;
  final String? direccion;
  final String? observaciones;

  Map<String, dynamic> toJson() {
    return {
      'tipoDocumento': tipoDocumento,
      'numeroDocumento': numeroDocumento,
      'nombres': nombres,
      'apellidos': apellidos,
      'email': ?email,
      'telefono': ?telefono,
      'nacionalidad': ?nacionalidad,
      if (fechaNacimiento != null)
        'fechaNacimiento': formatearFecha(fechaNacimiento!),
      'direccion': ?direccion,
      'observaciones': ?observaciones,
    };
  }
}
