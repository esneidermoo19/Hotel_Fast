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
      // Verde esmeralda suave.
      'DISPONIBLE' ||
      'CHECK_IN' ||
      'ACTIVO' ||
      'LIMPIA' => (const Color(0xFFECFDF5), const Color(0xFF047857)),
      // Rojo borgona suave.
      'OCUPADA' ||
      'CANCELADA' => (const Color(0xFFFEF2F2), const Color(0xFFB91C1C)),
      // Ambar calido.
      'MANTENIMIENTO' ||
      'INACTIVO' ||
      'SUCIA' ||
      'PENDIENTE' ||
      'NO_SHOW' => (const Color(0xFFFFFBEB), const Color(0xFFB45309)),
      // Azul indigo suave (confirmada).
      'CONFIRMADA' => (const Color(0xFFEFF6FF), const Color(0xFF1D4ED8)),
      // Teal suave (check-out).
      'CHECK_OUT' => (const Color(0xFFF0FDFA), const Color(0xFF0F766E)),
      _ => (const Color(0xFFF1F5F9), const Color(0xFF475569)),
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
