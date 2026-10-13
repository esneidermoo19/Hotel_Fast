import 'package:flutter/foundation.dart';

/// Configuracion de la aplicacion y de la API.
///
/// La URL base se inyecta en tiempo de compilacion con `--dart-define`, de modo
/// que el mismo codigo sirve para desarrollo, Web, Android y Windows:
///
///   flutter run --dart-define=API_BASE_URL=http://192.168.1.10:8000
///
/// Si no se define, se usa el valor por defecto de desarrollo local.
///
/// En compilacion release solo se admite HTTPS (evita enviar credenciales en
/// claro y sufrir ataques de red). Para un desarrollo local en release (por
/// ejemplo, un APK de prueba contra un backend HTTP) usa el define
/// `--dart-define=ALLOW_INSECURE_HTTP=true`.
class AppConfig {
  AppConfig({
    required String baseUrl,
    this.timeout = const Duration(seconds: 15),
    bool? permitirHttp,
  }) : baseUrl = _normalizar(
         baseUrl,
         permitirHttp: permitirHttp ?? !kReleaseMode,
       );

  /// URL base de la API, sin barra final.
  final String baseUrl;

  /// Tiempo maximo de espera de una solicitud HTTP.
  final Duration timeout;

  /// Valor por defecto: backend local (uvicorn escucha en el puerto 8000).
  ///
  /// En el emulador de Android, `localhost` apunta al emulador; usar el host
  /// de la maquina (10.0.2.2) con `--dart-define`.
  static const String urlPorDefecto = 'http://localhost:8000';

  static const String claveDartDefine = 'API_BASE_URL';

  /// Define que permite HTTP aun en release (solo para pruebas locales).
  static const String clavePermitirHttp = 'ALLOW_INSECURE_HTTP';

  /// Construye la configuracion leyendo el entorno de compilacion.
  factory AppConfig.fromEnvironment() {
    const url = String.fromEnvironment(
      claveDartDefine,
      defaultValue: urlPorDefecto,
    );
    const permitirHttp = bool.fromEnvironment(clavePermitirHttp);
    return AppConfig(baseUrl: url, permitirHttp: permitirHttp || !kReleaseMode);
  }

  /// Resuelve una ruta relativa (`/api/...`) contra la URL base.
  ///
  /// Los valores de `query` que sean `null` se omiten.
  Uri resolve(String path, {Map<String, dynamic>? query}) {
    final base = Uri.parse(baseUrl);
    final prefijo = base.path.endsWith('/')
        ? base.path.substring(0, base.path.length - 1)
        : base.path;
    final ruta = path.startsWith('/') ? path : '/$path';

    final parametros = <String, String>{};
    query?.forEach((clave, valor) {
      if (valor != null) {
        parametros[clave] = '$valor';
      }
    });

    return base.replace(
      path: '$prefijo$ruta',
      queryParameters: parametros.isEmpty ? null : parametros,
    );
  }

  static String _normalizar(String url, {required bool permitirHttp}) {
    final limpio = url.trim();
    if (limpio.isEmpty) {
      throw ArgumentError.value(
        url,
        'baseUrl',
        'La URL base no puede estar vacia',
      );
    }
    final uri = Uri.tryParse(limpio);
    if (uri == null ||
        !uri.isAbsolute ||
        (uri.scheme != 'http' && uri.scheme != 'https')) {
      throw ArgumentError.value(
        url,
        'baseUrl',
        'La URL base debe ser una URL absoluta http o https',
      );
    }
    if (uri.scheme == 'http' && !permitirHttp) {
      throw ArgumentError.value(
        url,
        'baseUrl',
        'La URL base debe usar HTTPS en produccion; '
            'usa --dart-define=ALLOW_INSECURE_HTTP=true solo para pruebas',
      );
    }
    return limpio.endsWith('/')
        ? limpio.substring(0, limpio.length - 1)
        : limpio;
  }
}
