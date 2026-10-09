/// Utilidades para importes monetarios (COP).
///
/// El backend envia `Decimal` como numero JSON (por ejemplo `120.5`); se lee
/// como `double` solo para presentacion. Los calculos financieros deben seguir
/// siendo responsabilidad del backend.
library;

/// Lee un importe desde `num` o una cadena numerica.
///
/// Devuelve `null` si el valor no representa un numero.
double? leerMonto(Object? valor) {
  if (valor == null) return null;
  if (valor is num) return valor.toDouble();
  if (valor is String) return double.tryParse(valor.trim());
  return null;
}

/// Formatea un importe con separador de miles `.` y decimal `,` (es-CO).
///
/// Por ejemplo, `1234567.5` con decimales produce `$ 1.234.567,50`.
/// Devuelve cadena vacia si el valor no es numerico.
String formatearMonto(
  Object? valor, {
  bool decimales = true,
  String simbolo = r'$',
}) {
  final monto = leerMonto(valor);
  if (monto == null) return '';

  final negativo = monto.isNegative;
  final absoluto = monto.abs();
  var entero = absoluto.truncate();
  var centavos = ((absoluto - entero) * 100).round();
  if (centavos == 100) {
    entero += 1;
    centavos = 0;
  }

  final buffer = StringBuffer();
  if (negativo) buffer.write('-');
  buffer.write(simbolo);
  buffer.write(' ');
  buffer.write(_agruparMiles(entero.toString()));
  if (decimales) {
    buffer.write(',');
    buffer.write(centavos.toString().padLeft(2, '0'));
  }
  return buffer.toString();
}

String _agruparMiles(String digitos) {
  final buffer = StringBuffer();
  final longitud = digitos.length;
  for (var i = 0; i < longitud; i++) {
    if (i > 0 && (longitud - i) % 3 == 0) {
      buffer.write('.');
    }
    buffer.write(digitos[i]);
  }
  return buffer.toString();
}
