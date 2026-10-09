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
