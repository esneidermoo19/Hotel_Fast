import 'package:flutter/widgets.dart';

import 'catalogos/catalogos_service.dart';
import 'dashboard/dashboard_service.dart';

/// Provee a las pantallas los servicios compartidos de la aplicacion.
///
/// [InheritedWidget] nativo; las instancias son estables (se crean una vez en
/// `HotelApp`), por lo que no hay que notificar cambios.
class AppScope extends InheritedWidget {
  const AppScope({
    super.key,
    required this.catalogos,
    required this.dashboard,
    required super.child,
  });

  final CatalogosService catalogos;
  final DashboardService dashboard;

  static AppScope of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<AppScope>();
    assert(scope != null, 'No se encontro AppScope en el arbol de widgets');
    return scope!;
  }

  @override
  bool updateShouldNotify(AppScope oldWidget) => false;
}
