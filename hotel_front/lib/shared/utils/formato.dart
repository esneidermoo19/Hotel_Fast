/// Convierte un valor de enum de la API a etiqueta legible.
///
/// Ejemplos: `PRESIDENCIAL` -> `Presidencial`, `CHECK_IN` -> `Check in`.
String humanizar(String valor) {
  return valor
      .split('_')
      .map(
        (parte) => parte.isEmpty
            ? parte
            : parte.substring(0, 1).toUpperCase() +
                  parte.substring(1).toLowerCase(),
      )
      .join(' ');
}

/// Iniciales (hasta dos) de un nombre para el avatar.
///
/// Tolerante a nombres vacios (devuelve `?`), de una sola palabra (una inicial)
/// y con tildes (conserva la letra, p. ej. `Jose` o `José` -> `J`).
String iniciales(String nombre) {
  final palabras = nombre
      .trim()
      .split(RegExp(r'\s+'))
      .where((palabra) => palabra.isNotEmpty)
      .toList();
  if (palabras.isEmpty) return '?';

  String primera(String palabra) => palabra[0].toUpperCase();
  final inicial = primera(palabras.first);
  final segunda = palabras.length > 1 ? primera(palabras.last) : '';
  return '$inicial$segunda';
}
