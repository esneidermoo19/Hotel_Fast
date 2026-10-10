import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../catalogos/catalogos_service.dart';
import '../core/network/api_exception.dart';
import '../shared/utils/formato.dart';
import '../shared/utils/moneda.dart';
import '../theme/app_theme.dart';
import '../widgets/aviso_error.dart';
import '../widgets/esqueleto.dart';
import '../widgets/estado_vacio.dart';
import '../widgets/pastilla_estado.dart';
import '../widgets/tarjeta_hover.dart';
import 'habitaciones_service.dart';
import 'models/habitacion.dart';

/// Icono representativo por tipo de habitacion (para el placeholder).
IconData _iconoTipo(String tipo) => switch (tipo) {
  'SIMPLE' => Icons.single_bed_outlined,
  'DOBLE' => Icons.bed_outlined,
  'SUITE' => Icons.weekend_outlined,
  'PRESIDENCIAL' => Icons.king_bed_outlined,
  _ => Icons.meeting_room_outlined,
};

/// Imagen de red con carga, fade-in y placeholder ante errores.
class _ImagenHabitacion extends StatelessWidget {
  const _ImagenHabitacion({
    required this.url,
    this.icono = Icons.image_outlined,
    this.cacheWidth = 640,
  });

  final String url;
  final IconData icono;
  final int cacheWidth;

  @override
  Widget build(BuildContext context) {
    return Image.network(
      url,
      fit: BoxFit.cover,
      cacheWidth: cacheWidth,
      loadingBuilder: (context, child, progress) {
        if (progress == null) return child;
        return ColoredBox(
          color: AppTheme.midnightClaro.withValues(alpha: 0.25),
          child: const Center(child: CircularProgressIndicator(strokeWidth: 2)),
        );
      },
      errorBuilder: (_, _, _) => _PlaceholderImagen(icono: icono),
      frameBuilder: (context, child, frame, sincronizado) {
        if (sincronizado) return child;
        return AnimatedOpacity(
          opacity: frame == null ? 0 : 1,
          duration: const Duration(milliseconds: 350),
          curve: Curves.easeOut,
          child: child,
        );
      },
    );
  }
}

/// Placeholder elegante por tipo: degradado midnight/oro + icono.
class _PlaceholderImagen extends StatelessWidget {
  const _PlaceholderImagen({required this.icono});

  final IconData icono;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [AppTheme.midnight, AppTheme.oro],
        ),
      ),
      alignment: Alignment.center,
      child: Icon(
        icono,
        size: 48,
        color: AppTheme.oroClaro.withValues(alpha: 0.9),
      ),
    );
  }
}

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

  Future<void> _abrirDetalle(Habitacion habitacion) async {
    await showDialog<void>(
      context: context,
      builder: (_) => _DialogoDetalleHabitacion(
        habitacion: habitacion,
        resolverUrl: widget.service.resolverUrlMedia,
      ),
    );
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
        title: const Text('Eliminar habitación'),
        content: Text(
          'Se eliminará la habitación #${habitacion.numero}. '
          'Esta acción no se puede deshacer.',
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
                  label: const Text('Nueva habitación'),
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
                return const ListaEsqueleto();
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
                return const EstadoVacio(
                  icono: Icons.meeting_room_outlined,
                  mensaje: 'No hay habitaciones.',
                );
              }
              return GridView.builder(
                padding: const EdgeInsets.all(24),
                gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                  maxCrossAxisExtent: 360,
                  mainAxisSpacing: 16,
                  crossAxisSpacing: 16,
                  childAspectRatio: 0.78,
                ),
                itemCount: habitaciones.length,
                itemBuilder: (context, index) {
                  final habitacion = habitaciones[index];
                  return _TarjetaHabitacion(
                    habitacion: habitacion,
                    estados: estados,
                    esAdmin: widget.esAdmin,
                    resolverUrl: widget.service.resolverUrlMedia,
                    alCambiarEstado: (valor) =>
                        _cambiarEstado(habitacion, valor),
                    alCambiarLimpieza: (valor) =>
                        _cambiarLimpieza(habitacion, valor),
                    alEditar: () => _abrirFormulario(habitacion),
                    alEliminar: () => _eliminar(habitacion),
                    alAbrirDetalle: () => _abrirDetalle(habitacion),
                  );
                },
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
            label: Text(humanizar(opcion)),
            selected: actual == opcion,
            onSelected: (_) => alCambiar(opcion),
          ),
      ],
    );
  }
}

/// Portada de la tarjeta: imagen (o placeholder) con degradado, estado y numero.
class _PortadaHabitacion extends StatelessWidget {
  const _PortadaHabitacion({
    required this.habitacion,
    required this.resolverUrl,
  });

  final Habitacion habitacion;
  final String Function(String) resolverUrl;

  @override
  Widget build(BuildContext context) {
    final ruta = habitacion.imagenPrincipalUrl;
    final portada = (ruta != null && ruta.isNotEmpty)
        ? _ImagenHabitacion(
            url: resolverUrl(ruta),
            icono: _iconoTipo(habitacion.tipo),
          )
        : _PlaceholderImagen(icono: _iconoTipo(habitacion.tipo));

    return Stack(
      fit: StackFit.expand,
      children: [
        portada,
        const DecoratedBox(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [Colors.transparent, Color(0xCC0F172A)],
            ),
          ),
        ),
        Positioned(
          top: 8,
          left: 8,
          child: PastillaEstado(estado: habitacion.estado),
        ),
        Positioned(
          left: 12,
          bottom: 8,
          child: Text(
            '#${habitacion.numero}',
            style: Theme.of(context).textTheme.titleLarge
                ?.copyWith(color: Colors.white, fontWeight: FontWeight.w700),
          ),
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
    required this.resolverUrl,
    required this.alCambiarEstado,
    required this.alCambiarLimpieza,
    required this.alEditar,
    required this.alEliminar,
    required this.alAbrirDetalle,
  });

  final Habitacion habitacion;
  final List<String> estados;
  final bool esAdmin;
  final String Function(String) resolverUrl;
  final ValueChanged<String> alCambiarEstado;
  final ValueChanged<String> alCambiarLimpieza;
  final VoidCallback alEditar;
  final VoidCallback alEliminar;
  final VoidCallback alAbrirDetalle;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return TarjetaHover(
      onTap: alAbrirDetalle,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: alAbrirDetalle,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            AspectRatio(
              aspectRatio: 16 / 9,
              child: _PortadaHabitacion(
                habitacion: habitacion,
                resolverUrl: resolverUrl,
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            '${humanizar(habitacion.tipo)} · '
                            '${habitacion.capacidad} pers.',
                            style: tema.textTheme.bodyMedium,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        _menuAcciones(),
                      ],
                    ),
                    Text(
                      '${formatearMonto(habitacion.precioPorNoche)} / noche',
                      style: tema.textTheme.titleMedium?.copyWith(
                        color: AppTheme.oro,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    Row(
                      children: [
                        Icon(
                          Icons.cleaning_services_outlined,
                          size: 16,
                          color: tema.colorScheme.onSurfaceVariant,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          'Limpieza: ${humanizar(habitacion.limpieza)}',
                          style: tema.textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _menuAcciones() {
    return PopupMenuButton<String>(
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
            child: Text('Estado: ${humanizar(estado)}'),
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
          const PopupMenuItem(value: 'editar', child: Text('Editar')),
          const PopupMenuItem(value: 'eliminar', child: Text('Eliminar')),
        ],
      ],
    );
  }
}

/// Detalle con galeria (PageView + miniaturas + flechas) y datos completos.
class _DialogoDetalleHabitacion extends StatefulWidget {
  const _DialogoDetalleHabitacion({
    required this.habitacion,
    required this.resolverUrl,
  });

  final Habitacion habitacion;
  final String Function(String) resolverUrl;

  @override
  State<_DialogoDetalleHabitacion> createState() =>
      _DialogoDetalleHabitacionState();
}

class _DialogoDetalleHabitacionState extends State<_DialogoDetalleHabitacion> {
  final PageController _controlador = PageController();
  int _pagina = 0;

  List<HabitacionImagen> get _imagenes => widget.habitacion.imagenes;

  @override
  void dispose() {
    _controlador.dispose();
    super.dispose();
  }

  void _irA(int destino) {
    if (destino < 0 || destino >= _imagenes.length) return;
    _controlador.animateToPage(
      destino,
      duration: const Duration(milliseconds: 240),
      curve: Curves.easeOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    final habitacion = widget.habitacion;
    return Dialog(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (_imagenes.isEmpty)
                const SizedBox(
                  height: 220,
                  child: _PlaceholderImagen(icono: Icons.meeting_room_outlined),
                )
              else
                _galeria(),
              Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '#${habitacion.numero} · ${humanizar(habitacion.tipo)}',
                      style: tema.textTheme.titleLarge,
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        PastillaEstado(estado: habitacion.estado),
                        PastillaEstado(estado: habitacion.limpieza),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      '${formatearMonto(habitacion.precioPorNoche)} / noche',
                      style: tema.textTheme.titleMedium?.copyWith(
                        color: AppTheme.oro,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Capacidad: ${habitacion.capacidad} personas',
                      style: tema.textTheme.bodyMedium,
                    ),
                    if (habitacion.descripcion != null) ...[
                      const SizedBox(height: 8),
                      Text(
                        habitacion.descripcion!,
                        style: tema.textTheme.bodyMedium,
                      ),
                    ],
                    const SizedBox(height: 16),
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text('Cerrar'),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _galeria() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          height: 260,
          child: Stack(
            fit: StackFit.expand,
            children: [
              PageView.builder(
                controller: _controlador,
                itemCount: _imagenes.length,
                onPageChanged: (indice) => setState(() => _pagina = indice),
                itemBuilder: (_, indice) => _ImagenHabitacion(
                  url: widget.resolverUrl(_imagenes[indice].url),
                  icono: _iconoTipo(widget.habitacion.tipo),
                ),
              ),
              if (_imagenes.length > 1) ...[
                Positioned(
                  left: 8,
                  top: 0,
                  bottom: 0,
                  child: Center(child: _flecha(izquierda: true)),
                ),
                Positioned(
                  right: 8,
                  top: 0,
                  bottom: 0,
                  child: Center(child: _flecha(izquierda: false)),
                ),
              ],
            ],
          ),
        ),
        if (_imagenes.length > 1)
          SizedBox(
            height: 68,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.all(8),
              itemCount: _imagenes.length,
              separatorBuilder: (_, _) => const SizedBox(width: 8),
              itemBuilder: (_, indice) {
                final seleccionada = indice == _pagina;
                return GestureDetector(
                  onTap: () => _irA(indice),
                  child: Container(
                    width: 52,
                    height: 52,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8),
                      border: seleccionada
                          ? Border.all(color: AppTheme.oro, width: 2)
                          : Border.all(color: AppTheme.borde),
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: _ImagenHabitacion(
                      url: widget.resolverUrl(_imagenes[indice].url),
                      icono: _iconoTipo(widget.habitacion.tipo),
                      cacheWidth: 160,
                    ),
                  ),
                );
              },
            ),
          ),
      ],
    );
  }

  Widget _flecha({required bool izquierda}) {
    return IconButton.filled(
      style: IconButton.styleFrom(
        backgroundColor: AppTheme.midnight.withValues(alpha: 0.6),
        foregroundColor: Colors.white,
      ),
      onPressed: () => _irA(_pagina + (izquierda ? -1 : 1)),
      icon: Icon(izquierda ? Icons.chevron_left : Icons.chevron_right),
    );
  }
}

class _ArchivoPendiente {
  const _ArchivoPendiente({required this.nombre, required this.bytes});

  final String nombre;
  final Uint8List bytes;
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

  late final List<HabitacionImagen> _imagenes;
  final List<_ArchivoPendiente> _pendientes = [];
  int? _guardadoId;

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
    _imagenes = [...?widget.habitacion?.imagenes];
    _guardadoId = widget.habitacion?.id;
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
      final id =
          _guardadoId ??
          (_esNueva
              ? (await widget.service.crear(datos)).id
              : (await widget.service.actualizar(
                  widget.habitacion!.id,
                  datos,
                )).id);
      _guardadoId = id;
      await _subirPendientes(id);
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

  Future<void> _subirPendientes(int habitacionId) async {
    while (_pendientes.isNotEmpty) {
      final archivo = _pendientes.first;
      final subida = await widget.service.subirImagen(
        habitacionId,
        archivo.bytes,
        archivo.nombre,
      );
      _pendientes.removeAt(0);
      _imagenes.add(subida);
    }
  }

  Future<void> _agregarImagen() async {
    final archivo = await FilePicker.pickFile(
      type: FileType.custom,
      allowedExtensions: const ['jpg', 'jpeg', 'png', 'webp'],
    );
    if (archivo == null) return;
    final bytes = await archivo.readAsBytes();
    setState(() {
      _error = null;
      _pendientes.add(_ArchivoPendiente(nombre: archivo.name, bytes: bytes));
    });
  }

  Future<void> _marcarPrincipal(HabitacionImagen imagen) async {
    final id = _guardadoId;
    if (id == null) return;
    try {
      await widget.service.marcarPrincipal(id, imagen.id);
      setState(() {
        final actualizadas = [
          for (final item in _imagenes)
            item.copiarCon(esPrincipal: item.id == imagen.id),
        ];
        _imagenes
          ..clear()
          ..addAll(actualizadas);
      });
    } on ApiException catch (error) {
      setState(() => _error = error.mensaje);
    }
  }

  Future<void> _eliminarImagen(HabitacionImagen imagen) async {
    final confirmado = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Eliminar imagen'),
        content: const Text('Esta acción no se puede deshacer.'),
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
    final id = _guardadoId;
    if (id == null) return;
    try {
      await widget.service.eliminarImagen(id, imagen.id);
      setState(() => _imagenes.removeWhere((item) => item.id == imagen.id));
    } on ApiException catch (error) {
      setState(() => _error = error.mensaje);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(_esNueva ? 'Nueva habitación' : 'Editar habitación'),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _numero,
                decoration: const InputDecoration(labelText: 'Número'),
                keyboardType: TextInputType.number,
                validator: (valor) {
                  final numero = int.tryParse(valor ?? '');
                  return (numero == null || numero <= 0)
                      ? 'Ingresa un número válido'
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
                    DropdownMenuItem(value: tipo, child: Text(humanizar(tipo))),
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
                      ? 'Ingresa un precio válido'
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
                      child: Text(humanizar(estado)),
                    ),
                ],
                onChanged: (valor) =>
                    setState(() => _estado = valor ?? _estado),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _descripcion,
                decoration: const InputDecoration(labelText: 'Descripción'),
                maxLength: 300,
                buildCounter: (
                  _, {
                  required currentLength,
                  required isFocused,
                  maxLength,
                }) => null,
              ),
              const Divider(height: 24),
              _seccionImagenes(),
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

  Widget _seccionImagenes() {
    final tema = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text('Imágenes', style: tema.textTheme.titleSmall),
            const Spacer(),
            TextButton.icon(
              onPressed: _enviando ? null : _agregarImagen,
              icon: const Icon(Icons.add_photo_alternate_outlined),
              label: const Text('Subir imagen'),
            ),
          ],
        ),
        if (_imagenes.isEmpty && _pendientes.isEmpty)
          Text(
            'Sin imágenes.',
            style: tema.textTheme.bodySmall?.copyWith(
              color: tema.colorScheme.onSurfaceVariant,
            ),
          ),
        if (_imagenes.isNotEmpty || _pendientes.isNotEmpty)
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final imagen in _imagenes) _miniaturaExistente(imagen),
              for (final pendiente in _pendientes)
                _miniaturaPendiente(pendiente),
            ],
          ),
      ],
    );
  }

  Widget _miniaturaExistente(HabitacionImagen imagen) {
    return SizedBox(
      width: 84,
      height: 84,
      child: Stack(
        fit: StackFit.expand,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: _ImagenHabitacion(
              url: widget.service.resolverUrlMedia(imagen.url),
              cacheWidth: 160,
            ),
          ),
          if (imagen.esPrincipal)
            Positioned(
              left: 4,
              bottom: 4,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: AppTheme.oro,
                  borderRadius: BorderRadius.circular(999),
                ),
                child: const Text(
                  'Principal',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.midnight,
                  ),
                ),
              ),
            ),
          Positioned(right: 2, top: 2, child: _menuImagen(imagen)),
        ],
      ),
    );
  }

  Widget _miniaturaPendiente(_ArchivoPendiente pendiente) {
    return SizedBox(
      width: 84,
      height: 84,
      child: Stack(
        fit: StackFit.expand,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.memory(pendiente.bytes, fit: BoxFit.cover),
          ),
          Positioned(
            right: 2,
            top: 2,
            child: IconButton(
              tooltip: 'Quitar',
              icon: const Icon(Icons.close, size: 18),
              onPressed: () => setState(() => _pendientes.remove(pendiente)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _menuImagen(HabitacionImagen imagen) {
    return PopupMenuButton<String>(
      icon: const Icon(Icons.more_vert, size: 18),
      tooltip: 'Acciones de la imagen',
      onSelected: (accion) {
        if (accion == 'principal') _marcarPrincipal(imagen);
        if (accion == 'eliminar') _eliminarImagen(imagen);
      },
      itemBuilder: (_) => [
        if (!imagen.esPrincipal)
          const PopupMenuItem(
            value: 'principal',
            child: Text('Marcar principal'),
          ),
        const PopupMenuItem(value: 'eliminar', child: Text('Eliminar')),
      ],
    );
  }
}
