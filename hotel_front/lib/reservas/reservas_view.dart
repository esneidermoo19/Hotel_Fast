import 'package:flutter/material.dart';

import '../catalogos/catalogos_service.dart';
import '../core/network/api_exception.dart';
import '../huespedes/huespedes_service.dart';
import '../huespedes/models/huesped.dart';
import '../shared/models/pagina.dart';
import '../shared/utils/fecha_hora.dart';
import '../shared/utils/formato.dart';
import '../shared/utils/moneda.dart';
import '../widgets/aviso_error.dart';
import '../widgets/barra_paginacion.dart';
import 'models/reserva.dart';
import 'reservas_service.dart';

/// Vista del modulo de reservas: listado con filtros, nueva reserva con
/// disponibilidad y detalle con acciones de ciclo de vida.
class ReservasView extends StatefulWidget {
  const ReservasView({
    super.key,
    required this.service,
    required this.catalogos,
    required this.huespedes,
  });

  final ReservasService service;
  final CatalogosService catalogos;
  final HuespedesService huespedes;

  @override
  State<ReservasView> createState() => _ReservasViewState();
}

class _ReservasViewState extends State<ReservasView> {
  static const int _tamano = 20;

  String? _estado;
  DateTime? _desde;
  DateTime? _hasta;
  int _pagina = 1;
  late Future<Pagina<Reserva>> _futuro;

  @override
  void initState() {
    super.initState();
    _futuro = _consulta();
  }

  Future<Pagina<Reserva>> _consulta() {
    return widget.service.listar(
      pagina: _pagina,
      tamano: _tamano,
      estado: _estado,
      desde: _desde,
      hasta: _hasta,
    );
  }

  void _aplicar({
    String? estado,
    DateTime? desde,
    DateTime? hasta,
    int? pagina,
  }) {
    setState(() {
      _estado = estado ?? _estado;
      _desde = desde;
      _hasta = hasta;
      _pagina = pagina ?? 1;
      _futuro = _consulta();
    });
  }

  void _recargar() => _aplicar(pagina: _pagina);

  Future<void> _abrirNueva() async {
    final creada = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (_) => _DialogoNuevaReserva(
        service: widget.service,
        catalogos: widget.catalogos,
        huespedes: widget.huespedes,
      ),
    );
    if (creada == true && mounted) _recargar();
  }

  Future<void> _abrirDetalle(Reserva reserva) async {
    await showDialog<void>(
      context: context,
      builder: (_) =>
          _DialogoDetalleReserva(reserva: reserva, service: widget.service),
    );
    if (mounted) _recargar();
  }

  @override
  Widget build(BuildContext context) {
    final estados = widget.catalogos.valores('estados_reserva');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 8),
          child: Row(
            children: [
              Text('Reservas', style: Theme.of(context).textTheme.titleLarge),
              const Spacer(),
              FilledButton.icon(
                onPressed: _abrirNueva,
                icon: const Icon(Icons.add),
                label: const Text('Nueva reserva'),
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
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Text('Estado:', style: Theme.of(context).textTheme.labelLarge),
              ChoiceChip(
                label: const Text('Todos'),
                selected: _estado == null,
                onSelected: (_) => _aplicar(estado: null),
              ),
              for (final estado in estados)
                ChoiceChip(
                  label: Text(humanizar(estado)),
                  selected: _estado == estado,
                  onSelected: (_) => _aplicar(estado: estado),
                ),
              _SelectorFecha(
                etiqueta: 'Desde',
                fecha: _desde,
                alElegir: (fecha) => _aplicar(desde: fecha, hasta: _hasta),
                alLimpiar: _desde == null
                    ? null
                    : () => _aplicar(desde: null, hasta: _hasta),
              ),
              _SelectorFecha(
                etiqueta: 'Hasta',
                fecha: _hasta,
                alElegir: (fecha) => _aplicar(desde: _desde, hasta: fecha),
                alLimpiar: _hasta == null
                    ? null
                    : () => _aplicar(desde: _desde, hasta: null),
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Expanded(
          child: FutureBuilder<Pagina<Reserva>>(
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
                      : 'No se pudieron cargar las reservas.',
                  alReintentar: _recargar,
                );
              }
              final pagina = snapshot.data!;
              if (pagina.items.isEmpty) {
                return const Center(child: Text('No hay reservas.'));
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
                        final reserva = pagina.items[indice];
                        return _FilaReserva(
                          reserva: reserva,
                          alAbrir: () => _abrirDetalle(reserva),
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

  int _totalPaginas(Pagina<Reserva> pagina) {
    final total = (pagina.total + _tamano - 1) ~/ _tamano;
    return total < 1 ? 1 : total;
  }
}

class _SelectorFecha extends StatelessWidget {
  const _SelectorFecha({
    required this.etiqueta,
    required this.fecha,
    required this.alElegir,
    this.alLimpiar,
  });

  final String etiqueta;
  final DateTime? fecha;
  final ValueChanged<DateTime> alElegir;
  final VoidCallback? alLimpiar;

  @override
  Widget build(BuildContext context) {
    final texto = fecha == null
        ? '$etiqueta: -'
        : '$etiqueta: ${formatearFecha(fecha!)}';
    return InputChip(
      avatar: const Icon(Icons.calendar_today_outlined, size: 18),
      label: Text(texto),
      onPressed: () async {
        final elegida = await showDatePicker(
          context: context,
          initialDate: fecha ?? DateTime.now(),
          firstDate: DateTime(2000),
          lastDate: DateTime(2100),
        );
        if (elegida != null) alElegir(elegida);
      },
      onDeleted: alLimpiar,
    );
  }
}

class _FilaReserva extends StatelessWidget {
  const _FilaReserva({required this.reserva, required this.alAbrir});

  final Reserva reserva;
  final VoidCallback alAbrir;

  @override
  Widget build(BuildContext context) {
    final tema = Theme.of(context);
    return Card(
      child: ListTile(
        onTap: alAbrir,
        title: Row(
          children: [
            Text(reserva.codigo, style: tema.textTheme.titleMedium),
            const SizedBox(width: 8),
            _EtiquetaEstado(estado: reserva.estado),
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(reserva.huesped.nombreCompleto),
            Text(
              'Hab. ${reserva.habitacion.numero} · '
              '${formatearFecha(reserva.fechaEntrada)} → '
              '${formatearFecha(reserva.fechaSalida)}',
            ),
            Text(
              '${reserva.numeroHuespedes} huesped(es) · '
              '${formatearMonto(reserva.totalEstimado)}',
            ),
          ],
        ),
        trailing: const Icon(Icons.chevron_right),
      ),
    );
  }
}

class _EtiquetaEstado extends StatelessWidget {
  const _EtiquetaEstado({required this.estado});

  final String estado;

  Color _color() {
    return switch (estado) {
      'PENDIENTE' => const Color(0xFF546E7A),
      'CONFIRMADA' => const Color(0xFF1565C0),
      'CHECK_IN' => const Color(0xFF2E7D32),
      'CHECK_OUT' => const Color(0xFF00695C),
      'CANCELADA' => const Color(0xFFC62828),
      'NO_SHOW' => const Color(0xFFE65100),
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
        humanizar(estado),
        style: const TextStyle(color: Colors.white, fontSize: 12),
      ),
    );
  }
}

class _DialogoDetalleReserva extends StatefulWidget {
  const _DialogoDetalleReserva({required this.reserva, required this.service});

  final Reserva reserva;
  final ReservasService service;

  @override
  State<_DialogoDetalleReserva> createState() => _DialogoDetalleReservaState();
}

class _DialogoDetalleReservaState extends State<_DialogoDetalleReserva> {
  late Reserva _reserva;
  bool _enviando = false;

  @override
  void initState() {
    super.initState();
    _reserva = widget.reserva;
  }

  void _aviso(String mensaje) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(mensaje)));
  }

  Future<void> _ejecutar(Future<Reserva> Function() accion) async {
    setState(() => _enviando = true);
    try {
      final actualizada = await accion();
      if (!mounted) return;
      setState(() {
        _reserva = actualizada;
        _enviando = false;
      });
      _aviso('Reserva actualizada: ${humanizar(actualizada.estado)}');
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() => _enviando = false);
      _aviso(error.mensaje);
    }
  }

  Future<void> _confirmar() =>
      _ejecutar(() => widget.service.confirmar(_reserva.id));

  Future<void> _noShow() async {
    final ok = await _preguntar(
      'Marcar No-show',
      'Se marcara la reserva como no asistida.',
    );
    if (ok == true) {
      await _ejecutar(() => widget.service.marcarNoShow(_reserva.id));
    }
  }

  Future<void> _checkIn() async {
    final ok = await _preguntar(
      'Registrar check-in',
      'Se confirmara el ingreso del huesped.',
    );
    if (ok == true) await _ejecutar(() => widget.service.checkIn(_reserva.id));
  }

  Future<void> _cancelar() async {
    final motivo = await _pedirMotivo();
    if (motivo == null) return;
    await _ejecutar(() => widget.service.cancelar(_reserva.id, motivo));
  }

  Future<void> _checkOut() async {
    final ok = await _preguntar(
      'Registrar check-out',
      'Se finalizara la estancia del huesped.',
    );
    if (ok != true) return;
    setState(() => _enviando = true);
    try {
      final resultado = await widget.service.checkOut(_reserva.id);
      if (!mounted) return;
      setState(() {
        _reserva = resultado.reserva;
        _enviando = false;
      });
      await _mostrarResultadoCheckOut(resultado);
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() => _enviando = false);
      _aviso(error.mensaje);
    }
  }

  Future<void> _extender() async {
    final elegida = await showDatePicker(
      context: context,
      initialDate: _reserva.fechaSalida,
      firstDate: _reserva.fechaEntrada,
      lastDate: DateTime(2100),
    );
    if (elegida == null) return;
    await _ejecutar(() => widget.service.extender(_reserva.id, elegida));
  }

  Future<bool?> _preguntar(String titulo, String contenido) {
    return showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(titulo),
        content: Text(contenido),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Continuar'),
          ),
        ],
      ),
    );
  }

  Future<String?> _pedirMotivo() {
    final controlador = TextEditingController();
    return showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancelar reserva'),
        content: TextField(
          controller: controlador,
          maxLines: 2,
          autofocus: true,
          decoration: const InputDecoration(
            labelText: 'Motivo (minimo 3 caracteres)',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () {
              final motivo = controlador.text.trim();
              if (motivo.length < 3) return;
              Navigator.of(context).pop(motivo);
            },
            child: const Text('Confirmar'),
          ),
        ],
      ),
    );
  }

  Future<void> _mostrarResultadoCheckOut(ReservaCheckOut resultado) {
    return showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Check-out completado'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _FilaEconomica('Total cuenta', resultado.totalCuenta),
            _FilaEconomica('Total pagado', resultado.totalPagado),
            _FilaEconomica('Saldo pendiente', resultado.saldoPendiente),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Aceptar'),
          ),
        ],
      ),
    );
  }

  List<(String, String)> get _datos {
    return [
      ('Codigo', _reserva.codigo),
      ('Huesped', _reserva.huesped.nombreCompleto),
      ('Habitacion', '#${_reserva.habitacion.numero}'),
      ('Check-in', formatearFecha(_reserva.fechaEntrada)),
      ('Check-out', formatearFecha(_reserva.fechaSalida)),
      ('Huespedes', '${_reserva.numeroHuespedes}'),
      ('Estado', humanizar(_reserva.estado)),
      ('Precio noche', formatearMonto(_reserva.precioNocheAplicado)),
      ('Total estimado', formatearMonto(_reserva.totalEstimado)),
      if (_reserva.observaciones != null)
        ('Observaciones', _reserva.observaciones!),
      if (_reserva.motivoCancelacion != null)
        ('Motivo cancelacion', _reserva.motivoCancelacion!),
    ];
  }

  List<(String, VoidCallback)> get _acciones {
    return switch (_reserva.estado) {
      'PENDIENTE' => [('Confirmar', _confirmar), ('Cancelar', _cancelar)],
      'CONFIRMADA' => [
        ('Check-in', _checkIn),
        ('No-show', _noShow),
        ('Cancelar', _cancelar),
      ],
      'CHECK_IN' => [('Check-out', _checkOut), ('Extender', _extender)],
      _ => const <(String, VoidCallback)>[],
    };
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(_reserva.codigo),
      content: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (final (etiqueta, valor) in _datos)
              _FilaDetalle(etiqueta: etiqueta, valor: valor),
            const SizedBox(height: 12),
            if (_acciones.isNotEmpty)
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final (etiqueta, accion) in _acciones)
                    FilledButton.tonal(
                      onPressed: _enviando ? null : accion,
                      child: Text(etiqueta),
                    ),
                ],
              ),
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

class _FilaEconomica extends StatelessWidget {
  const _FilaEconomica(this.etiqueta, this.monto);

  final String etiqueta;
  final double monto;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [Text(etiqueta), Text(formatearMonto(monto))],
      ),
    );
  }
}

class _FilaDetalle extends StatelessWidget {
  const _FilaDetalle({required this.etiqueta, required this.valor});

  final String etiqueta;
  final String valor;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(etiqueta, style: Theme.of(context).textTheme.labelSmall),
          Text(valor),
        ],
      ),
    );
  }
}

class _DialogoNuevaReserva extends StatefulWidget {
  const _DialogoNuevaReserva({
    required this.service,
    required this.catalogos,
    required this.huespedes,
  });

  final ReservasService service;
  final CatalogosService catalogos;
  final HuespedesService huespedes;

  @override
  State<_DialogoNuevaReserva> createState() => _DialogoNuevaReservaState();
}

class _DialogoNuevaReservaState extends State<_DialogoNuevaReserva> {
  final _busquedaHuesped = TextEditingController();
  final _numeroHuespedes = TextEditingController(text: '1');

  DateTime? _entrada;
  DateTime? _salida;
  Huesped? _huesped;
  List<Huesped>? _resultados;
  bool _buscandoHuesped = false;
  List<ReservaHabitacion>? _disponibles;
  bool _consultando = false;
  ReservaHabitacion? _habitacion;
  bool _creando = false;
  String? _error;

  @override
  void dispose() {
    _busquedaHuesped.dispose();
    _numeroHuespedes.dispose();
    super.dispose();
  }

  Future<void> _elegirFecha(bool esEntrada) async {
    final inicial = esEntrada
        ? _entrada
        : (_salida ?? _entrada ?? DateTime.now());
    final elegida = await showDatePicker(
      context: context,
      initialDate: inicial ?? DateTime.now(),
      firstDate: esEntrada ? DateTime(2000) : (_entrada ?? DateTime(2000)),
      lastDate: DateTime(2100),
    );
    if (elegida == null) return;
    setState(() {
      if (esEntrada) {
        _entrada = elegida;
        if (_salida != null && !_salida!.isAfter(_entrada!)) _salida = null;
      } else {
        _salida = elegida;
      }
      _disponibles = null;
      _habitacion = null;
    });
  }

  Future<void> _buscarHuesped() async {
    final texto = _busquedaHuesped.text.trim();
    if (texto.isEmpty) return;
    setState(() {
      _buscandoHuesped = true;
      _resultados = null;
    });
    try {
      final pagina = await widget.huespedes.listar(
        pagina: 1,
        tamano: 5,
        q: texto,
      );
      if (!mounted) return;
      setState(() {
        _buscandoHuesped = false;
        _resultados = pagina.items;
      });
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() {
        _buscandoHuesped = false;
        _error = error.mensaje;
      });
    }
  }

  Future<void> _consultarDisponibilidad() async {
    final numero = int.tryParse(_numeroHuespedes.text.trim()) ?? 1;
    setState(() {
      _consultando = true;
      _disponibles = null;
      _habitacion = null;
      _error = null;
    });
    try {
      final disponibles = await widget.service.disponibilidad(
        DisponibilidadConsulta(
          entrada: _entrada!,
          salida: _salida!,
          huespedes: numero,
        ),
      );
      if (!mounted) return;
      setState(() {
        _consultando = false;
        _disponibles = disponibles;
      });
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() {
        _consultando = false;
        _error = error.mensaje;
      });
    }
  }

  Future<void> _crear() async {
    if (_entrada == null || _salida == null) {
      _setError('Selecciona las fechas de la estancia');
      return;
    }
    if (!_salida!.isAfter(_entrada!)) {
      _setError('Check-out debe ser posterior a check-in');
      return;
    }
    if (_huesped == null) {
      _setError('Selecciona el huesped');
      return;
    }
    if (_habitacion == null) {
      _setError('Selecciona una habitacion disponible');
      return;
    }
    setState(() {
      _creando = true;
      _error = null;
    });
    final request = CrearReservaRequest(
      huespedId: _huesped!.id,
      habitacionId: _habitacion!.id,
      fechaEntrada: _entrada!,
      fechaSalida: _salida!,
      numeroHuespedes: int.tryParse(_numeroHuespedes.text.trim()) ?? 1,
    );
    try {
      await widget.service.crear(request);
      if (mounted) Navigator.of(context).pop(true);
    } on ApiException catch (error) {
      if (!mounted) return;
      setState(() {
        _creando = false;
        _error = error.esValidacion && error.mensajesPorCampo.isNotEmpty
            ? error.mensajesPorCampo.values.first
            : error.mensaje;
      });
    }
  }

  void _setError(String mensaje) {
    setState(() => _error = mensaje);
  }

  @override
  Widget build(BuildContext context) {
    final puedeCrear = _huesped != null && _habitacion != null;
    return AlertDialog(
      title: const Text('Nueva reserva'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _BotonFecha(
              etiqueta: 'Check-in',
              fecha: _entrada,
              alPulsar: () => _elegirFecha(true),
            ),
            const SizedBox(height: 8),
            _BotonFecha(
              etiqueta: 'Check-out',
              fecha: _salida,
              alPulsar: () => _elegirFecha(false),
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: _numeroHuespedes,
              decoration: const InputDecoration(
                labelText: 'Numero de huespedes',
              ),
              keyboardType: TextInputType.number,
            ),
            const Divider(height: 24),
            Text('Huesped', style: Theme.of(context).textTheme.titleSmall),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _busquedaHuesped,
                    decoration: const InputDecoration(
                      hintText: 'Buscar por nombre o documento',
                    ),
                    onSubmitted: (_) => _buscarHuesped(),
                  ),
                ),
                IconButton(
                  tooltip: 'Buscar',
                  icon: const Icon(Icons.search),
                  onPressed: _buscarHuesped,
                ),
              ],
            ),
            if (_buscandoHuesped)
              const Padding(
                padding: EdgeInsets.all(8),
                child: Center(child: CircularProgressIndicator()),
              ),
            if (_resultados != null)
              Column(
                children: [
                  for (final huesped in _resultados!)
                    ListTile(
                      dense: true,
                      selected: _huesped?.id == huesped.id,
                      title: Text(huesped.nombreCompleto),
                      subtitle: Text(huesped.documento),
                      trailing: _huesped?.id == huesped.id
                          ? const Icon(Icons.check)
                          : null,
                      onTap: () => setState(() => _huesped = huesped),
                    ),
                ],
              ),
            if (_huesped != null)
              Text(
                'Seleccionado: ${_huesped!.nombreCompleto}',
                style: Theme.of(context).textTheme.labelMedium,
              ),
            const Divider(height: 24),
            Text('Habitacion', style: Theme.of(context).textTheme.titleSmall),
            FilledButton.tonalIcon(
              onPressed: (_entrada != null && _salida != null)
                  ? _consultarDisponibilidad
                  : null,
              icon: _consultando
                  ? const SizedBox(
                      height: 16,
                      width: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.search),
              label: const Text('Ver disponibilidad'),
            ),
            if (_disponibles != null && _disponibles!.isEmpty)
              const Padding(
                padding: EdgeInsets.only(top: 8),
                child: Text('No hay habitaciones disponibles para el rango.'),
              ),
            if (_disponibles != null && _disponibles!.isNotEmpty)
              Column(
                children: [
                  for (final habitacion in _disponibles!)
                    ListTile(
                      dense: true,
                      selected: _habitacion?.id == habitacion.id,
                      title: Text(
                        'Hab. ${habitacion.numero} · '
                        '${humanizar(habitacion.tipo)}',
                      ),
                      subtitle: Text(
                        'Capacidad ${habitacion.capacidad} · '
                        '${formatearMonto(habitacion.precioPorNoche)}',
                      ),
                      trailing: _habitacion?.id == habitacion.id
                          ? const Icon(Icons.check)
                          : null,
                      onTap: () => setState(() => _habitacion = habitacion),
                    ),
                ],
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
      actions: [
        TextButton(
          onPressed: _creando ? null : () => Navigator.of(context).pop(false),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _creando || !puedeCrear ? null : _crear,
          child: _creando
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Crear reserva'),
        ),
      ],
    );
  }
}

class _BotonFecha extends StatelessWidget {
  const _BotonFecha({
    required this.etiqueta,
    required this.fecha,
    required this.alPulsar,
  });

  final String etiqueta;
  final DateTime? fecha;
  final VoidCallback alPulsar;

  @override
  Widget build(BuildContext context) {
    final texto = fecha == null
        ? etiqueta
        : '$etiqueta: ${formatearFecha(fecha!)}';
    return OutlinedButton.icon(
      onPressed: alPulsar,
      icon: const Icon(Icons.event_outlined),
      label: Text(texto),
    );
  }
}
