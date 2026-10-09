import 'dart:async';

import 'package:flutter/material.dart';

import 'app.dart';
import 'auth/auth_controller.dart';
import 'auth/auth_service.dart';
import 'config/app_config.dart';
import 'core/network/api_client.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  final api = ApiClient(config: AppConfig.fromEnvironment());
  final auth = AuthService(api: api);
  api.sesion = auth;
  final controller = AuthController(auth: auth);

  runApp(HotelApp(controller: controller));
  unawaited(controller.restaurar());
}
