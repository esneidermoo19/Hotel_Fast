import '../../shared/utils/lectura_json.dart';
import '../../shared/utils/moneda.dart';

/// Imagen de una habitacion segun `HabitacionImagenRead` del contrato.
class HabitacionImagen {
  const HabitacionImagen({
    required this.id,
    required this.url,
    required this.orden,
    required this.esPrincipal,
  });

  final int id;

  /// Ruta relativa a la API (p. ej. `/media/abc.png`). Se resuelve contra la
  /// URL base con [AppConfig.resolveMediaUrl].
  final String url;
  final int orden;
  final bool esPrincipal;

  factory HabitacionImagen.fromJson(Map<String, dynamic> json) {
    return HabitacionImagen(
      id: leerEntero(json['id']) ?? 0,
      url: leerTexto(json['url']) ?? '',
      orden: leerEntero(json['orden']) ?? 0,
      esPrincipal: leerBooleano(json['esPrincipal']) ?? false,
    );
  }

  HabitacionImagen copiarCon({bool? esPrincipal}) {
    return HabitacionImagen(
      id: id,
      url: url,
      orden: orden,
      esPrincipal: esPrincipal ?? this.esPrincipal,
    );
  }
}

/// Habitacion segun `HabitacionRead` del contrato.
class Habitacion {
  const Habitacion({
    required this.id,
    required this.numero,
    required this.tipo,
    required this.capacidad,
    required this.precioPorNoche,
    required this.estado,
    required this.limpieza,
    this.descripcion,
    this.imagenPrincipalUrl,
    this.imagenes = const [],
  });

  final int id;
  final int numero;
  final String tipo;
  final int capacidad;

  /// Monto en COP (el backend lo envia como numero).
  final double precioPorNoche;

  /// `DISPONIBLE`, `OCUPADA` o `MANTENIMIENTO`.
  final String estado;

  /// `LIMPIA` o `SUCIA`.
  final String limpieza;
  final String? descripcion;

  /// Ruta relativa de la imagen principal, o `null` si no hay.
  final String? imagenPrincipalUrl;
  final List<HabitacionImagen> imagenes;

  /// Verdadero si la habitacion tiene al menos una imagen.
  bool get tieneImagenes => imagenes.isNotEmpty;

  factory Habitacion.fromJson(Map<String, dynamic> json) {
    return Habitacion(
      id: leerEntero(json['id']) ?? 0,
      numero: leerEntero(json['numero']) ?? 0,
      tipo: leerTexto(json['tipo']) ?? '',
      capacidad: leerEntero(json['capacidad']) ?? 0,
      precioPorNoche: leerMonto(json['precioPorNoche']) ?? 0,
      estado: leerTexto(json['estado']) ?? '',
      limpieza: leerTexto(json['limpieza']) ?? '',
      descripcion: leerTexto(json['descripcion']),
      imagenPrincipalUrl: leerTexto(json['imagenPrincipalUrl']),
      imagenes: [
        for (final mapa in leerListaDeMapas(json['imagenes']))
          HabitacionImagen.fromJson(mapa),
      ],
    );
  }
}

/// Cuerpo de creacion y actualizacion (`HabitacionCreate`/`Update`).
class HabitacionPayload {
  const HabitacionPayload({
    required this.numero,
    required this.tipo,
    required this.capacidad,
    required this.precioPorNoche,
    required this.estado,
    this.descripcion,
  });

  final int numero;
  final String tipo;
  final int capacidad;
  final double precioPorNoche;
  final String estado;
  final String? descripcion;

  Map<String, dynamic> toJson() {
    return {
      'numero': numero,
      'tipo': tipo,
      'capacidad': capacidad,
      'precioPorNoche': precioPorNoche,
      'estado': estado,
      if (descripcion != null) 'descripcion': descripcion,
    };
  }
}
