/// Credenciales de inicio de sesion.
///
/// El backend acepta `username` o `email` (al menos uno) mas `password`.
class LoginRequest {
  const LoginRequest({this.username, this.email, required this.password});

  final String? username;
  final String? email;
  final String password;

  Map<String, dynamic> toJson() => {
    if (username != null) 'username': username,
    if (email != null) 'email': email,
    'password': password,
  };
}
