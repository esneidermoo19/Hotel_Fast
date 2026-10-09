import '../../shared/utils/lectura_json.dart';

/// Usuario autenticado segun `GET /api/auth/me` y el login.
class Usuario {
  const Usuario({
    required this.id,
    required this.username,
    required this.email,
    required this.nombre,
    required this.role,
    required this.activo,
  });

  final int id;
  final String username;
  final String email;
  final String nombre;

  /// `ADMIN` o `RECEPCION`.
  final String role;
  final bool activo;

  bool get esAdministrador => role == 'ADMIN';

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: leerEntero(json['id']) ?? 0,
      username: leerTexto(json['username']) ?? '',
      email: leerTexto(json['email']) ?? '',
      nombre: leerTexto(json['nombre']) ?? '',
      role: leerTexto(json['role']) ?? '',
      activo: leerBooleano(json['activo']) ?? false,
    );
  }
}
