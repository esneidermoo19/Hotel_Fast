import 'package:flutter/material.dart';

import 'app_scope.dart';
import 'auth/auth_controller.dart';
import 'auth/auth_scope.dart';
import 'catalogos/catalogos_service.dart';
import 'dashboard/dashboard_service.dart';
import 'habitaciones/habitaciones_service.dart';
import 'huespedes/huespedes_service.dart';
import 'reservas/reservas_service.dart';
import 'screens/login_screen.dart';
import 'screens/shell_screen.dart';
import 'widgets/pantalla_carga.dart';

/// Raiz de la aplicacion. Decide entre carga, login y shell segun el estado de
/// autenticacion (guardas por sesion). El estado de rol se aplica dentro del
/// shell para filtrar los modulos.
class HotelApp extends StatefulWidget {
  const HotelApp({super.key, required this.controller});

  final AuthController controller;

  @override
  State<HotelApp> createState() => _HotelAppState();
}

class _HotelAppState extends State<HotelApp> {
  late final CatalogosService _catalogos = CatalogosService(
    widget.controller.auth.api,
  );
  late final DashboardService _dashboard = DashboardService(
    widget.controller.auth.api,
  );
  late final HabitacionesService _habitaciones = HabitacionesService(
    widget.controller.auth.api,
  );
  late final HuespedesService _huespedes = HuespedesService(
    widget.controller.auth.api,
  );
  late final ReservasService _reservas = ReservasService(
    widget.controller.auth.api,
  );

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hotel Fast',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1565C0)),
      ),
      home: AuthScope(
        controller: widget.controller,
        child: AppScope(
          catalogos: _catalogos,
          dashboard: _dashboard,
          habitaciones: _habitaciones,
          huespedes: _huespedes,
          reservas: _reservas,
          child: AnimatedBuilder(
            animation: widget.controller,
            builder: (context, _) {
              return switch (widget.controller.estado) {
                EstadoAuth.cargando => const PantallaCarga(),
                EstadoAuth.sinSesion => const LoginScreen(),
                EstadoAuth.autenticado => const ShellScreen(),
              };
            },
          ),
        ),
      ),
    );
  }
}
