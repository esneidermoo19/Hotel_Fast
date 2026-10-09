import 'package:flutter/widgets.dart';

import 'catalogos/catalogos_service.dart';
import 'dashboard/dashboard_service.dart';
import 'habitaciones/habitaciones_service.dart';
import 'huespedes/huespedes_service.dart';
import 'reservas/reservas_service.dart';

/// Provee a las pantallas los servicios compartidos de la aplicacion.
///
/// [InheritedWidget] nativo; las instancias son estables (se crean una vez en
/// `HotelApp`), por lo que no hay que notificar cambios.
class AppScope extends InheritedWidget {
  const AppScope({
    super.key,
    required this.catalogos,
    required this.dashboard,
    required this.habitaciones,
    required this.huespedes,
    required this.reservas,
    required super.child,
  });

  final CatalogosService catalogos;
  final DashboardService dashboard;
  final HabitacionesService habitaciones;
  final HuespedesService huespedes;
  final ReservasService reservas;

  static AppScope of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<AppScope>();
    assert(scope != null, 'No se encontro AppScope en el arbol de widgets');
    return scope!;
  }

  @override
  bool updateShouldNotify(AppScope oldWidget) => false;
}
