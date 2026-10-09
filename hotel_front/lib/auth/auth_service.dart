import '../core/network/api_client.dart';
import '../core/network/api_exception.dart';
import '../core/network/sesion_autenticacion.dart';
import '../shared/utils/lectura_json.dart';
import 'auth_storage.dart';
import 'models/auth_token_response.dart';
import 'models/login_request.dart';
import 'models/usuario.dart';

/// Servicio de autenticacion: consume los endpoints de `/api/auth` y mantiene
/// los tokens en memoria y en [AuthStorage].
///
/// Implementa [SesionAutenticacion] para que [ApiClient] adjunte el Bearer y
/// renueve la sesion ante un 401.
class AuthService implements SesionAutenticacion {
  AuthService({required this.api, AuthStorage? storage})
    : storage = storage ?? AuthStorage();

  final ApiClient api;
  final AuthStorage storage;

  AuthTokenResponse? _tokens;
  Usuario? _usuario;
  Future<bool>? _refrescoEnCurso;

  /// Se invoca cuando la sesion se limpia (logout o refresco fallido).
  ///
  /// Permite que la capa de UI vuelva al login cuando el interceptor detecta
  /// que la sesion ya no es recuperable.
  void Function()? alExpirar;

  @override
  String? get accessToken => _tokens?.accessToken;

  /// Ultimo usuario cargado por login o [usuarioActual].
  Usuario? get usuario => _usuario;

  /// Carga los tokens persistidos al iniciar la app.
  ///
  /// Devuelve `true` si habia una sesion guardada.
  Future<bool> restaurarSesion() async {
    _tokens = await storage.leer();
    return _tokens != null;
  }

  Future<Usuario> iniciarSesion(LoginRequest credenciales) async {
    final data = await api.post(
      '/api/auth/login',
      body: credenciales.toJson(),
      renovarEn401: false,
    );
    final mapa = leerMapa(data) ?? const <String, dynamic>{};
    final tokens = AuthTokenResponse.fromJson(mapa);
    _tokens = tokens;
    _usuario = Usuario.fromJson(mapa);
    await storage.guardar(tokens);
    return _usuario!;
  }

  Future<Usuario> usuarioActual() async {
    final data = await api.get('/api/auth/me');
    _usuario = Usuario.fromJson(leerMapa(data) ?? const <String, dynamic>{});
    return _usuario!;
  }

  /// Revoca el refresh token en el servidor y limpia la sesion local.
  ///
  /// El cierre es local aunque el servidor falle (por ejemplo, token ya
  /// expirado).
  Future<void> cerrarSesion() async {
    final refresh = (await _asegurarTokens())?.refreshToken;
    try {
      if (refresh != null) {
        await api.post(
          '/api/auth/logout',
          body: {'refreshToken': refresh},
          renovarEn401: false,
        );
      }
    } on ApiException {
      // Best-effort: la sesion local se limpia igualmente.
    } finally {
      await alExpirarSesion();
    }
  }

  /// Renueva la sesion. Si ya hay un refresco en curso, lo comparte.
  ///
  /// Compartir el refresco es obligatorio con la rotacion del backend:
  /// presentar dos veces el mismo refresh token revocaria la familia completa.
  @override
  Future<bool> refrescar() {
    return _refrescoEnCurso ??= _refrescar().whenComplete(
      () => _refrescoEnCurso = null,
    );
  }

  @override
  Future<void> alExpirarSesion() async {
    _tokens = null;
    _usuario = null;
    await storage.borrar();
    alExpirar?.call();
  }

  Future<bool> _refrescar() async {
    final refresh = (await _asegurarTokens())?.refreshToken;
    if (refresh == null) {
      return false;
    }
    try {
      final data = await api.post(
        '/api/auth/refresh',
        body: {'refreshToken': refresh},
        renovarEn401: false,
      );
      final nuevos = AuthTokenResponse.fromJson(
        leerMapa(data) ?? const <String, dynamic>{},
      );
      _tokens = nuevos;
      await storage.guardar(nuevos);
      return true;
    } on ApiException {
      return false;
    }
  }

  Future<AuthTokenResponse?> _asegurarTokens() async {
    return _tokens ??= await storage.leer();
  }
}
