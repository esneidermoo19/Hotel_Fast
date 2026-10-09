import 'package:flutter/material.dart';

import '../shared/utils/formato.dart';

/// Pastilla (pill) semantica para estados de la API.
///
/// Colores pastel/suaves con texto contrastado y borde fino.
class PastillaEstado extends StatelessWidget {
  const PastillaEstado({super.key, required this.estado, this.texto});

  /// Valor del estado tal como llega del backend (p. ej. `DISPONIBLE`).
  final String estado;

  /// Texto opcional; por defecto se humaniza [estado].
  final String? texto;

  (Color fondo, Color texto) get _paleta {
    return switch (estado) {
      'DISPONIBLE' ||
      'CHECK_IN' ||
      'ACTIVO' => (const Color(0xFFDCFCE7), const Color(0xFF166534)),
      'PENDIENTE' ||
      'SUCIA' => (const Color(0xFFFEF3C7), const Color(0xFF92400E)),
      'CONFIRMADA' ||
      'OCUPADA' => (const Color(0xFFDBEAFE), const Color(0xFF1E40AF)),
      'CHECK_OUT' => (const Color(0xFFCCFBF1), const Color(0xFF115E59)),
      'CANCELADA' => (const Color(0xFFFEE2E2), const Color(0xFFB91C1C)),
      'NO_SHOW' => (const Color(0xFFFFEDD5), const Color(0xFFC2410C)),
      'MANTENIMIENTO' ||
      'INACTIVO' => (const Color(0xFFE2E8F0), const Color(0xFF475569)),
      _ => (const Color(0xFFE2E8F0), const Color(0xFF334155)),
    };
  }

  @override
  Widget build(BuildContext context) {
    final (fondo, color) = _paleta;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: fondo,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Text(
        texto ?? humanizar(estado),
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.w600,
          height: 1,
        ),
      ),
    );
  }
}
