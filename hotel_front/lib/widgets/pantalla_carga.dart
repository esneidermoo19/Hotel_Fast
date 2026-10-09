import 'package:flutter/material.dart';

/// Pantalla de carga mientras se restaura la sesion persistida.
class PantallaCarga extends StatelessWidget {
  const PantallaCarga({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: CircularProgressIndicator()));
  }
}
