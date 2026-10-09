import 'dart:convert';

import 'package:hotel_front/auth/auth_controller.dart';
import 'package:hotel_front/auth/auth_service.dart';
import 'package:hotel_front/auth/auth_storage.dart';
import 'package:hotel_front/config/app_config.dart';
import 'package:hotel_front/core/network/api_client.dart';
import 'package:http/testing.dart';

/// Cliente HTTP simulado apuntando a la API local.
ApiClient crearApiSimulada(MockClientHandler handler) {
  return ApiClient(
    config: AppConfig(baseUrl: 'http://localhost:8000'),
    cliente: MockClient(handler),
  );
}

/// Construye un [AuthController] real conectado a un cliente HTTP simulado.
AuthController crearControladorAuth(MockClientHandler handler) {
  final api = crearApiSimulada(handler);
  final auth = AuthService(api: api, storage: AuthStorage());
  api.sesion = auth;
  return AuthController(auth: auth);
}

/// Respuesta de login/me valida para pruebas.
String loginJson({String role = 'ADMIN'}) {
  return jsonEncode({
    'token': 'access-1',
    'refreshToken': 'refresh-1',
    'tokenType': 'bearer',
    'expiresIn': 1800,
    'id': 1,
    'username': 'usuario',
    'email': 'usuario@example.com',
    'nombre': 'Usuario Prueba',
    'role': role,
    'activo': true,
  });
}
