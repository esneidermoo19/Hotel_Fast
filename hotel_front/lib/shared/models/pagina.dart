import '../utils/lectura_json.dart';

/// Respuesta paginada unificada del backend.
///
/// Forma JSON: `{ "items": [...], "total": int, "pagina": int, "tamano": int }`.
class Pagina<T> {
  const Pagina({
    required this.items,
    required this.total,
    required this.pagina,
    required this.tamano,
  });

  final List<T> items;
  final int total;
  final int pagina;
  final int tamano;

  /// `true` si existe una pagina siguiente con los parametros actuales.
  bool get tienePaginaSiguiente => pagina * tamano < total;

  /// Construye una [Pagina] a partir de un mapa JSON y un conversor de item.
  factory Pagina.fromJson(
    Map<String, dynamic> json,
    T Function(Map<String, dynamic> item) convertir,
  ) {
    final items = leerListaDeMapas(json['items'])
        .map(convertir)
        .toList(growable: false);
    return Pagina<T>(
      items: items,
      total: leerEntero(json['total']) ?? items.length,
      pagina: leerEntero(json['pagina']) ?? 1,
      tamano: leerEntero(json['tamano']) ?? items.length,
    );
  }

  @override
  String toString() =>
      'Pagina<$T>(items: ${items.length}, total: $total, '
      'pagina: $pagina, tamano: $tamano)';
}
