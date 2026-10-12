/// Saludo y fecha del dia en espanol, segun la hora local.
///
/// Sin dependencias externas: los nombres de dias y meses se definen aqui para
/// evitar agregar `intl` solo para un saludo. Las funciones son puras y
/// deterministas (reciben [DateTime]) para poder probarlas sin depender del
/// reloj del sistema.
library;

const List<String> _dias = [
  'lunes',
  'martes',
  'miércoles',
  'jueves',
  'viernes',
  'sábado',
  'domingo',
];

const List<String> _meses = [
  'enero',
  'febrero',
  'marzo',
  'abril',
  'mayo',
  'junio',
  'julio',
  'agosto',
  'septiembre',
  'octubre',
  'noviembre',
  'diciembre',
];

/// Saludo segun la franja horaria: dias (5-11), tardes (12-18), noches (resto).
String saludoPorHora(DateTime ahora) {
  final hora = ahora.hour;
  if (hora >= 5 && hora < 12) return 'Buenos días';
  if (hora >= 12 && hora < 19) return 'Buenas tardes';
  return 'Buenas noches';
}

/// Fecha legible, p. ej. `sabado, 10 de octubre`.
String fechaLegible(DateTime ahora) {
  final dia = _dias[ahora.weekday - 1];
  final mes = _meses[ahora.month - 1];
  return '$dia, ${ahora.day} de $mes';
}

/// Saludo completo con la fecha del dia.
String saludoDelDia(DateTime ahora) {
  return '${saludoPorHora(ahora)} · ${fechaLegible(ahora)}';
}
