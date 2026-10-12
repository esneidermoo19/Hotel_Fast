import 'package:flutter/material.dart';

import '../core/network/api_exception.dart';
import '../shared/utils/moneda.dart';
import '../shared/utils/saludo.dart';
import '../theme/app_theme.dart';
import '../widgets/aviso_error.dart';
import '../widgets/esqueleto.dart';
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
          return const ListaEsqueleto(filas: 4);
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

/// Acento semantico para tarjetas accionables: icono + etiqueta, no solo color.
class _Acento {
  const _Acento({
    required this.icono,
    required this.texto,
    required this.color,
  });

  final IconData icono;
  final String texto;
  final Color color;
}

class _Indicador {
  const _Indicador({
    required this.etiqueta,
    required this.valor,
    required this.icono,
    this.acento,
    this.mostrarAcento = false,
  });

  final String etiqueta;

  /// Valor ya formateado para mostrar (entero, porcentaje o importe).
  final String valor;
  final IconData icono;
  final _Acento? acento;

  /// Si el acento debe mostrarse (p. ej. solo cuando el conteo es mayor que 0).
  final bool mostrarAcento;
}

class _Indicadores extends StatelessWidget {
  const _Indicadores({required this.resumen});

  final DashboardResumen resumen;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final tarjetas = <_Indicador>[
      _Indicador(
        etiqueta: 'Reservas activas',
        valor: '${resumen.reservasActivas}',
        icono: Icons.event_available_outlined,
      ),
      _Indicador(
        etiqueta: 'Pendientes de check-in',
        valor: '${resumen.reservasPendientesCheckIn}',
        icono: Icons.login_outlined,
        mostrarAcento: resumen.reservasPendientesCheckIn > 0,
        acento: const _Acento(
          icono: Icons.schedule,
          texto: 'Requiere atención',
          color: Color(0xFFB45309),
        ),
      ),
      _Indicador(
        etiqueta: 'Huéspedes alojados',
        valor: '${resumen.huespedesAlojados}',
        icono: Icons.people_outline,
      ),
      _Indicador(
        etiqueta: 'Check-outs del día',
        valor: '${resumen.checkOutsDelDia}',
        icono: Icons.logout_outlined,
      ),
      _Indicador(
        etiqueta: 'Habitaciones disponibles',
        valor: '${resumen.habitacionesDisponibles}',
        icono: Icons.check_circle_outline,
      ),
      _Indicador(
        etiqueta: 'Habitaciones ocupadas',
        valor: '${resumen.habitacionesOcupadas}',
        icono: Icons.meeting_room_outlined,
      ),
      _Indicador(
        etiqueta: 'En mantenimiento',
        valor: '${resumen.habitacionesEnMantenimiento}',
        icono: Icons.build_outlined,
      ),
      _Indicador(
        etiqueta: 'Cuentas con saldo',
        valor: '${resumen.cuentasConSaldoPendiente}',
        icono: Icons.receipt_long_outlined,
        mostrarAcento: resumen.cuentasConSaldoPendiente > 0,
        acento: const _Acento(
          icono: Icons.warning_amber_rounded,
          texto: 'Saldo pendiente',
          color: Color(0xFFB91C1C),
        ),
      ),
      _Indicador(
        etiqueta: 'Ingresos del día',
        valor: formatearMonto(resumen.ingresosDelDia),
        icono: Icons.payments_outlined,
      ),
      _Indicador(
        etiqueta: 'RevPAR',
        valor: formatearMonto(resumen.revpar),
        icono: Icons.trending_up_outlined,
      ),
      _Indicador(
        etiqueta: 'Balance de caja',
        valor: formatearMonto(resumen.balanceCaja),
        icono: Icons.account_balance_wallet_outlined,
      ),
    ];

    return CustomScrollView(
      slivers: [
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 0),
          sliver: SliverToBoxAdapter(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  saludoDelDia(DateTime.now()),
                  style: tema.textTheme.headlineSmall,
                ),
                const SizedBox(height: 4),
                Text(
                  'Resumen operativo',
                  style: tema.textTheme.titleMedium?.copyWith(
                    color: tema.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        ),
        SliverPadding(
          padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
          sliver: SliverToBoxAdapter(child: _HeroOcupacion(resumen: resumen)),
        ),
        SliverPadding(
          padding: const EdgeInsets.all(24),
          sliver: SliverGrid(
            gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
              maxCrossAxisExtent: 320,
              mainAxisSpacing: 16,
              crossAxisSpacing: 16,
              mainAxisExtent: 168,
            ),
            delegate: SliverChildBuilderDelegate(
              (context, indice) => _TarjetaIndicador(datos: tarjetas[indice]),
              childCount: tarjetas.length,
            ),
          ),
        ),
      ],
    );
  }
}

String _formatearPorcentaje(double valor) => '${valor.toStringAsFixed(1)}%';

/// Tarjeta destacada con la ocupacion del hotel y su barra de progreso.
class _HeroOcupacion extends StatelessWidget {
  const _HeroOcupacion({required this.resumen});

  final DashboardResumen resumen;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final operativas =
        resumen.habitacionesDisponibles + resumen.habitacionesOcupadas;
    final fraccion = (resumen.tasaOcupacion / 100).clamp(0.0, 1.0);
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [AppTheme.midnight, AppTheme.midnightClaro],
        ),
        boxShadow: [
          BoxShadow(
            color: AppTheme.midnight.withValues(alpha: 0.28),
            blurRadius: 24,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Ocupación',
                      style: tema.textTheme.titleMedium?.copyWith(
                        color: AppTheme.oroClaro,
                        letterSpacing: 0.4,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '$operativas habitaciones operativas',
                      style: tema.textTheme.bodySmall?.copyWith(
                        color: Colors.white.withValues(alpha: 0.7),
                      ),
                    ),
                  ],
                ),
              ),
              Text(
                _formatearPorcentaje(resumen.tasaOcupacion),
                style: tema.textTheme.displaySmall?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: LinearProgressIndicator(
              value: fraccion,
              minHeight: 12,
              backgroundColor: Colors.white.withValues(alpha: 0.15),
              valueColor: const AlwaysStoppedAnimation(AppTheme.oro),
            ),
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 20,
            runSpacing: 8,
            children: [
              _DatoHero(
                color: AppTheme.esmeralda,
                valor: resumen.habitacionesDisponibles,
                texto: 'disponibles',
              ),
              _DatoHero(
                color: AppTheme.borgona,
                valor: resumen.habitacionesOcupadas,
                texto: 'ocupadas',
              ),
              _DatoHero(
                color: AppTheme.ambar,
                valor: resumen.habitacionesEnMantenimiento,
                texto: 'mantenimiento',
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _DatoHero extends StatelessWidget {
  const _DatoHero({
    required this.color,
    required this.valor,
    required this.texto,
  });

  final Color color;
  final int valor;
  final String texto;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 6),
        Text(
          '$valor',
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w700,
            fontSize: 15,
          ),
        ),
        const SizedBox(width: 4),
        Text(
          texto,
          style: TextStyle(
            color: Colors.white.withValues(alpha: 0.75),
            fontSize: 13,
          ),
        ),
      ],
    );
  }
}

class _TarjetaIndicador extends StatelessWidget {
  const _TarjetaIndicador({required this.datos});

  final _Indicador datos;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final acento = datos.acento;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CircleAvatar(
              radius: 20,
              backgroundColor: AppTheme.oro,
              child: Icon(datos.icono, size: 20, color: AppTheme.midnight),
            ),
            const Spacer(),
            Text(
              datos.valor,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: tema.textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w800,
                color: tema.colorScheme.onSurface,
              ),
            ),
            Text(
              datos.etiqueta,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: tema.textTheme.bodySmall?.copyWith(
                color: tema.colorScheme.onSurfaceVariant,
              ),
            ),
            if (acento != null && datos.mostrarAcento) ...[
              const SizedBox(height: 6),
              Row(
                children: [
                  Icon(acento.icono, size: 14, color: acento.color),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      acento.texto,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        color: acento.color,
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
