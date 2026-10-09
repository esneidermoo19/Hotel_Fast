import 'package:flutter/material.dart';

/// Tarjeta con micro-interaccion: eleva suavemente y resalta al pasar el cursor.
///
/// El fondo se aplica con un [Material] (no con color en el `BoxDecoration`)
/// para que la tinta de los `InkWell`/`ListTile` hijos siga siendo visible.
class TarjetaHover extends StatefulWidget {
  const TarjetaHover({super.key, this.onTap, required this.child});

  /// Opcional; define el cursor de clic (el hijo maneja el toque/informacion).
  final VoidCallback? onTap;
  final Widget child;

  @override
  State<TarjetaHover> createState() => _TarjetaHoverState();
}

class _TarjetaHoverState extends State<TarjetaHover> {
  bool _sobre = false;

  @override
  Widget build(BuildContext context) {
    final colores = Theme.of(context).colorScheme;
    return MouseRegion(
      cursor: widget.onTap != null
          ? SystemMouseCursors.click
          : MouseCursor.defer,
      onEnter: (_) => setState(() => _sobre = true),
      onExit: (_) => setState(() => _sobre = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 160),
        curve: Curves.easeOut,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: _sobre ? const Color(0x2E0F172A) : const Color(0x120F172A),
              blurRadius: _sobre ? 18 : 6,
              offset: Offset(0, _sobre ? 6 : 2),
            ),
          ],
        ),
        child: Material(
          color: _sobre ? colores.surfaceContainerHighest : colores.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0x1A0F172A)),
          ),
          clipBehavior: Clip.antiAlias,
          child: widget.child,
        ),
      ),
    );
  }
}
