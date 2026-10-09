/// Cuerpo de creacion de usuario (`UsuarioCrear`).
class UsuarioCrear {
  const UsuarioCrear({
    required this.username,
    required this.email,
    required this.nombre,
    required this.password,
    required this.role,
  });

  final String username;
  final String email;
  final String nombre;

  /// Reglas de fortaleza: minimo 8, maximo 128, letra y numero.
  final String password;

  /// `ADMIN` o `RECEPCION`.
  final String role;

  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'email': email,
      'nombre': nombre,
      'password': password,
      'role': role,
    };
  }
}

/// Cuerpo de actualizacion de usuario (`UsuarioActualizar`); todos opcionales.
class UsuarioActualizar {
  const UsuarioActualizar({
    this.username,
    this.email,
    this.nombre,
    this.role,
    this.activo,
  });

  final String? username;
  final String? email;
  final String? nombre;
  final String? role;
  final bool? activo;

  Map<String, dynamic> toJson() {
    return {
      'username': ?username,
      'email': ?email,
      'nombre': ?nombre,
      'role': ?role,
      'activo': ?activo,
    };
  }
}
