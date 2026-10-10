import 'package:flutter/material.dart';

import '../auth/models/usuario.dart';

/// Modulo navegable del shell. En esta fase solo son entradas de menu con una
/// vista placeholder; las pantallas reales llegan en fases posteriores.
class ModuloApp {
  const ModuloApp({
    required this.id,
    required this.etiqueta,
    required this.icono,
    this.soloAdmin = false,
  });

  /// Identificador estable para enrutar el contenido.
  final String id;
  final String etiqueta;
  final IconData icono;

  /// Si es `true`, solo se muestra a usuarios `ADMIN`.
  final bool soloAdmin;
}

const List<ModuloApp> _todos = <ModuloApp>[
  ModuloApp(id: 'panel', etiqueta: 'Panel', icono: Icons.dashboard_outlined),
  ModuloApp(
    id: 'habitaciones',
    etiqueta: 'Habitaciones',
    icono: Icons.meeting_room_outlined,
  ),
  ModuloApp(
    id: 'huespedes',
    etiqueta: 'Huéspedes',
    icono: Icons.people_outline,
  ),
  ModuloApp(
    id: 'reservas',
    etiqueta: 'Reservas',
    icono: Icons.event_available_outlined,
  ),
  ModuloApp(
    id: 'usuarios',
    etiqueta: 'Usuarios',
    icono: Icons.manage_accounts_outlined,
    soloAdmin: true,
  ),
  ModuloApp(
    id: 'auditoria',
    etiqueta: 'Auditoría',
    icono: Icons.history_outlined,
    soloAdmin: true,
  ),
];

/// Modulos visibles segun el rol del usuario autenticado.
List<ModuloApp> modulosPara(Usuario? usuario) {
  final esAdmin = usuario?.esAdministrador ?? false;
  return _todos
      .where((modulo) => !modulo.soloAdmin || esAdmin)
      .toList(growable: false);
}
