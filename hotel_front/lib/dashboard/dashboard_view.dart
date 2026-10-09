import 'package:flutter/material.dart';

import '../core/network/api_exception.dart';
import '../widgets/aviso_error.dart';
import 'dashboard_service.dart';
import 'models/dashboard_resumen.dart';

/// Panel inicial: tarjetas con los indicadores del dia.
class DashboardView extends StatefulWidget {
  const DashboardView({super.key, required this.service});

  final DashboardService service;

  @override
  State<DashboardView> createState() => _DashboardViewState();
}

class _DashboardViewState extends State<DashboardView> {
  late Future<DashboardResumen> _futuro;

  @override
  void initState() {
    super.initState();
    _futuro = widget.service.cargar();
  }

  void _reintentar() {
    setState(() => _futuro = widget.service.cargar());
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<DashboardResumen>(
      future: _futuro,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          final err = snapshot.error;
          return AvisoError(
            mensaje: err is ApiException
                ? err.mensaje
                : 'No se pudo cargar el panel.',
            alReintentar: _reintentar,
          );
        }
        return _Indicadores(resumen: snapshot.data!);
      },
    );
  }
}

class _Indicadores extends StatelessWidget {
  const _Indicadores({required this.resumen});

  final DashboardResumen resumen;

  @override
  Widget build(BuildContext context) {
    final tarjetas = <Widget>[
      _TarjetaIndicador(
        etiqueta: 'Reservas activas',
        valor: resumen.reservasActivas,
        icono: Icons.event_available_outlined,
      ),
      _TarjetaIndicador(
        etiqueta: 'Pendientes de check-in',
        valor: resumen.reservasPendientesCheckIn,
        icono: Icons.login_outlined,
      ),
      _TarjetaIndicador(
        etiqueta: 'Huespedes alojados',
        valor: resumen.huespedesAlojados,
        icono: Icons.people_outline,
      ),
      _TarjetaIndicador(
        etiqueta: 'Check-outs del dia',
        valor: resumen.checkOutsDelDia,
        icono: Icons.logout_outlined,
      ),
      _TarjetaIndicador(
        etiqueta: 'Habitaciones disponibles',
        valor: resumen.habitacionesDisponibles,
        icono: Icons.check_circle_outline,
      ),
      _TarjetaIndicador(
        etiqueta: 'Habitaciones ocupadas',
        valor: resumen.habitacionesOcupadas,
        icono: Icons.meeting_room_outlined,
      ),
      _TarjetaIndicador(
        etiqueta: 'En mantenimiento',
        valor: resumen.habitacionesEnMantenimiento,
        icono: Icons.build_outlined,
      ),
      _TarjetaIndicador(
        etiqueta: 'Cuentas con saldo',
        valor: resumen.cuentasConSaldoPendiente,
        icono: Icons.receipt_long_outlined,
      ),
    ];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Resumen operativo',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 16,
            runSpacing: 16,
            children: [
              for (final tarjeta in tarjetas)
                SizedBox(width: 220, child: tarjeta),
            ],
          ),
        ],
      ),
    );
  }
}

class _TarjetaIndicador extends StatelessWidget {
  const _TarjetaIndicador({
    required this.etiqueta,
    required this.valor,
    required this.icono,
  });

  final String etiqueta;
  final int valor;
  final IconData icono;

  @override
  Widget build(BuildContext context) {
    final colores = Theme.of(context).colorScheme;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: colores.primaryContainer,
              child: Icon(icono, color: colores.onPrimaryContainer),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '$valor',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  Text(etiqueta, style: Theme.of(context).textTheme.bodySmall),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
