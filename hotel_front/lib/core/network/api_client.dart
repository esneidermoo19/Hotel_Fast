import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../config/app_config.dart';
import 'api_exception.dart';
import 'error_mapper.dart';
import 'sesion_autenticacion.dart';

/// Cliente HTTP reutilizable para la API de Hotel Fast.
///
/// - Construye las URLs sobre [AppConfig].
/// - Aplica un timeout a cada solicitud.
/// - Decodifica JSON en UTF-8 (soporta acentos).
/// - Convierte cualquier falla en [ApiException] mediante [ErrorMapper].
/// - Si `sesion` esta asignada, adjunta `Authorization: Bearer` y, ante un 401,
///   intenta renovar la sesion una vez y reintenta la solicitud.
class ApiClient {
  ApiClient({required this.config, http.Client? cliente})
    : _cliente = cliente ?? http.Client();

  final AppConfig config;
  final http.Client _cliente;

  /// Sesion opcional; la asigna la capa de auth tras construir el cliente.
  SesionAutenticacion? sesion;

  /// Cierra el cliente subyacente.
  void cerrar() => _cliente.close();

  Future<Object?> get(
    String path, {
    Map<String, dynamic>? query,
    bool renovarEn401 = true,
  }) {
    return _conRenovacion(
      () => _ejecutar('GET', path, query: query),
      renovarEn401,
    );
  }

  Future<Object?> post(
    String path, {
    Object? body,
    Map<String, dynamic>? query,
    bool renovarEn401 = true,
  }) {
    return _conRenovacion(
      () => _ejecutar('POST', path, body: body, query: query),
      renovarEn401,
    );
  }

  Future<Object?> put(
    String path, {
    Object? body,
    Map<String, dynamic>? query,
    bool renovarEn401 = true,
  }) {
    return _conRenovacion(
      () => _ejecutar('PUT', path, body: body, query: query),
      renovarEn401,
    );
  }

  Future<Object?> patch(
    String path, {
    Object? body,
    Map<String, dynamic>? query,
    bool renovarEn401 = true,
  }) {
    return _conRenovacion(
      () => _ejecutar('PATCH', path, body: body, query: query),
      renovarEn401,
    );
  }

  Future<void> delete(
    String path, {
    Map<String, dynamic>? query,
    bool renovarEn401 = true,
  }) async {
    await _conRenovacion(
      () => _ejecutar('DELETE', path, query: query),
      renovarEn401,
    );
  }

  Future<Object?> _conRenovacion(
    Future<Object?> Function() accion,
    bool renovar,
  ) async {
    try {
      return await accion();
    } on ApiException catch (error) {
      final sesionActual = sesion;
      if (!renovar || error.statusCode != 401 || sesionActual == null) {
        rethrow;
      }
      final renovado = await sesionActual.refrescar();
      if (!renovado) {
        await sesionActual.alExpirarSesion();
        rethrow;
      }
      return await accion();
    }
  }

  Future<Object?> _ejecutar(
    String metodo,
    String path, {
    Object? body,
    Map<String, dynamic>? query,
  }) async {
    final uri = config.resolve(path, query: query);
    final request = http.Request(metodo, uri)
      ..headers['Accept'] = 'application/json';

    final token = sesion?.accessToken;
    if (token != null && token.isNotEmpty) {
      request.headers['Authorization'] = 'Bearer $token';
    }

    if (body != null) {
      request.headers['Content-Type'] = 'application/json; charset=utf-8';
      request.body = jsonEncode(body);
    }

    try {
      final streamed = await _cliente.send(request).timeout(config.timeout);
      final response = await http.Response.fromStream(streamed);
      return _procesar(response);
    } on TimeoutException {
      throw ErrorMapper.deTiempoDeEspera(config.timeout);
    } on http.ClientException catch (error) {
      throw ErrorMapper.deRed(error.message);
    } on ApiException {
      rethrow;
    } catch (error) {
      throw ErrorMapper.deRed(error.toString());
    }
  }

  Object? _procesar(http.Response response) {
    final cuerpo = _decodificar(response);
    final status = response.statusCode;
    if (status >= 200 && status < 300) {
      return cuerpo;
    }
    throw ErrorMapper.desdeRespuesta(status, cuerpo);
  }

  Object? _decodificar(http.Response response) {
    if (response.bodyBytes.isEmpty) {
      return null;
    }
    final texto = utf8.decode(response.bodyBytes, allowMalformed: true);
    if (texto.isEmpty) {
      return null;
    }
    try {
      return jsonDecode(texto);
    } on FormatException {
      return texto;
    }
  }
}
