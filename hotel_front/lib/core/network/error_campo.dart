/// Detalle por campo de un error de validacion (HTTP 422).
///
/// Corresponde a cada elemento de `errors[]` en el sobre de error del backend:
/// `{ "campo": "precioPorNoche", "mensaje": "...", "tipo": "greater_than" }`.
class ErrorCampo {
  const ErrorCampo({this.campo, required this.mensaje, this.tipo});

  /// Nombre del campo en camelCase, o `null` si el error no es de un campo.
  final String? campo;

  /// Mensaje legible del backend.
  final String mensaje;

  /// Tipo de validacion de Pydantic (por ejemplo `greater_than`).
  final String? tipo;

  factory ErrorCampo.fromJson(Map<String, dynamic> json) {
    final mensaje = json['mensaje'];
    return ErrorCampo(
      campo: json['campo'] as String?,
      mensaje: mensaje is String && mensaje.isNotEmpty
          ? mensaje
          : 'Valor invalido',
      tipo: json['tipo'] as String?,
    );
  }

  @override
  String toString() => 'ErrorCampo($campo: $mensaje)';
}
