import 'package:flutter/material.dart';

import '../auth/auth_scope.dart';
import '../auth/models/login_request.dart';
import '../core/network/api_exception.dart';

/// Pantalla de inicio de sesion.
///
/// Un solo campo acepta usuario o correo: si contiene `@` se envia como `email`,
/// en caso contrario como `username` (el backend admite cualquiera de los dos).
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _identificador = TextEditingController();
  final _password = TextEditingController();
  bool _verPassword = false;

  @override
  void dispose() {
    _identificador.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _enviar() async {
    final auth = AuthScope.de(context);
    if (!(_formKey.currentState?.validate() ?? false)) return;
    FocusScope.of(context).unfocus();
    final texto = _identificador.text.trim();
    final credenciales = texto.contains('@')
        ? LoginRequest(email: texto, password: _password.text)
        : LoginRequest(username: texto, password: _password.text);
    await auth.iniciarSesion(credenciales);
  }

  @override
  Widget build(BuildContext context) {
    final auth = AuthScope.de(context);
    final colores = Theme.of(context).colorScheme;

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(28),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Icon(
                        Icons.hotel_outlined,
                        size: 48,
                        color: colores.primary,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Hotel Fast',
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Gestion hotelera',
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      const SizedBox(height: 24),
                      TextFormField(
                        controller: _identificador,
                        enabled: !auth.enviando,
                        autofocus: true,
                        textInputAction: TextInputAction.next,
                        decoration: const InputDecoration(
                          labelText: 'Usuario o correo',
                          prefixIcon: Icon(Icons.person_outline),
                          border: OutlineInputBorder(),
                        ),
                        validator: (valor) =>
                            (valor == null || valor.trim().isEmpty)
                            ? 'Ingresa tu usuario o correo'
                            : null,
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _password,
                        enabled: !auth.enviando,
                        obscureText: !_verPassword,
                        textInputAction: TextInputAction.done,
                        onFieldSubmitted: (_) => _enviar(),
                        decoration: InputDecoration(
                          labelText: 'Contrasena',
                          prefixIcon: const Icon(Icons.lock_outline),
                          border: const OutlineInputBorder(),
                          suffixIcon: IconButton(
                            tooltip: _verPassword
                                ? 'Ocultar contrasena'
                                : 'Mostrar contrasena',
                            icon: Icon(
                              _verPassword
                                  ? Icons.visibility_off_outlined
                                  : Icons.visibility_outlined,
                            ),
                            onPressed: () =>
                                setState(() => _verPassword = !_verPassword),
                          ),
                        ),
                        validator: (valor) => (valor == null || valor.isEmpty)
                            ? 'Ingresa tu contrasena'
                            : null,
                      ),
                      if (auth.error != null) ...[
                        const SizedBox(height: 16),
                        _MensajeError(error: auth.error!),
                      ],
                      const SizedBox(height: 24),
                      FilledButton(
                        onPressed: auth.enviando ? null : _enviar,
                        style: FilledButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: auth.enviando
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Text('Iniciar sesion'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Mensaje de error del intento de inicio de sesion.
class _MensajeError extends StatelessWidget {
  const _MensajeError({required this.error});

  final ApiException error;

  String get _texto {
    if (error.statusCode == 401) {
      return 'Usuario o contrasena incorrectos.';
    }
    if (error.statusCode == 429) {
      return 'Demasiados intentos. Espera un momento e intentalo de nuevo.';
    }
    if (error.esValidacion && error.mensajesPorCampo.isNotEmpty) {
      return error.mensajesPorCampo.values.first;
    }
    return error.mensaje;
  }

  @override
  Widget build(BuildContext context) {
    final colores = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colores.errorContainer,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.error_outline, color: colores.onErrorContainer, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _texto,
              style: TextStyle(color: colores.onErrorContainer),
            ),
          ),
        ],
      ),
    );
  }
}
