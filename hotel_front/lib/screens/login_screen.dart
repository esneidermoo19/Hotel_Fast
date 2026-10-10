import 'package:flutter/material.dart';

import '../auth/auth_scope.dart';
import '../auth/models/login_request.dart';
import '../core/network/api_exception.dart';
import '../theme/app_theme.dart';
import '../widgets/cristal.dart';

/// Pantalla de inicio de sesion.
///
/// Un solo campo acepta usuario o correo: si contiene `@` se envia como `email`,
/// en caso contrario como `username` (el backend admite cualquiera de los dos).
/// En escritorio usa una pantalla dividida (panel de marca + tarjeta flotante);
/// en pantallas angostas, una tarjeta de cristal sobre un degradado de lujo.
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
    final ancho = MediaQuery.sizeOf(context).width;
    final esEscritorio = ancho >= 900;
    final tarjeta = Cristal(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 420),
        child: _formulario(context),
      ),
    );

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(gradient: _degradado()),
        child: esEscritorio
            ? Row(
                children: [
                  const Expanded(child: _PanelMarca()),
                  Expanded(
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.all(24),
                        child: SingleChildScrollView(child: tarjeta),
                      ),
                    ),
                  ),
                ],
              )
            : Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: tarjeta,
                ),
              ),
      ),
    );
  }

  static LinearGradient _degradado() {
    return const LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [AppTheme.midnight, AppTheme.midnightClaro, Color(0xFF243B55)],
    );
  }

  Widget _formulario(BuildContext context) {
    final auth = AuthScope.de(context);
    return Form(
      key: _formKey,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Center(
            child: Container(
              height: 64,
              width: 64,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  colors: [AppTheme.oroClaro, AppTheme.oro],
                ),
              ),
              child: const Icon(Icons.hotel_outlined, color: AppTheme.midnight),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Hotel Fast',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.headlineSmall
                ?.copyWith(letterSpacing: 1.5),
          ),
          const SizedBox(height: 4),
          Text(
            'Gestión hotelera',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 28),
          TextFormField(
            controller: _identificador,
            enabled: !auth.enviando,
            autofocus: true,
            textInputAction: TextInputAction.next,
            decoration: const InputDecoration(
              labelText: 'Usuario o correo',
              prefixIcon: Icon(Icons.person_outline),
            ),
            validator: (valor) => (valor == null || valor.trim().isEmpty)
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
              labelText: 'Contraseña',
              prefixIcon: const Icon(Icons.lock_outline),
              suffixIcon: IconButton(
                tooltip: _verPassword
                    ? 'Ocultar contraseña'
                    : 'Mostrar contraseña',
                icon: Icon(
                  _verPassword
                      ? Icons.visibility_off_outlined
                      : Icons.visibility_outlined,
                ),
                onPressed: () => setState(() => _verPassword = !_verPassword),
              ),
            ),
            validator: (valor) => (valor == null || valor.isEmpty)
                ? 'Ingresa tu contraseña'
                : null,
          ),
          if (auth.error != null) ...[
            const SizedBox(height: 16),
            _MensajeError(error: auth.error!),
          ],
          const SizedBox(height: 24),
          FilledButton(
            onPressed: auth.enviando ? null : _enviar,
            child: auth.enviando
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: AppTheme.midnight,
                    ),
                  )
                : const Text('Iniciar Sesión'),
          ),
        ],
      ),
    );
  }
}

class _PanelMarca extends StatelessWidget {
  const _PanelMarca();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(56),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Row(
            children: [
              Container(
                height: 52,
                width: 52,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: [AppTheme.oroClaro, AppTheme.oro],
                  ),
                ),
                child: const Icon(
                  Icons.hotel_outlined,
                  color: AppTheme.midnight,
                ),
              ),
              const SizedBox(width: 16),
              Text(
                'Hotel Fast',
                style: Theme.of(context).textTheme.headlineMedium
                    ?.copyWith(color: Colors.white, letterSpacing: 1.5),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'Gestión hotelera premium',
            style: Theme.of(context).textTheme.titleMedium
                ?.copyWith(color: AppTheme.oroClaro, letterSpacing: 0.5),
          ),
          const SizedBox(height: 40),
          const _Caracteristica(
            icono: Icons.meeting_room_outlined,
            texto: 'Habitaciones, reservas y ciclo de vida completo',
          ),
          const SizedBox(height: 16),
          const _Caracteristica(
            icono: Icons.receipt_long_outlined,
            texto: 'Estado de cuenta, consumos y pagos',
          ),
          const SizedBox(height: 16),
          const _Caracteristica(
            icono: Icons.dashboard_outlined,
            texto: 'Panel operativo del día y catálogo centralizado',
          ),
        ],
      ),
    );
  }
}

class _Caracteristica extends StatelessWidget {
  const _Caracteristica({required this.icono, required this.texto});

  final IconData icono;
  final String texto;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icono, color: AppTheme.oroClaro, size: 22),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            texto,
            style: Theme.of(context).textTheme.bodyMedium
                ?.copyWith(color: Colors.white.withValues(alpha: 0.88)),
          ),
        ),
      ],
    );
  }
}

/// Mensaje de error del intento de inicio de sesion.
class _MensajeError extends StatelessWidget {
  const _MensajeError({required this.error});

  final ApiException error;

  String get _texto {
    if (error.statusCode == 401) {
      return 'Usuario o contraseña incorrectos.';
    }
    if (error.statusCode == 429) {
      return 'Demasiados intentos. Espera un momento e inténtalo de nuevo.';
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
        borderRadius: BorderRadius.circular(12),
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
