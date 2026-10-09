# Plan de desarrollo del frontend - Hotel Fast (Flutter)

Proyecto: `hotel_front` (Flutter y Dart; primera plataforma Web, luego Android y
Windows). Este plan se apoya unicamente en los endpoints confirmados en
`docs/API_CONTRACT.md`. No se planifica funcionalidad que el backend no exponga.

Estado actual del frontend: **esqueleto vacio**. `lib/main.dart` esta en blanco y
`test/widget_test.dart` todavia referencia `MyApp`. `pubspec.yaml` solo trae
`cupertino_icons` y `flutter_lints`. Hay que construir la base completa.

---

## Principios (reglas de `hotel_front/Agents.md`)

- Separar presentacion / estado / modelos / servicios HTTP; no concentrar todo en
  `main.dart`.
- Centralizar la configuracion de la API y el manejo de errores HTTP.
- No duplicar reglas de negocio del backend (transiciones de estado, permisos,
  validaciones de negocio). El backend es la autoridad.
- Interfaz en espanol; diseno responsive (navegacion lateral en escritorio).
- Sin secretos en el codigo; URL base configurable por entorno/compilacion.
- Compatibilidad Web, Android y Windows; no tocar plataformas nativas salvo necesidad.

---

## Fase 0 - Fundaciones tecnicas

**Objetivo**: base del proyecto sin pantallas de negocio.

- Configuracion de entorno: URL base de la API via `--dart-define`
  (`String.fromEnvironment`), con valor por defecto para desarrollo.
- Cliente HTTP (paquete `http` o `dio`) envuelto en un servicio central.
- Modelo de error tipado mapeando el sobre
  `{ detail, code, errors[] }` a una excepcion de aplicacion (`ApiException`).
- Manejo de 401: disparar renovacion de sesion (ver Fase 1) o cerrar sesion.
- Infraestructura de modelos con serializacion JSON en camelCase
  (recomendado `freezed`+`json_serializable`, o manual si se quiere evitar codegen).
- Almacenamiento de tokens: evaluar seguridad. En Web, `localStorage` es accesible
  por scripts; documentar el riesgo. Alternativas: memoria + refresh, o
  `flutter_secure_storage` (no disponible en Web) con estrategia por plataforma.
- Tema y estructura de carpetas (`lib/core`, `lib/models`, `lib/services`,
  `lib/features/*`).
- Widgets de estado reutilizables: carga, vacio, error y exito.

**Criterio de cierre**: `flutter analyze` y `flutter test` en verde; un test del
cliente HTTP y del mapeo de errores.

---

## Fase 1 - Autenticacion y sesion

**Endpoints**: `POST /api/auth/login`, `POST /api/auth/refresh`,
`POST /api/auth/logout`, `POST /api/auth/cambiar-password`, `GET /api/auth/me`.

- Pantalla de login por `username` o `email` + contrasena.
- Guardar `token`, `refreshToken` y `expiresIn`.
- Renovacion automatica: antes de expirar (`expiresIn`), llamar a `refresh`.
  Recordar que la rotacion invalida el token anterior y que reutilizar un token
  rotado revoca la sesion completa.
- Logout revocando el `refreshToken` actual.
- Interceptor/rutina que agrega `Authorization: Bearer <token>`.
- Guardas de ruta por rol (`ADMIN` / `RECEPCION`) usando `role` de login y `/me`.
- Manejo de 429 (`DEMASIADAS_SOLICITUDES`) con mensaje y `Retry-After`.
- Pantalla de cambio de contrasena propia.

**Criterio de cierre**: login/logout/refresh probados contra la API; test del
flujo de renovacion y del manejo de 401.

---

## Fase 2 - Shell, navegacion y dashboard

**Endpoints**: `GET /api/dashboard`, `GET /api/catalogos`.

- Layout con navegacion lateral (escritorio) y adaptacion movil.
- Menu condicionado por rol (ocultar no es autorizar; el backend valida).
- Dashboard con los 8 indicadores confirmados.
- Carga de catalogos al iniciar sesion para poblar desplegables.
- Formatos configurables de fecha y moneda (COP). Los montos llegan como numero.

**Criterio de cierre**: dashboard con estados de carga/error; catalogos cacheados.

---

## Fase 3 - Habitaciones

**Endpoints**: `GET/POST/PUT/DELETE /api/habitaciones`,
`GET /api/habitaciones/{id}`, `PATCH .../estado`, `PATCH .../limpieza`.

- Listado con filtros `estado`, `tipo`, `limpieza` (respuesta sin paginar).
- Alta/edicion/eliminacion solo para `ADMIN` (confirmacion antes de eliminar).
- Cambio rapido de estado y de limpieza (permitido a `RECEPCION`).
- Tablero visual de estados de habitacion (opcional, en una fase posterior).

**Criterio de cierre**: CRUD completo con validaciones del backend reflejadas.

---

## Fase 4 - Huespedes

**Endpoints**: `GET/POST/PUT/DELETE /api/huespedes`,
`GET /api/huespedes/{id}`, `GET /api/huespedes/{id}/reservas`.

- Listado paginado con busqueda `q` y filtros de documento.
- Formulario con validaciones (documento 4-20 alfanumerico, telefono, email,
  fecha de nacimiento no futura).
- Detalle con historial de reservas del huesped (paginado).
- Eliminar solo `ADMIN` y solo sin reservas.

**Criterio de cierre**: flujo de alta y busqueda completo; widget de paginacion reutilizable.

---

## Fase 5 - Reservas (nucleo del PMS)

**Endpoints**: `GET/POST/PUT /api/reservas`, `GET /api/reservas/{id}`,
`GET /api/reservas/disponibilidad`, y las acciones
`confirmar`, `cancelar`, `no-show`, `check-in`, `check-out`, `extender`.

- Listado paginado con filtros `estado`, `habitacionId`, `huespedId`, `desde`, `hasta`.
- Asistente de creacion: buscar huesped, consultar disponibilidad por rango y
  tipo, seleccionar habitacion, fijar numero de huespedes y observaciones.
- Detalle de reserva con acciones segun estado, respetando las transiciones:
  - `PENDIENTE` -> confirmar / cancelar / editar
  - `CONFIRMADA` -> check-in / no-show / cancelar / editar
  - `CHECK_IN` -> consumos / pagos / check-out / extender
- Cancelar exige motivo (3-500).
- Check-in y check-out con confirmacion; el check-out muestra el resultado
  economico (`totalCuenta`, `totalPagado`, `saldoPendiente`) aunque haya saldo.
- Extender pide `nuevaFechaSalida`.

**Criterio de cierre**: ciclo de vida completo de una reserva operable end-to-end.

---

## Fase 6 - Consumos, pagos y cuenta

**Endpoints**:
`GET/POST /api/reservas/{id}/consumos`, `POST .../consumos/{cid}/anular`,
`GET/POST /api/reservas/{id}/pagos`, `POST .../pagos/{pid}/anular`,
`GET /api/cuentas/{reservaId}`.

- Pestana de cuenta dentro del detalle de reserva: alojamiento, consumos, pagos y saldo.
- Consumos solo si la reserva esta en `CHECK_IN`.
- Pagos salvo en `CANCELADA`/`NO_SHOW`.
- Anular consumo/pago solo `ADMIN`, con motivo.
- Listados con `soloVigentes` y paginacion.

**Criterio de cierre**: cuenta cuadra contra `/api/cuentas`.

---

## Fase 7 - Usuarios y auditoria (ADMIN)

**Endpoints**: CRUD `/api/usuarios`, `desactivar`, `reactivar`,
`GET /api/auditoria`.

- Gestion de usuarios con roles; reglas de ultimo admin y de la propia cuenta.
  El filtro de listado se llama `soloActivos` (camelCase).
- Auditoria paginada con filtros `entidad`, `entidadId`, `accion`, `usuarioId`,
  `desde`, `hasta`.

**Criterio de cierre**: pantallas exclusivas de ADMIN con acceso denegado para RECEPCION.

---

## Fase 8 - Modulos no disponibles

- `reportes` y `horarios`: **los routers existen pero no exponen endpoints**.
  No implementar hasta que el backend los publique. Dejar entradas de menu
  deshabilitadas o no incluirlas.

---

## Fase 9 - Calidad, pruebas y empaquetado

- `dart format`, `flutter analyze`, `flutter test` en cada tarea.
- Pruebas de servicios HTTP (con cliente simulado), modelos, validadores y
  widgets clave; cubrir 401, 403, 409, 422, 429 y errores de red.
- Build Web y verificacion de CORS (agregar el origen real a `CORS_ORIGINS`).
- Builds para Android y Windows Desktop.
- HTTPS en produccion; no desactivar validacion TLS; no resolver CORS
  desactivando la seguridad del navegador.

---

## Riesgos y decisiones abiertas

1. **CORS**: fijar el puerto de Flutter Web o registrar su origen en
   `CORS_ORIGINS`; confirmar el valor desplegado. No usar `"*"` con credenciales.
2. **Almacenamiento de tokens en Web**: `localStorage` es legible por scripts;
   evaluar el riesgo y documentar la decision.
3. **Zona horaria**: los `datetime` podrian no traer offset en desarrollo;
   no asumir zona, interpretar y mostrar en America/Bogota.
4. **`openapi.json` del repo desactualizado**: no usarlo; regenerar o consultar
   `docs/API_CONTRACT.md`.
5. **Sin endpoint de "olvide mi contrasena"**: no disenar ese flujo.
6. **Paginacion heterogenea**: algunas listas paginan y otras no; respetar cada caso.
7. **Errores**: `REGLA_NEGOCIO` llega como 409 (unificado en docs y codigo);
   mapear por `code`, no solo por HTTP.
