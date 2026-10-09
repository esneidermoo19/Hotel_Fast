import 'package:flutter/material.dart';

import '../catalogos/catalogos_service.dart';
import '../core/network/api_exception.dart';
import '../shared/utils/moneda.dart';
import '../widgets/aviso_error.dart';
import 'habitaciones_service.dart';
import 'models/habitacion.dart';

/// Vista del modulo de habitaciones: listado, filtros, acciones rapidas y
/// formulario de creacion/edicion.
class HabitacionesView extends StatefulWidget {
  const HabitacionesView({
    super.key,
    required this.service,
    required this.catalogos,
    this.esAdmin = false,
  });

  final HabitacionesService service;
  final CatalogosService catalogos;

  /// `true` habilita crear, editar y eliminar (solo ADMIN).
  final bool esAdmin;

  @override
  State<HabitacionesView> createState() => _HabitacionesViewState();
}

class _HabitacionesViewState extends State<HabitacionesView> {
  String? _estado;
  String? _tipo;
  late Future<List<Habitacion>> _futuro;

  @override
  void initState() {
    super.initState();
    _futuro = widget.service.listar();
  }

  Future<List<Habitacion>> _listarFiltrado() {
    return widget.service.listar(estado: _estado, tipo: _tipo);
  }

  void _aplicarFiltros({String? estado, String? tipo}) {
    setState(() {
      _estado = estado;
      _tipo = tipo;
      _futuro = _listarFiltrado();
    });
  }

  void _recargar() => _aplicarFiltros(estado: _estado, tipo: _tipo);

  Future<void> _abrirFormulario([Habitacion? habitacion]) async {
    final guardado = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (_) => _DialogoHabitacion(
        service: widget.service,
        catalogos: widget.catalogos,
        habitacion: habitacion,
      ),
    );
    if (guardado == true && mounted) _recargar();
  }

  Future<void> _cambiarEstado(Habitacion habitacion, String estado) async {
    try {
      await widget.service.cambiarEstado(habitacion.id, estado);
      if (mounted) _recargar();
    } on ApiException catch (error) {
      _mostrarError(error);
    }
  }

  Future<void> _cambiarLimpieza(Habitacion habitacion, String limpieza) async {
    try {
      await widget.service.cambiarLimpieza(habitacion.id, limpieza);
      if (mounted) _recargar();
    } on ApiException catch (error) {
      _mostrarError(error);
    }
  }

  Future<void> _eliminar(Habitacion habitacion) async {
    final confirmado = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Eliminar habitacion'),
        content: Text(
          'Se eliminara la habitacion #${habitacion.numero}. '
          'Esta accion no se puede deshacer.',
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
      await widget.service.eliminar(habitacion.id);
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
    final estados = widget.catalogos.valores('estados_habitacion');
    final tipos = widget.catalogos.valores('tipos_habitacion');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 8),
          child: Row(
            children: [
              Text(
                'Habitaciones',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const Spacer(),
              if (widget.esAdmin) ...[
                FilledButton.icon(
                  onPressed: () => _abrirFormulario(),
                  icon: const Icon(Icons.add),
                  label: const Text('Nueva habitacion'),
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
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _grupoFiltros(
                titulo: 'Estado',
                opciones: estados,
                actual: _estado,
                alCambiar: (valor) =>
                    _aplicarFiltros(estado: valor, tipo: _tipo),
              ),
              const SizedBox(height: 8),
              _grupoFiltros(
                titulo: 'Tipo',
                opciones: tipos,
                actual: _tipo,
                alCambiar: (valor) =>
                    _aplicarFiltros(estado: _estado, tipo: valor),
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Expanded(
          child: FutureBuilder<List<Habitacion>>(
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
                      : 'No se pudieron cargar las habitaciones.',
                  alReintentar: _recargar,
                );
              }
              final habitaciones = snapshot.data ?? const [];
              if (habitaciones.isEmpty) {
                return const Center(child: Text('No hay habitaciones.'));
              }
              return SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Wrap(
                  spacing: 16,
                  runSpacing: 16,
                  children: [
                    for (final habitacion in habitaciones)
                      SizedBox(
                        width: 320,
                        child: _TarjetaHabitacion(
                          habitacion: habitacion,
                          estados: estados,
                          esAdmin: widget.esAdmin,
                          alCambiarEstado: (valor) =>
                              _cambiarEstado(habitacion, valor),
                          alCambiarLimpieza: (valor) =>
                              _cambiarLimpieza(habitacion, valor),
                          alEditar: () => _abrirFormulario(habitacion),
                          alEliminar: () => _eliminar(habitacion),
                        ),
                      ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _grupoFiltros({
    required String titulo,
    required List<String> opciones,
    required String? actual,
    required ValueChanged<String?> alCambiar,
  }) {
    return Wrap(
      spacing: 8,
      runSpacing: 4,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        Text('$titulo:', style: Theme.of(context).textTheme.labelLarge),
        ChoiceChip(
          label: const Text('Todos'),
          selected: actual == null,
          onSelected: (_) => alCambiar(null),
        ),
        for (final opcion in opciones)
          ChoiceChip(
            label: Text(_humanizar(opcion)),
            selected: actual == opcion,
            onSelected: (_) => alCambiar(opcion),
          ),
      ],
    );
  }
}

class _TarjetaHabitacion extends StatelessWidget {
  const _TarjetaHabitacion({
    required this.habitacion,
    required this.estados,
    required this.esAdmin,
    required this.alCambiarEstado,
    required this.alCambiarLimpieza,
    required this.alEditar,
    required this.alEliminar,
  });

  final Habitacion habitacion;
  final List<String> estados;
  final bool esAdmin;
  final ValueChanged<String> alCambiarEstado;
  final ValueChanged<String> alCambiarLimpieza;
  final VoidCallback alEditar;
  final VoidCallback alEliminar;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    '#${habitacion.numero}',
                    style: tema.textTheme.headlineMedium,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                _EtiquetaEstado(estado: habitacion.estado),
                PopupMenuButton<String>(
                  tooltip: 'Acciones',
                  onSelected: (accion) {
                    if (accion.startsWith('estado:')) {
                      alCambiarEstado(accion.substring('estado:'.length));
                    } else if (accion.startsWith('limpieza:')) {
                      alCambiarLimpieza(accion.substring('limpieza:'.length));
                    } else if (accion == 'editar') {
                      alEditar();
                    } else if (accion == 'eliminar') {
                      alEliminar();
                    }
                  },
                  itemBuilder: (context) => [
                    for (final estado in estados)
                      PopupMenuItem(
                        value: 'estado:$estado',
                        child: Text('Estado: ${_humanizar(estado)}'),
                      ),
                    const PopupMenuDivider(),
                    PopupMenuItem(
                      value: 'limpieza:LIMPIA',
                      child: const Text('Marcar limpia'),
                    ),
                    PopupMenuItem(
                      value: 'limpieza:SUCIA',
                      child: const Text('Marcar sucia'),
                    ),
                    if (esAdmin) ...[
                      const PopupMenuDivider(),
                      const PopupMenuItem(
                        value: 'editar',
                        child: Text('Editar'),
                      ),
                      const PopupMenuItem(
                        value: 'eliminar',
                        child: Text('Eliminar'),
                      ),
                    ],
                  ],
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              '${_humanizar(habitacion.tipo)} · Capacidad: '
              '${habitacion.capacidad}',
              style: tema.textTheme.bodyMedium,
            ),
            const SizedBox(height: 4),
            Text(
              '${formatearMonto(habitacion.precioPorNoche)} / noche',
              style: tema.textTheme.bodyMedium,
            ),
            const SizedBox(height: 4),
            Text(
              'Limpieza: ${_humanizar(habitacion.limpieza)}',
              style: tema.textTheme.bodySmall,
            ),
            if (habitacion.descripcion != null) ...[
              const SizedBox(height: 4),
              Text(habitacion.descripcion!, style: tema.textTheme.bodySmall),
            ],
          ],
        ),
      ),
    );
  }
}

class _EtiquetaEstado extends StatelessWidget {
  const _EtiquetaEstado({required this.estado});

  final String estado;

  Color _color() {
    return switch (estado) {
      'DISPONIBLE' => const Color(0xFF2E7D32),
      'OCUPADA' => const Color(0xFFE64A19),
      _ => const Color(0xFF546E7A),
    };
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: _color(),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        _humanizar(estado),
        style: const TextStyle(color: Colors.white, fontSize: 12),
      ),
    );
  }
}

class _DialogoHabitacion extends StatefulWidget {
  const _DialogoHabitacion({
    required this.service,
    required this.catalogos,
    this.habitacion,
  });

  final HabitacionesService service;
  final CatalogosService catalogos;
  final Habitacion? habitacion;

  @override
  State<_DialogoHabitacion> createState() => _DialogoHabitacionState();
}

class _DialogoHabitacionState extends State<_DialogoHabitacion> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _numero;
  late final TextEditingController _capacidad;
  late final TextEditingController _precio;
  late final TextEditingController _descripcion;
  late String _tipo;
  late String _estado;
  bool _enviando = false;
  String? _error;

  bool get _esNueva => widget.habitacion == null;

  @override
  void initState() {
    super.initState();
    final tipos = widget.catalogos.valores('tipos_habitacion');
    _numero = TextEditingController(text: widget.habitacion?.numero.toString());
    _capacidad = TextEditingController(
      text: widget.habitacion?.capacidad.toString(),
    );
    _precio = TextEditingController(
      text: widget.habitacion?.precioPorNoche.toString(),
    );
    _descripcion = TextEditingController(
      text: widget.habitacion?.descripcion ?? '',
    );
    _tipo = widget.habitacion?.tipo ?? (tipos.isEmpty ? '' : tipos.first);
    _estado = widget.habitacion?.estado ?? 'DISPONIBLE';
  }

  @override
  void dispose() {
    _numero.dispose();
    _capacidad.dispose();
    _precio.dispose();
    _descripcion.dispose();
    super.dispose();
  }

  Future<void> _guardar() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    setState(() {
      _enviando = true;
      _error = null;
    });
    final datos = HabitacionPayload(
      numero: int.parse(_numero.text.trim()),
      tipo: _tipo,
      capacidad: int.parse(_capacidad.text.trim()),
      precioPorNoche: double.parse(_precio.text.trim()),
      estado: _estado,
      descripcion: _descripcion.text.trim().isEmpty
          ? null
          : _descripcion.text.trim(),
    );
    try {
      if (_esNueva) {
        await widget.service.crear(datos);
      } else {
        await widget.service.actualizar(widget.habitacion!.id, datos);
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

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(_esNueva ? 'Nueva habitacion' : 'Editar habitacion'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _numero,
                decoration: const InputDecoration(labelText: 'Numero'),
                keyboardType: TextInputType.number,
                validator: (valor) {
                  final numero = int.tryParse(valor ?? '');
                  return (numero == null || numero <= 0)
                      ? 'Ingresa un numero valido'
                      : null;
                },
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _tipo,
                decoration: const InputDecoration(labelText: 'Tipo'),
                items: [
                  for (final tipo in widget.catalogos.valores(
                    'tipos_habitacion',
                  ))
                    DropdownMenuItem(
                      value: tipo,
                      child: Text(_humanizar(tipo)),
                    ),
                ],
                onChanged: (valor) => setState(() => _tipo = valor ?? _tipo),
                validator: (valor) => (valor == null || valor.isEmpty)
                    ? 'Selecciona el tipo'
                    : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _capacidad,
                decoration: const InputDecoration(labelText: 'Capacidad'),
                keyboardType: TextInputType.number,
                validator: (valor) {
                  final numero = int.tryParse(valor ?? '');
                  return (numero == null || numero < 1)
                      ? 'La capacidad debe ser al menos 1'
                      : null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _precio,
                decoration: const InputDecoration(
                  labelText: 'Precio por noche (COP)',
                ),
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                validator: (valor) {
                  final numero = double.tryParse(valor ?? '');
                  return (numero == null || numero <= 0)
                      ? 'Ingresa un precio valido'
                      : null;
                },
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: _estado,
                decoration: const InputDecoration(labelText: 'Estado'),
                items: [
                  for (final estado in widget.catalogos.valores(
                    'estados_habitacion',
                  ))
                    DropdownMenuItem(
                      value: estado,
                      child: Text(_humanizar(estado)),
                    ),
                ],
                onChanged: (valor) =>
                    setState(() => _estado = valor ?? _estado),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _descripcion,
                decoration: const InputDecoration(labelText: 'Descripcion'),
                maxLength: 300,
                buildCounter: (
                  _, {
                  required currentLength,
                  required isFocused,
                  maxLength,
                }) => null,
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

String _humanizar(String valor) {
  return valor
      .split('_')
      .map(
        (parte) =>
            parte.isEmpty ? parte : parte[0] + parte.substring(1).toLowerCase(),
      )
      .join(' ');
}
