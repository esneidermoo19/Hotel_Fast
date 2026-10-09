import 'package:flutter/material.dart';

import '../catalogos/catalogos_service.dart';
import '../core/network/api_exception.dart';
import '../shared/models/pagina.dart';
import '../shared/utils/fecha_hora.dart';
import '../widgets/aviso_error.dart';
import '../widgets/estado_vacio.dart';
import '../widgets/tarjeta_hover.dart';
import 'huespedes_service.dart';
import 'models/huesped.dart';

/// Vista del modulo de huespedes: listado paginado, busqueda, detalle y
/// formulario de registro/edicion.
class HuespedesView extends StatefulWidget {
  const HuespedesView({
    super.key,
    required this.service,
    required this.catalogos,
    this.esAdmin = false,
  });

  final HuespedesService service;
  final CatalogosService catalogos;

  /// `true` habilita registrar, editar y eliminar (solo ADMIN).
  final bool esAdmin;

  @override
  State<HuespedesView> createState() => _HuespedesViewState();
}

class _HuespedesViewState extends State<HuespedesView> {
  static const int _tamano = 20;

  final _busqueda = TextEditingController();
  String _q = '';
  int _pagina = 1;
  late Future<Pagina<Huesped>> _futuro;

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

  Future<Pagina<Huesped>> _consulta() {
    return widget.service.listar(
      pagina: _pagina,
      tamano: _tamano,
      q: _q.isEmpty ? null : _q,
    );
  }

  void _recargar() {
    setState(() {
      _futuro = _consulta();
    });
  }

  void _buscar(String texto) {
    _q = texto.trim();
    _pagina = 1;
    _recargar();
  }

  void _irPagina(int pagina) {
    _pagina = pagina;
    _recargar();
  }

  Future<void> _abrirFormulario([Huesped? huesped]) async {
    final guardado = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (_) => _DialogoHuesped(
        service: widget.service,
        catalogos: widget.catalogos,
        huesped: huesped,
      ),
    );
    if (guardado == true && mounted) _recargar();
  }

  void _mostrarDetalle(Huesped huesped) {
    showDialog<void>(
      context: context,
      builder: (_) => _DialogoDetalleHuesped(huesped: huesped),
    );
  }

  Future<void> _eliminar(Huesped huesped) async {
    final confirmado = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Eliminar huesped'),
        content: Text(
          'Se eliminara a ${huesped.nombreCompleto}. '
          'No se puede eliminar si tiene reservas.',
        ),
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
      await widget.service.eliminar(huesped.id);
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
              Text('Huespedes', style: Theme.of(context).textTheme.titleLarge),
              const Spacer(),
              if (widget.esAdmin) ...[
                FilledButton.icon(
                  onPressed: () => _abrirFormulario(),
                  icon: const Icon(Icons.person_add_outlined),
                  label: const Text('Nuevo huesped'),
                ),
                const SizedBox(width: 8),
              ],
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
          child: TextField(
            controller: _busqueda,
            onSubmitted: _buscar,
            decoration: InputDecoration(
              hintText: 'Buscar por nombre o documento',
              prefixIcon: const Icon(Icons.search),
              border: const OutlineInputBorder(),
              suffixIcon: _busqueda.text.isEmpty
                  ? null
                  : IconButton(
                      tooltip: 'Limpiar',
                      icon: const Icon(Icons.clear),
                      onPressed: () {
                        _busqueda.clear();
                        _buscar('');
                      },
                    ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Expanded(
          child: FutureBuilder<Pagina<Huesped>>(
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
                      : 'No se pudieron cargar los huespedes.',
                  alReintentar: _recargar,
                );
              }
              final pagina = snapshot.data!;
              if (pagina.items.isEmpty) {
                return const EstadoVacio(
                  icono: Icons.people_outline,
                  mensaje: 'No se encontraron huespedes.',
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
                        final huesped = pagina.items[indice];
                        return _FilaHuesped(
                          huesped: huesped,
                          esAdmin: widget.esAdmin,
                          alVer: () => _mostrarDetalle(huesped),
                          alEditar: () => _abrirFormulario(huesped),
                          alEliminar: () => _eliminar(huesped),
                        );
                      },
                    ),
                  ),
                  _BarraPaginacion(
                    etiqueta: 'Pagina $_pagina de $totalPaginas',
                    alAnterior: _pagina > 1
                        ? () => _irPagina(_pagina - 1)
                        : null,
                    alSiguiente: _pagina < totalPaginas
                        ? () => _irPagina(_pagina + 1)
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

  int _totalPaginas(Pagina<Huesped> pagina) {
    final total = (pagina.total + _tamano - 1) ~/ _tamano;
    return total < 1 ? 1 : total;
  }
}

class _FilaHuesped extends StatelessWidget {
  const _FilaHuesped({
    required this.huesped,
    required this.esAdmin,
    required this.alVer,
    required this.alEditar,
    required this.alEliminar,
  });

  final Huesped huesped;
  final bool esAdmin;
  final VoidCallback alVer;
  final VoidCallback alEditar;
  final VoidCallback alEliminar;

  String get _iniciales {
    final iniciales =
        '${huesped.nombres.isEmpty ? '' : huesped.nombres[0]}'
        '${huesped.apellidos.isEmpty ? '' : huesped.apellidos[0]}';
    return iniciales.isEmpty ? '?' : iniciales.toUpperCase();
  }

  @override
  Widget build(BuildContext context) {
    return TarjetaHover(
      onTap: alVer,
      child: ListTile(
        leading: CircleAvatar(child: Text(_iniciales)),
        title: Text(huesped.nombreCompleto),
        subtitle: Text(
          [
            huesped.documento,
            if (huesped.email != null) huesped.email!,
          ].join(' · '),
        ),
        isThreeLine: false,
        onTap: alVer,
        trailing: PopupMenuButton<String>(
          tooltip: 'Acciones',
          onSelected: (accion) {
            if (accion == 'ver') {
              alVer();
            } else if (accion == 'editar') {
              alEditar();
            } else if (accion == 'eliminar') {
              alEliminar();
            }
          },
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'ver', child: Text('Ver detalle')),
            if (esAdmin) ...[
              const PopupMenuItem(value: 'editar', child: Text('Editar')),
              const PopupMenuItem(value: 'eliminar', child: Text('Eliminar')),
            ],
          ],
        ),
      ),
    );
  }
}

class _BarraPaginacion extends StatelessWidget {
  const _BarraPaginacion({
    required this.etiqueta,
    required this.alAnterior,
    required this.alSiguiente,
  });

  final String etiqueta;
  final VoidCallback? alAnterior;
  final VoidCallback? alSiguiente;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          IconButton(
            tooltip: 'Pagina anterior',
            icon: const Icon(Icons.chevron_left),
            onPressed: alAnterior,
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Text(etiqueta),
          ),
          IconButton(
            tooltip: 'Pagina siguiente',
            icon: const Icon(Icons.chevron_right),
            onPressed: alSiguiente,
          ),
        ],
      ),
    );
  }
}

class _DialogoDetalleHuesped extends StatelessWidget {
  const _DialogoDetalleHuesped({required this.huesped});

  final Huesped huesped;

  @override
  Widget build(BuildContext context) {
    final filas = <(String, String?)>[
      ('Tipo de documento', huesped.tipoDocumento),
      ('Numero de documento', huesped.numeroDocumento),
      ('Nombres', huesped.nombres),
      ('Apellidos', huesped.apellidos),
      ('Correo', huesped.email),
      ('Telefono', huesped.telefono),
      ('Nacionalidad', huesped.nacionalidad),
      if (huesped.fechaNacimiento != null)
        ('Fecha de nacimiento', formatearFecha(huesped.fechaNacimiento!)),
      ('Direccion', huesped.direccion),
      ('Observaciones', huesped.observaciones),
    ];
    return AlertDialog(
      title: Text(huesped.nombreCompleto),
      content: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (final (etiqueta, valor) in filas)
              _FilaDetalle(etiqueta: etiqueta, valor: valor),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cerrar'),
        ),
      ],
    );
  }
}

class _FilaDetalle extends StatelessWidget {
  const _FilaDetalle({required this.etiqueta, required this.valor});

  final String etiqueta;
  final String? valor;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(etiqueta, style: Theme.of(context).textTheme.labelSmall),
          Text(valor ?? '—'),
        ],
      ),
    );
  }
}

class _DialogoHuesped extends StatefulWidget {
  const _DialogoHuesped({
    required this.service,
    required this.catalogos,
    this.huesped,
  });

  final HuespedesService service;
  final CatalogosService catalogos;
  final Huesped? huesped;

  @override
  State<_DialogoHuesped> createState() => _DialogoHuespedState();
}

class _DialogoHuespedState extends State<_DialogoHuesped> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _numeroDocumento;
  late final TextEditingController _nombres;
  late final TextEditingController _apellidos;
  late final TextEditingController _email;
  late final TextEditingController _telefono;
  late final TextEditingController _nacionalidad;
  late final TextEditingController _fechaNacimiento;
  late final TextEditingController _direccion;
  late final TextEditingController _observaciones;
  late String _tipoDocumento;
  bool _enviando = false;
  String? _error;

  bool get _esNuevo => widget.huesped == null;

  static final _patronDocumento = RegExp(r'^[A-Za-z0-9]{4,20}$');
  static final _patronTelefono = RegExp(r'^\+?\d{7,15}$');

  @override
  void initState() {
    super.initState();
    final tipos = widget.catalogos.valores('tipos_documento');
    final huesped = widget.huesped;
    _numeroDocumento = TextEditingController(text: huesped?.numeroDocumento);
    _nombres = TextEditingController(text: huesped?.nombres);
    _apellidos = TextEditingController(text: huesped?.apellidos);
    _email = TextEditingController(text: huesped?.email ?? '');
    _telefono = TextEditingController(text: huesped?.telefono ?? '');
    _nacionalidad = TextEditingController(text: huesped?.nacionalidad ?? '');
    _fechaNacimiento = TextEditingController(
      text: huesped?.fechaNacimiento == null
          ? ''
          : formatearFecha(huesped!.fechaNacimiento!),
    );
    _direccion = TextEditingController(text: huesped?.direccion ?? '');
    _observaciones = TextEditingController(text: huesped?.observaciones ?? '');
    _tipoDocumento =
        huesped?.tipoDocumento ?? (tipos.isEmpty ? '' : tipos.first);
  }

  @override
  void dispose() {
    _numeroDocumento.dispose();
    _nombres.dispose();
    _apellidos.dispose();
    _email.dispose();
    _telefono.dispose();
    _nacionalidad.dispose();
    _fechaNacimiento.dispose();
    _direccion.dispose();
    _observaciones.dispose();
    super.dispose();
  }

  Future<void> _guardar() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    setState(() {
      _enviando = true;
      _error = null;
    });
    final datos = HuespedPayload(
      tipoDocumento: _tipoDocumento,
      numeroDocumento: _numeroDocumento.text.trim(),
      nombres: _nombres.text.trim(),
      apellidos: _apellidos.text.trim(),
      email: _textoOpcional(_email),
      telefono: _textoOpcional(_telefono),
      nacionalidad: _textoOpcional(_nacionalidad),
      fechaNacimiento: _fechaNacimiento.text.trim().isEmpty
          ? null
          : leerFecha(_fechaNacimiento.text.trim()),
      direccion: _textoOpcional(_direccion),
      observaciones: _textoOpcional(_observaciones),
    );
    try {
      if (_esNuevo) {
        await widget.service.crear(datos);
      } else {
        await widget.service.actualizar(widget.huesped!.id, datos);
      }
      if (mounted) Navigator.of(context).pop(true);
    } on ApiException catch (error) {
      setState(() {
        _error = error.esValidacion && error.mensajesPorCampo.isNotEmpty
            ? error.mensajesPorCampo.values.first
            : error.mensaje;
        _enviando = false;
      });
    }
  }

  String? _textoOpcional(TextEditingController controlador) {
    final texto = controlador.text.trim();
    return texto.isEmpty ? null : texto;
  }

  @override
  Widget build(BuildContext context) {
    final tiposDocumento = widget.catalogos.valores('tipos_documento');
    return AlertDialog(
      title: Text(_esNuevo ? 'Nuevo huesped' : 'Editar huesped'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              DropdownButtonFormField<String>(
                initialValue: _tipoDocumento,
                decoration: const InputDecoration(
                  labelText: 'Tipo de documento',
                ),
                items: [
                  for (final tipo in tiposDocumento)
                    DropdownMenuItem(value: tipo, child: Text(tipo)),
                ],
                onChanged: (valor) =>
                    setState(() => _tipoDocumento = valor ?? _tipoDocumento),
                validator: (valor) => (valor == null || valor.isEmpty)
                    ? 'Selecciona el tipo'
                    : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _numeroDocumento,
                decoration: const InputDecoration(
                  labelText: 'Numero de documento',
                ),
                validator: (valor) => _patronDocumento.hasMatch(valor ?? '')
                    ? null
                    : 'De 4 a 20 caracteres alfanumericos',
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _nombres,
                decoration: const InputDecoration(labelText: 'Nombres'),
                validator: (valor) => (valor == null || valor.trim().isEmpty)
                    ? 'Ingresa los nombres'
                    : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _apellidos,
                decoration: const InputDecoration(labelText: 'Apellidos'),
                validator: (valor) => (valor == null || valor.trim().isEmpty)
                    ? 'Ingresa los apellidos'
                    : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _email,
                decoration: const InputDecoration(
                  labelText: 'Correo (opcional)',
                ),
                keyboardType: TextInputType.emailAddress,
                validator: (valor) {
                  final texto = (valor ?? '').trim();
                  if (texto.isEmpty || texto.contains('@')) return null;
                  return 'Ingresa un correo valido';
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _telefono,
                decoration: const InputDecoration(
                  labelText: 'Telefono (opcional)',
                ),
                keyboardType: TextInputType.phone,
                validator: (valor) {
                  final texto = (valor ?? '').trim();
                  if (texto.isEmpty || _patronTelefono.hasMatch(texto)) {
                    return null;
                  }
                  return 'Formato invalido (ej. +573001234567)';
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _nacionalidad,
                decoration: const InputDecoration(
                  labelText: 'Nacionalidad (opcional)',
                ),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _fechaNacimiento,
                decoration: const InputDecoration(
                  labelText: 'Fecha de nacimiento (opcional)',
                  hintText: 'AAAA-MM-DD',
                ),
                validator: (valor) {
                  final texto = (valor ?? '').trim();
                  if (texto.isEmpty) return null;
                  final fecha = DateTime.tryParse(texto);
                  if (fecha == null) return 'Formato AAAA-MM-DD';
                  if (fecha.isAfter(DateTime.now())) {
                    return 'No puede ser futura';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _direccion,
                decoration: const InputDecoration(
                  labelText: 'Direccion (opcional)',
                ),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _observaciones,
                decoration: const InputDecoration(
                  labelText: 'Observaciones (opcional)',
                ),
                maxLines: 2,
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
