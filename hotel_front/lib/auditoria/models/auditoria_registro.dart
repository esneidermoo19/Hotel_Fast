import '../../shared/utils/fecha_hora.dart';
import '../../shared/utils/lectura_json.dart';

/// Registro de auditoria (`AuditoriaRead`).
class AuditoriaRegistro {
  const AuditoriaRegistro({
    required this.id,
    required this.accion,
    required this.entidad,
    this.usuarioId,
    this.entidadId,
    this.ip,
    this.detalle,
    required this.createdAt,
  });

  final int id;
  final String accion;
  final String entidad;
  final int? usuarioId;
  final int? entidadId;
  final String? ip;

  /// Campos sensibles ya redactados por el backend (`[REDACTADO]`).
  final Map<String, dynamic>? detalle;
  final DateTime createdAt;

  /// Resumen corto del detalle para listados.
  String get resumenDetalle {
    final mapa = detalle;
    if (mapa == null || mapa.isEmpty) return '';
    return mapa.entries
        .map((entrada) => '${entrada.key}: ${entrada.value}')
        .join(', ');
  }

  factory AuditoriaRegistro.fromJson(Map<String, dynamic> json) {
    return AuditoriaRegistro(
      id: leerEntero(json['id']) ?? 0,
      accion: leerTexto(json['accion']) ?? '',
      entidad: leerTexto(json['entidad']) ?? '',
      usuarioId: leerEntero(json['usuarioId']),
      entidadId: leerEntero(json['entidadId']),
      ip: leerTexto(json['ip']),
      detalle: leerMapa(json['detalle']),
      createdAt:
          leerFechaHora(json['createdAt']) ??
          DateTime.fromMillisecondsSinceEpoch(0),
    );
  }
}
