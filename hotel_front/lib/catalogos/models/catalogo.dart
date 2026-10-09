import '../../shared/utils/lectura_json.dart';

/// Catalogo del sistema (`GET /api/catalogos`): valores admitidos por el
/// backend para poblar desplegables sin duplicarlos en el cliente.
class Catalogo {
  const Catalogo({
    required this.nombre,
    required this.etiqueta,
    required this.valores,
  });

  final String nombre;
  final String etiqueta;
  final List<String> valores;

  factory Catalogo.fromJson(Map<String, dynamic> json) {
    final valores = json['valores'];
    return Catalogo(
      nombre: leerTexto(json['nombre']) ?? '',
      etiqueta: leerTexto(json['etiqueta']) ?? '',
      valores: valores is List
          ? valores.whereType<String>().toList(growable: false)
          : const <String>[],
    );
  }
}
