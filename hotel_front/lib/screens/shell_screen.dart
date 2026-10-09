import 'dart:async';

import 'package:flutter/material.dart';

import '../app_scope.dart';
import '../auth/auth_scope.dart';
import '../auth/models/usuario.dart';
import '../dashboard/dashboard_view.dart';
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

  static const double _anchoEscritorio = 900;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_catalogosPrecargados) return;
    _catalogosPrecargados = true;
    unawaited(AppScope.of(context).catalogos.precargar());
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
    final contenido = moduloActual.id == 'panel'
        ? DashboardView(service: AppScope.of(context).dashboard)
        : _ContenidoModulo(modulo: moduloActual, usuario: usuario);

    return Scaffold(
      appBar: AppBar(
        title: Text(esEscritorio ? 'Hotel Fast' : moduloActual.etiqueta),
        actions: [
          if (usuario != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Center(child: Text('${usuario.nombre} (${usuario.role})')),
            ),
          IconButton(
            tooltip: 'Cerrar sesion',
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
                Expanded(child: contenido),
              ],
            )
          : contenido,
    );
  }

  Future<void> _confirmarCierre(BuildContext context) async {
    final auth = AuthScope.de(context);
    final confirmar = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cerrar sesion'),
        content: const Text('Se cerrara tu sesion actual. ¿Deseas continuar?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Cerrar sesion'),
          ),
        ],
      ),
    );
    if (confirmar == true) {
      await auth.cerrarSesion();
    }
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
              leading: const Icon(Icons.account_circle_outlined),
              title: Text(usuario?.nombre ?? ''),
              subtitle: Text(usuario?.role ?? ''),
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
              title: const Text('Cerrar sesion'),
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
