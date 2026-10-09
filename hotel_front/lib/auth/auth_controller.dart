import 'package:flutter/foundation.dart';

import '../core/network/api_exception.dart';
import 'auth_service.dart';
import 'models/login_request.dart';
import 'models/usuario.dart';

/// Estado global de la sesion.
enum EstadoAuth { cargando, sinSesion, autenticado }

/// Mantiene el estado de autenticacion para la UI y delega en [AuthService].
///
/// Es un [ChangeNotifier] minimo: sin dependencias externas de gestion de
/// estado. La pantalla raiz lo escucha para decidir entre login y shell.
class AuthController extends ChangeNotifier {
  AuthController({required this.auth}) {
    auth.alExpirar = _sesionExpirada;
  }

  final AuthService auth;

  EstadoAuth _estado = EstadoAuth.cargando;
  Usuario? _usuario;
  ApiException? _error;
  bool _enviando = false;

  EstadoAuth get estado => _estado;
  Usuario? get usuario => _usuario;

  /// Ultimo error de inicio de sesion, o `null`.
  ApiException? get error => _error;

  /// `true` mientras se procesa un inicio de sesion.
  bool get enviando => _enviando;

  /// Restaura la sesion persistida al arrancar la app.
  Future<void> restaurar() async {
    try {
      final habiaSesion = await auth.restaurarSesion();
      if (!habiaSesion) {
        _estado = EstadoAuth.sinSesion;
        notifyListeners();
        return;
      }
      _usuario = await auth.usuarioActual();
      _estado = EstadoAuth.autenticado;
    } on ApiException {
      // Tokens vencidos o revocados: volver al login.
      _usuario = null;
      _estado = EstadoAuth.sinSesion;
    }
    notifyListeners();
  }

  Future<void> iniciarSesion(LoginRequest credenciales) async {
    _enviando = true;
    _error = null;
    notifyListeners();
    try {
      _usuario = await auth.iniciarSesion(credenciales);
      _estado = EstadoAuth.autenticado;
    } on ApiException catch (error) {
      _error = error;
      _estado = EstadoAuth.sinSesion;
    } finally {
      _enviando = false;
      notifyListeners();
    }
  }

  Future<void> cerrarSesion() async {
    await auth.cerrarSesion();
    _usuario = null;
    _error = null;
    _estado = EstadoAuth.sinSesion;
    notifyListeners();
  }

  /// Limpia el error mostrado (por ejemplo, al reintentar).
  void limpiarError() {
    if (_error == null) return;
    _error = null;
    notifyListeners();
  }

  void _sesionExpirada() {
    _usuario = null;
    _error = null;
    _estado = EstadoAuth.sinSesion;
    notifyListeners();
  }
}
