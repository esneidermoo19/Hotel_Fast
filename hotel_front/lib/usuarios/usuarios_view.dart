import 'package:flutter/material.dart';

import '../auth/models/usuario.dart';
import '../catalogos/catalogos_service.dart';
import '../core/network/api_exception.dart';
import '../shared/models/pagina.dart';
import '../shared/utils/formato.dart';
import '../widgets/aviso_error.dart';
import '../widgets/barra_paginacion.dart';
import '../widgets/estado_vacio.dart';
import '../widgets/pastilla_estado.dart';
import '../widgets/tarjeta_hover.dart';
import 'models/usuario_payload.dart';
import 'usuarios_service.dart';

/// Administracion de usuarios (solo ADMIN).
class UsuariosView extends StatefulWidget {
  const UsuariosView({
    super.key,
    required this.service,
    required this.catalogos,
  });

  final UsuariosService service;
  final CatalogosService catalogos;

  @override
  State<UsuariosView> createState() => _UsuariosViewState();
}

class _UsuariosViewState extends State<UsuariosView> {
  static const int _tamano = 20;

  final _busqueda = TextEditingController();
  bool _soloActivos = false;
  String _q = '';
  int _pagina = 1;
  late Future<Pagina<Usuario>> _futuro;

  @override
  void initState() {
    super.initState();
    _futuro = _consulta();
  }

  @override
  void dispose() {
    _busqueda.dispose();
    super.dispose();
  }

  Future<Pagina<Usuario>> _consulta() {
    return widget.service.listar(
      pagina: _pagina,
      tamano: _tamano,
      q: _q.isEmpty ? null : _q,
      soloActivos: _soloActivos,
    );
  }

  void _aplicar({String? q, bool? soloActivos, int? pagina}) {
    setState(() {
      if (q != null) _q = q;
      if (soloActivos != null) _soloActivos = soloActivos;
      _pagina = pagina ?? 1;
      _futuro = _consulta();
    });
  }

  void _recargar() => _aplicar(pagina: _pagina);

  Future<void> _abrirCrear() async {
    final creado = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (_) => _DialogoNuevoUsuario(
        service: widget.service,
        catalogos: widget.catalogos,
      ),
    );
    if (creado == true && mounted) _recargar();
  }

  Future<void> _abrirEditar(Usuario usuario) async {
    final guardado = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (_) => _DialogoEditarUsuario(
        service: widget.service,
        catalogos: widget.catalogos,
        usuario: usuario,
      ),
    );
    if (guardado == true && mounted) _recargar();
  }

  Future<void> _cambiarEstado(Usuario usuario) async {
    try {
      if (usuario.activo) {
        await widget.service.desactivar(usuario.id);
      } else {
        await widget.service.reactivar(usuario.id);
      }
      if (mounted) _recargar();
    } on ApiException catch (error) {
      _mostrarError(error);
    }
  }

  Future<void> _eliminar(Usuario usuario) async {
    final confirmado = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Eliminar usuario'),
        content: Text('Se eliminaran los datos de ${usuario.username}.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Eliminar'),
          ),
        ],
      ),
    );
    if (confirmado != true) return;
    try {
      await widget.service.eliminar(usuario.id);
      if (mounted) _recargar();
    } on ApiException catch (error) {
      _mostrarError(error);
    }
  }

  void _mostrarError(ApiException error) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(error.mensaje)));
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 8),
          child: Row(
            children: [
              Text('Usuarios', style: Theme.of(context).textTheme.titleLarge),
              const Spacer(),
              FilledButton.icon(
                onPressed: _abrirCrear,
                icon: const Icon(Icons.person_add_outlined),
                label: const Text('Nuevo usuario'),
              ),
              const SizedBox(width: 8),
              IconButton(
                tooltip: 'Actualizar',
                icon: const Icon(Icons.refresh),
                onPressed: _recargar,
              ),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _busqueda,
                  onSubmitted: (texto) => _aplicar(q: texto.trim()),
                  decoration: InputDecoration(
                    hintText: 'Buscar por username, nombre o correo',
                    prefixIcon: const Icon(Icons.search),
                    border: const OutlineInputBorder(),
                    suffixIcon: _busqueda.text.isEmpty
                        ? null
                        : IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              _busqueda.clear();
                              _aplicar(q: '');
                            },
                          ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              FilterChip(
                label: const Text('Solo activos'),
                selected: _soloActivos,
                onSelected: (valor) => _aplicar(soloActivos: valor),
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Expanded(
          child: FutureBuilder<Pagina<Usuario>>(
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
                      : 'No se pudieron cargar los usuarios.',
                  alReintentar: _recargar,
                );
              }
              final pagina = snapshot.data!;
              if (pagina.items.isEmpty) {
                return const EstadoVacio(
                  icono: Icons.manage_accounts_outlined,
                  mensaje: 'No hay usuarios.',
                );
              }
              final totalPaginas = _totalPaginas(pagina);
              return Column(
                children: [
                  Expanded(
                    child: ListView.separated(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      itemCount: pagina.items.length,
                      separatorBuilder: (_, _) => const SizedBox(height: 8),
                      itemBuilder: (context, indice) {
                        final usuario = pagina.items[indice];
                        return _FilaUsuario(
                          usuario: usuario,
                          alEditar: () => _abrirEditar(usuario),
                          alCambiarEstado: () => _cambiarEstado(usuario),
                          alEliminar: () => _eliminar(usuario),
                        );
                      },
                    ),
                  ),
                  BarraPaginacion(
                    etiqueta: 'Pagina $_pagina de $totalPaginas',
                    alAnterior: _pagina > 1
                        ? () => _aplicar(pagina: _pagina - 1)
                        : null,
                    alSiguiente: _pagina < totalPaginas
                        ? () => _aplicar(pagina: _pagina + 1)
                        : null,
                  ),
                ],
              );
            },
          ),
        ),
      ],
    );
  }

  int _totalPaginas(Pagina<Usuario> pagina) {
    final total = (pagina.total + _tamano - 1) ~/ _tamano;
    return total < 1 ? 1 : total;
  }
}

class _FilaUsuario extends StatelessWidget {
  const _FilaUsuario({
    required this.usuario,
    required this.alEditar,
    required this.alCambiarEstado,
    required this.alEliminar,
  });

  final Usuario usuario;
  final VoidCallback alEditar;
  final VoidCallback alCambiarEstado;
  final VoidCallback alEliminar;

  @override
  Widget build(BuildContext context) {
    return TarjetaHover(
      child: ListTile(
        leading: CircleAvatar(
          child: Text(
            usuario.username.isEmpty ? '?' : usuario.username[0].toUpperCase(),
          ),
        ),
        title: Text(usuario.username),
        subtitle: Text(
          '${usuario.nombre} · ${usuario.email} · '
          '${humanizar(usuario.role)}',
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            PastillaEstado(
              estado: usuario.activo ? 'ACTIVO' : 'INACTIVO',
              texto: usuario.activo ? 'ACTIVO' : 'INACTIVO',
            ),
            PopupMenuButton<String>(
              tooltip: 'Acciones',
              onSelected: (accion) {
                switch (accion) {
                  case 'estado':
                    alCambiarEstado();
                  case 'editar':
                    alEditar();
                  case 'eliminar':
                    alEliminar();
                }
              },
              itemBuilder: (context) => [
                PopupMenuItem(
                  value: 'estado',
                  child: Text(usuario.activo ? 'Desactivar' : 'Reactivar'),
                ),
                const PopupMenuItem(value: 'editar', child: Text('Editar')),
                const PopupMenuItem(value: 'eliminar', child: Text('Eliminar')),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _DialogoNuevoUsuario extends StatefulWidget {
  const _DialogoNuevoUsuario({required this.service, required this.catalogos});

  final UsuariosService service;
  final CatalogosService catalogos;

  @override
  State<_DialogoNuevoUsuario> createState() => _DialogoNuevoUsuarioState();
}

class _DialogoNuevoUsuarioState extends State<_DialogoNuevoUsuario> {
  final _formKey = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _email = TextEditingController();
  final _nombre = TextEditingController();
  final _password = TextEditingController();
  late String _role;
  bool _enviando = false;
  String? _error;

  static final _patronUsuario = RegExp(r'^[A-Za-z0-9._-]{3,64}$');

  @override
  void initState() {
    super.initState();
    final roles = widget.catalogos.valores('roles');
    _role = roles.isEmpty ? 'RECEPCION' : roles.first;
  }

  @override
  void dispose() {
    _username.dispose();
    _email.dispose();
    _nombre.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _guardar() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    setState(() {
      _enviando = true;
      _error = null;
    });
    try {
      await widget.service.crear(
        UsuarioCrear(
          username: _username.text.trim(),
          email: _email.text.trim(),
          nombre: _nombre.text.trim(),
          password: _password.text,
          role: _role,
        ),
      );
      if (mounted) Navigator.of(context).pop(true);
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.esValidacion && error.mensajesPorCampo.isNotEmpty
            ? error.mensajesPorCampo.values.first
            : error.mensaje;
        _enviando = false;
      });
    }
  }

  String? _validarContrasena(String? valor) {
    final texto = valor ?? '';
    if (texto.length < 8) return 'Minimo 8 caracteres';
    if (!RegExp(r'[A-Za-z]').hasMatch(texto)) return 'Debe incluir una letra';
    if (!RegExp(r'\d').hasMatch(texto)) return 'Debe incluir un numero';
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final roles = widget.catalogos.valores('roles');
    return AlertDialog(
      title: const Text('Nuevo usuario'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _username,
                decoration: const InputDecoration(labelText: 'Username'),
                validator: (valor) => _patronUsuario.hasMatch(valor ?? '')
                    ? null
                    : 'Letras, numeros, . _ - (3-64)',
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _email,
                decoration: const InputDecoration(labelText: 'Correo'),
                keyboardType: TextInputType.emailAddress,
                validator: (valor) =>
                    (valor == null || valor.trim().contains('@'))
                    ? null
                    : 'Correo invalido',
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _nombre,
                decoration: const InputDecoration(labelText: 'Nombre'),
                validator: (valor) => (valor == null || valor.trim().isEmpty)
                    ? 'Ingresa el nombre'
                    : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _password,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Contrasena',
                  helperText: 'Minimo 8 caracteres, letra y numero',
                ),
                validator: _validarContrasena,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _role,
                decoration: const InputDecoration(labelText: 'Rol'),
                items: [
                  for (final rol in roles)
                    DropdownMenuItem(value: rol, child: Text(rol)),
                ],
                onChanged: (valor) => setState(() => _role = valor ?? _role),
              ),
              if (_error != null) ...[
                const SizedBox(height: 8),
                Text(
                  _error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ],
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _enviando ? null : () => Navigator.of(context).pop(false),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _enviando ? null : _guardar,
          child: _enviando
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Guardar'),
        ),
      ],
    );
  }
}

class _DialogoEditarUsuario extends StatefulWidget {
  const _DialogoEditarUsuario({
    required this.service,
    required this.catalogos,
    required this.usuario,
  });

  final UsuariosService service;
  final CatalogosService catalogos;
  final Usuario usuario;

  @override
  State<_DialogoEditarUsuario> createState() => _DialogoEditarUsuarioState();
}

class _DialogoEditarUsuarioState extends State<_DialogoEditarUsuario> {
  late String _role;
  late bool _activo;
  bool _enviando = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _role = widget.usuario.role;
    _activo = widget.usuario.activo;
  }

  Future<void> _guardar() async {
    setState(() {
      _enviando = true;
      _error = null;
    });
    try {
      await widget.service.actualizar(
        widget.usuario.id,
        UsuarioActualizar(role: _role, activo: _activo),
      );
      if (mounted) Navigator.of(context).pop(true);
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.esValidacion && error.mensajesPorCampo.isNotEmpty
            ? error.mensajesPorCampo.values.first
            : error.mensaje;
        _enviando = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final roles = widget.catalogos.valores('roles');
    return AlertDialog(
      title: Text('Editar ${widget.usuario.username}'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          DropdownButtonFormField<String>(
            initialValue: _role,
            decoration: const InputDecoration(labelText: 'Rol'),
            items: [
              for (final rol in roles)
                DropdownMenuItem(value: rol, child: Text(rol)),
            ],
            onChanged: (valor) => setState(() => _role = valor ?? _role),
          ),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Activo'),
            value: _activo,
            onChanged: (valor) => setState(() => _activo = valor),
          ),
          if (_error != null)
            Text(
              _error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: _enviando ? null : () => Navigator.of(context).pop(false),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _enviando ? null : _guardar,
          child: _enviando
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Guardar'),
        ),
      ],
    );
  }
}
