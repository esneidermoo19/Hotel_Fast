import 'package:flutter/material.dart';

/// Controles de paginacion previo/siguiente con etiqueta de pagina actual.
class BarraPaginacion extends StatelessWidget {
  const BarraPaginacion({
    super.key,
    required this.etiqueta,
    required this.alAnterior,
    required this.alSiguiente,
  });

  final String etiqueta;
  final VoidCallback? alAnterior;
  final VoidCallback? alSiguiente;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              tooltip: 'Página anterior',
              icon: const Icon(Icons.chevron_left),
              onPressed: alAnterior,
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Text(etiqueta),
            ),
            IconButton(
              tooltip: 'Página siguiente',
              icon: const Icon(Icons.chevron_right),
              onPressed: alSiguiente,
            ),
          ],
        ),
      ),
    );
  }
}
