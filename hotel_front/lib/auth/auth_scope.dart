import 'package:flutter/widgets.dart';

import 'auth_controller.dart';

/// Expone el [AuthController] a la pantalla raiz y a las pantallas hijas.
///
/// [InheritedNotifier] nativo de Flutter: reconstruye a los dependientes cuando
/// el controlador notifica, sin paquetes de gestion de estado.
class AuthScope extends InheritedNotifier<AuthController> {
  const AuthScope({
    super.key,
    required AuthController controller,
    required super.child,
  }) : super(notifier: controller);

  static AuthController de(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<AuthScope>();
    assert(scope != null, 'No se encontro AuthScope en el arbol de widgets');
    return scope!.notifier!;
  }
}
