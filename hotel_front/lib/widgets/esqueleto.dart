import 'package:flutter/material.dart';

/// Bloque gris para estados de carga (skeleton).
class Esqueleto extends StatelessWidget {
  const Esqueleto({super.key, this.ancho, this.alto = 16, this.radio = 8});

  final double? ancho;
  final double alto;
  final double radio;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: ancho,
      height: alto,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(radio),
      ),
    );
  }
}

/// Skeleton de lista con varias tarjetas, para reemplazar los spinners.
class ListaEsqueleto extends StatelessWidget {
  const ListaEsqueleto({super.key, this.filas = 6});

  final int filas;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(24),
      itemCount: filas,
      separatorBuilder: (_, _) => const SizedBox(height: 12),
      itemBuilder: (_, _) => Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: const [
              Esqueleto(ancho: 48, alto: 48, radio: 12),
              SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Esqueleto(ancho: 160, alto: 14),
                    SizedBox(height: 8),
                    Esqueleto(ancho: 240, alto: 12),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
