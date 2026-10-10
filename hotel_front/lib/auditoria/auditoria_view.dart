import 'package:flutter/material.dart';

import '../core/network/api_exception.dart';
import '../shared/models/pagina.dart';
import '../shared/utils/fecha_hora.dart';
import '../widgets/aviso_error.dart';
import '../widgets/barra_paginacion.dart';
import '../widgets/esqueleto.dart';
import '../widgets/estado_vacio.dart';
import '../widgets/tarjeta_hover.dart';
import 'auditoria_service.dart';
import 'models/auditoria_registro.dart';

/// Consulta de logs de auditoria (solo lectura, solo ADMIN).
class AuditoriaView extends StatefulWidget {
  const AuditoriaView({super.key, required this.service});

  final AuditoriaService service;

  @override
  State<AuditoriaView> createState() => _AuditoriaViewState();
}

class _AuditoriaViewState extends State<AuditoriaView> {
  static const int _tamano = 20;

  int _pagina = 1;
  late Future<Pagina<AuditoriaRegistro>> _futuro;

  @override
  void initState() {
    super.initState();
    _futuro = _consulta();
  }

  Future<Pagina<AuditoriaRegistro>> _consulta() {
    return widget.service.listar(pagina: _pagina, tamano: _tamano);
  }

  void _irPagina(int pagina) {
    setState(() {
      _pagina = pagina;
      _futuro = _consulta();
    });
  }

  void _recargar() => _irPagina(_pagina);

  void _abrirDetalle(AuditoriaRegistro registro) {
    showDialog<void>(
      context: context,
      builder: (_) => _DialogoAuditoria(registro: registro),
    );
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
              Text('Auditoría', style: Theme.of(context).textTheme.titleLarge),
              const Spacer(),
              IconButton(
                tooltip: 'Actualizar',
                icon: const Icon(Icons.refresh),
                onPressed: _recargar,
              ),
            ],
          ),
        ),
        Expanded(
          child: FutureBuilder<Pagina<AuditoriaRegistro>>(
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
                      : 'No se pudieron cargar los registros.',
                  alReintentar: _recargar,
                );
              }
              final pagina = snapshot.data!;
              if (pagina.items.isEmpty) {
                return const EstadoVacio(
                  icono: Icons.history_outlined,
                  mensaje: 'No hay registros.',
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
                        final registro = pagina.items[indice];
                        return _FilaAuditoria(
                          registro: registro,
                          alAbrir: () => _abrirDetalle(registro),
                        );
                      },
                    ),
                  ),
                  BarraPaginacion(
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

  int _totalPaginas(Pagina<AuditoriaRegistro> pagina) {
    final total = (pagina.total + _tamano - 1) ~/ _tamano;
    return total < 1 ? 1 : total;
  }
}

class _FilaAuditoria extends StatelessWidget {
  const _FilaAuditoria({required this.registro, required this.alAbrir});

  final AuditoriaRegistro registro;
  final VoidCallback alAbrir;

  @override
  Widget build(BuildContext context) {
    return TarjetaHover(
      onTap: alAbrir,
      child: ListTile(
        onTap: alAbrir,
        title: Text('${registro.accion} · ${registro.entidad}'),
        subtitle: Text(
          [
            '${registro.usuarioId ?? '-'}',
            formatearFechaHoraUtc(registro.createdAt),
            if (registro.resumenDetalle.isNotEmpty) registro.resumenDetalle,
          ].join(' · '),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: const Icon(Icons.chevron_right),
        dense: true,
      ),
    );
  }
}

class _DialogoAuditoria extends StatelessWidget {
  const _DialogoAuditoria({required this.registro});

  final AuditoriaRegistro registro;

  @override
  Widget build(BuildContext context) {
    final detalle = registro.detalle;
    return AlertDialog(
      title: Text('${registro.accion} · ${registro.entidad}'),
      content: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _Fila('Fecha', formatearFechaHoraUtc(registro.createdAt)),
            _Fila('Usuario', '${registro.usuarioId ?? '-'}'),
            _Fila(
              'Entidad',
              '${registro.entidad} #${registro.entidadId ?? '-'}',
            ),
            if (registro.ip != null) _Fila('IP', registro.ip!),
            if (detalle != null)
              for (final entrada in detalle.entries)
                _Fila(entrada.key, '${entrada.value}'),
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

class _Fila extends StatelessWidget {
  const _Fila(this.etiqueta, this.valor);

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
