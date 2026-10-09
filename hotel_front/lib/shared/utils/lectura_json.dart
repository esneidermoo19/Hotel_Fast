/// Lectura defensiva de valores JSON.
///
/// El backend responde en camelCase; estas utilidades convierten valores sin
/// lanzar excepciones cuando el dato falta o llega con otro tipo, para que los
/// modelos no dependan de casts fragiles.
library;

/// Devuelve el mapa si [valor] es un objeto JSON; `null` en otro caso.
Map<String, dynamic>? leerMapa(Object? valor) {
  if (valor is Map) {
    return valor.cast<String, dynamic>();
  }
  return null;
}

/// Devuelve una lista de mapas a partir de un arreglo JSON.
List<Map<String, dynamic>> leerListaDeMapas(Object? valor) {
  if (valor is List) {
    return valor
        .whereType<Map>()
        .map((item) => item.cast<String, dynamic>())
        .toList(growable: false);
  }
  return const <Map<String, dynamic>>[];
}

/// Lee un entero desde `int`, `num` o una cadena numerica.
int? leerEntero(Object? valor) {
  if (valor == null) return null;
  if (valor is int) return valor;
  if (valor is num) return valor.toInt();
  if (valor is String) return int.tryParse(valor.trim());
  return null;
}

/// Lee un decimal desde `num` o una cadena numerica.
double? leerDecimal(Object? valor) {
  if (valor == null) return null;
  if (valor is num) return valor.toDouble();
  if (valor is String) return double.tryParse(valor.trim());
  return null;
}

/// Lee un texto no vacio; `null` si no es una cadena o esta vacio.
String? leerTexto(Object? valor) {
  if (valor is String) {
    return valor.isEmpty ? null : valor;
  }
  return null;
}

/// Lee un booleano desde `bool` o desde cadenas `true`/`false`.
bool? leerBooleano(Object? valor) {
  if (valor is bool) return valor;
  if (valor is String) {
    final limpio = valor.trim().toLowerCase();
    if (limpio == 'true') return true;
    if (limpio == 'false') return false;
  }
  return null;
}
