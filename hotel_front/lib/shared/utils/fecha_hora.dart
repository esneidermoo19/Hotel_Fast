/// Utilidades de fecha y hora para el contrato de la API.
///
/// - Las fechas de estancia viajan como `YYYY-MM-DD` (sin zona).
/// - Las marcas de tiempo viajan en ISO-8601; si no traen offset se asumen UTC
///   (asi lo documenta `docs/API_CONTRACT.md`).
library;

final RegExp _conZona = RegExp(r'(Z|[+-]\d{2}:?\d{2})$');

/// Lee una fecha `YYYY-MM-DD` (o ISO) como `DateTime` sin componente horario.
///
/// Devuelve la fecha en hora local con hora 00:00 para evitar corrimientos.
DateTime? leerFecha(Object? valor) {
  if (valor == null) return null;
  if (valor is DateTime) {
    return DateTime(valor.year, valor.month, valor.day);
  }
  final texto = valor is String ? valor.trim() : valor.toString().trim();
  if (texto.isEmpty) return null;
  final parseado = DateTime.tryParse(texto);
  if (parseado == null) return null;
  return DateTime(parseado.year, parseado.month, parseado.day);
}

/// Lee una marca de tiempo ISO-8601 y la normaliza a UTC.
///
/// Si la cadena no incluye zona, se interpreta como UTC.
DateTime? leerFechaHora(Object? valor) {
  if (valor == null) return null;
  if (valor is DateTime) return valor.toUtc();
  final texto = valor is String ? valor.trim() : valor.toString().trim();
  if (texto.isEmpty) return null;
  final normalizado = _conZona.hasMatch(texto) ? texto : '${texto}Z';
  return DateTime.tryParse(normalizado)?.toUtc();
}

/// Formatea una fecha como `YYYY-MM-DD` (para query params o cuerpos).
String formatearFecha(DateTime fecha) {
  final anio = fecha.year.toString().padLeft(4, '0');
  final mes = fecha.month.toString().padLeft(2, '0');
  final dia = fecha.day.toString().padLeft(2, '0');
  return '$anio-$mes-$dia';
}

/// Formatea una marca de tiempo como ISO-8601 en UTC.
String formatearFechaHoraUtc(DateTime fecha) {
  final utc = fecha.toUtc();
  final hora = utc.hour.toString().padLeft(2, '0');
  final minuto = utc.minute.toString().padLeft(2, '0');
  final segundo = utc.second.toString().padLeft(2, '0');
  return '${formatearFecha(utc)}T$hora:$minuto:${segundo}Z';
}
