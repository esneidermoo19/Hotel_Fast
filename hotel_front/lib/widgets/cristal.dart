import 'dart:ui';

import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

/// Superficie con efecto glassmorphism (fondo translucido + desenfoque).
class Cristal extends StatelessWidget {
  const Cristal({
    super.key,
    required this.child,
    this.radio = 20,
    this.padding = const EdgeInsets.all(28),
    this.opacidad = 0.75,
    this.desenfoque = 18,
  });

  final Widget child;
  final double radio;
  final EdgeInsetsGeometry padding;
  final double opacidad;
  final double desenfoque;

  @override
  Widget build(BuildContext context) {
    final oscuro = Theme.of(context).brightness == Brightness.dark;
    return ClipRRect(
      borderRadius: BorderRadius.circular(radio),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: desenfoque, sigmaY: desenfoque),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            color: (oscuro ? AppTheme.midnightClaro : Colors.white).withValues(
              alpha: opacidad,
            ),
            borderRadius: BorderRadius.circular(radio),
            border: Border.all(color: Colors.white.withValues(alpha: 0.35)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x1A0F172A),
                blurRadius: 30,
                offset: Offset(0, 12),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
