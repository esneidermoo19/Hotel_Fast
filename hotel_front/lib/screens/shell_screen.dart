import 'dart:async';

import 'package:flutter/material.dart';

import '../app_scope.dart';
import '../auditoria/auditoria_view.dart';
import '../auth/auth_scope.dart';
import '../auth/models/usuario.dart';
import '../dashboard/dashboard_view.dart';
import '../habitaciones/habitaciones_view.dart';
import '../huespedes/huespedes_view.dart';
import '../reservas/reservas_view.dart';
import '../shared/utils/formato.dart';
import '../theme/app_theme.dart';
import '../usuarios/usuarios_view.dart';
import 'modulos.dart';

/// Shell principal tras iniciar sesion: menu lateral (escritorio) o drawer
/// (pantallas angostas), area de contenido y boton de cierre de sesion.
class ShellScreen extends StatefulWidget {
  const ShellScreen({super.key});

  @override
  State<ShellScreen> createState() => _ShellScreenState();
}

class _ShellScreenState extends State<ShellScreen> {
  int _indice = 0;
  bool _catalogosPrecargados = false;

  /// Modulos ya construidos (para no recargar datos al volver a uno visitado).
  final List<Widget?> _modulosCacheados = [];

  static const double _anchoEscritorio = 900;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_catalogosPrecargados) return;
    _catalogosPrecargados = true;
    unawaited(AppScope.of(context).catalogos.precargar());
  }

  Widget _construirModulo(ModuloApp modulo, AppScope scope, Usuario? usuario) {
    switch (modulo.id) {
      case 'panel':
        return DashboardView(service: scope.dashboard);
      case 'habitaciones':
        return HabitacionesView(
          service: scope.habitaciones,
          catalogos: scope.catalogos,
          esAdmin: usuario?.esAdministrador ?? false,
        );
      case 'huespedes':
        return HuespedesView(
          service: scope.huespedes,
          catalogos: scope.catalogos,
          esAdmin: usuario?.esAdministrador ?? false,
        );
      case 'reservas':
        return ReservasView(
          service: scope.reservas,
          catalogos: scope.catalogos,
          huespedes: scope.huespedes,
          cuentas: scope.cuentas,
          consumos: scope.consumos,
          pagos: scope.pagos,
        );
      case 'usuarios':
        return UsuariosView(
          service: scope.usuarios,
          catalogos: scope.catalogos,
        );
      case 'auditoria':
        return AuditoriaView(service: scope.auditoria);
      default:
        return _ContenidoModulo(modulo: modulo, usuario: usuario);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = AuthScope.de(context);
    final usuario = auth.usuario;
    final modulos = modulosPara(usuario);
    final ancho = MediaQuery.sizeOf(context).width;
    final esEscritorio = ancho >= _anchoEscritorio;
    final indice = _indice < modulos.length ? _indice : 0;
    final moduloActual = modulos[indice];
    final scope = AppScope.of(context);
    final desactivarAnimaciones = MediaQuery.disableAnimationsOf(context);

    while (_modulosCacheados.length < modulos.length) {
      _modulosCacheados.add(null);
    }
    _modulosCacheados[indice] ??= _construirModulo(
      moduloActual,
      scope,
      usuario,
    );

    final areaContenido = _transicion(
      desactivarAnimaciones,
      indice,
      modulos.length,
    );

    return Scaffold(
      appBar: AppBar(
        title: Text(esEscritorio ? 'Hotel Fast' : moduloActual.etiqueta),
        actions: [
          if (usuario != null && esEscritorio) ...[
            _AvatarIniciales(nombre: usuario.nombre),
            const SizedBox(width: 8),
            _ChipRol(role: usuario.role),
            const SizedBox(width: 4),
          ],
          IconButton(
            tooltip: 'Cerrar sesión',
            icon: const Icon(Icons.logout),
            onPressed: () => _confirmarCierre(context),
          ),
        ],
      ),
      drawer: esEscritorio
          ? null
          : _MenuDrawer(
              modulos: modulos,
              indice: indice,
              usuario: usuario,
              alSeleccionar: (i) {
                setState(() => _indice = i);
                Navigator.of(context).pop();
              },
              alCerrarSesion: () => _confirmarCierre(context),
            ),
      body: esEscritorio
          ? Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                NavigationRail(
                  extended: ancho >= 1200,
                  selectedIndex: indice,
                  onDestinationSelected: (i) => setState(() => _indice = i),
                  labelType: ancho >= 1200
                      ? NavigationRailLabelType.none
                      : NavigationRailLabelType.all,
                  destinations: [
                    for (final modulo in modulos)
                      NavigationRailDestination(
                        icon: Icon(modulo.icono),
                        label: Text(modulo.etiqueta),
                      ),
                  ],
                ),
                const VerticalDivider(width: 1),
                Expanded(child: areaContenido),
              ],
            )
          : areaContenido,
    );
  }

  /// Fundido suave entre modulos. Mantiene vivos los ya visitados (no recargan
  /// datos) y respeta la preferencia de reducir animaciones.
  Widget _transicion(bool desactivarAnimaciones, int indice, int total) {
    return Stack(
      children: [
        for (var i = 0; i < total; i++)
          IgnorePointer(
            ignoring: i != indice,
            child: ExcludeSemantics(
              excluding: i != indice,
              child: AnimatedOpacity(
                duration: desactivarAnimaciones
                    ? Duration.zero
                    : const Duration(milliseconds: 220),
                curve: Curves.easeOut,
                opacity: i == indice ? 1 : 0,
                child: _modulosCacheados[i] ?? const SizedBox.shrink(),
              ),
            ),
          ),
      ],
    );
  }

  Future<void> _confirmarCierre(BuildContext context) async {
    final auth = AuthScope.de(context);
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cerrar sesión'),
        content: const Text('Se cerrará tu sesión actual. ¿Deseas continuar?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Cerrar sesión'),
          ),
        ],
      ),
    );
    if (confirmar == true) {
      await auth.cerrarSesion();
    }
  }
}

/// Avatar con las iniciales del usuario.
class _AvatarIniciales extends StatelessWidget {
  const _AvatarIniciales({required this.nombre});

  final String nombre;

  @override
  Widget build(BuildContext context) {
    return CircleAvatar(
      radius: 16,
      backgroundColor: AppTheme.oro,
      child: Text(
        iniciales(nombre),
        style: const TextStyle(
          color: AppTheme.midnight,
          fontWeight: FontWeight.w700,
          fontSize: 13,
        ),
      ),
    );
  }
}

/// Chip con el rol del usuario.
class _ChipRol extends StatelessWidget {
  const _ChipRol({required this.role});

  final String role;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: AppTheme.oro.withValues(alpha: 0.6)),
      ),
      child: Text(
        humanizar(role),
        style: const TextStyle(
          color: AppTheme.oro,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class _MenuDrawer extends StatelessWidget {
  const _MenuDrawer({
    required this.modulos,
    required this.indice,
    required this.usuario,
    required this.alSeleccionar,
    required this.alCerrarSesion,
  });

  final List<ModuloApp> modulos;
  final int indice;
  final Usuario? usuario;
  final ValueChanged<int> alSeleccionar;
  final VoidCallback alCerrarSesion;

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: SafeArea(
        child: Column(
          children: [
            ListTile(
              leading: CircleAvatar(
                backgroundColor: AppTheme.oro,
                child: Text(
                  iniciales(usuario?.nombre ?? ''),
                  style: const TextStyle(
                    color: AppTheme.midnight,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              title: Text(usuario?.nombre ?? ''),
              subtitle: Text(humanizar(usuario?.role ?? '')),
            ),
            const Divider(),
            Expanded(
              child: ListView(
                children: [
                  for (var i = 0; i < modulos.length; i++)
                    ListTile(
                      leading: Icon(modulos[i].icono),
                      title: Text(modulos[i].etiqueta),
                      selected: i == indice,
                      onTap: () => alSeleccionar(i),
                    ),
                ],
              ),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Cerrar sesión'),
              onTap: alCerrarSesion,
            ),
          ],
        ),
      ),
    );
  }
}

/// Vista provisional de cada modulo hasta que se implementen sus pantallas.
class _ContenidoModulo extends StatelessWidget {
  const _ContenidoModulo({required this.modulo, required this.usuario});

  final ModuloApp modulo;
  final Usuario? usuario;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            modulo.icono,
            size: 64,
            color: Theme.of(context).colorScheme.primary,
          ),
          const SizedBox(height: 12),
          Text(
            modulo.etiqueta,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'Bienvenido, ${usuario?.nombre ?? ''}',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 4),
          Text(
            'Modulo en construccion',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}
