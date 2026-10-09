# Plan de desarrollo del frontend - Hotel Fast (Flutter)

Proyecto: `hotel_front` (Flutter y Dart; primera plataforma Web, luego Android y
Windows). Este plan se apoya unicamente en los endpoints confirmados en
`docs/API_CONTRACT.md`. No se planifica funcionalidad que el backend no exponga.

Estado actual del frontend: **Fases 0, 1, 2, 2b, 3, 4 y 5 completadas**. Login,
sesion con guardas por rol, shell, dashboard, catalogos cacheados y los modulos
de Habitaciones, Huespedes y Reservas (ciclo de vida completo: disponibilidad,
creacion, confirmar/cancelar/no-show/check-in/check-out/extender), todo en
Material 3 sin librerias de UI. Proximas entregas: Fase 6 (consumos, pagos y
cuenta) y el resto de los modulos.

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

## Fase 0 - Fundaciones tecnicas (COMPLETADA)

**Objetivo**: base del proyecto sin pantallas de negocio.

Entregado:

- **Estructura** en `lib/`: `config/`, `core/network/`, `shared/models/`,
  `shared/utils/` (las carpetas `screens/`, `widgets/`, `providers/`, `routes/`,
  `services/` quedan reservadas para fases posteriores).
- **Configuracion** (`lib/config/app_config.dart`): URL base por `--dart-define`
  (`API_BASE_URL`), valor por defecto `http://localhost:8000` para desarrollo,
  timeout configurable y resolucion segura de rutas y query params.
- **Cliente HTTP** (`lib/core/network/api_client.dart`): envuelve `package:http`,
  metodos `get/post/put/patch/delete`, timeout, decodificacion UTF-8, y conversion
  de toda falla a `ApiException`. Sin gestion de tokens (Fase 1).
- **Errores** (`lib/core/network/`): `ApiException`, `ErrorCampo`,
  `CodigosError` y `ErrorMapper`, que interpreta el sobre
  `{ detail, code, errors[] }` usando `code` como referencia estable. Contempla
  409 `CONFLICTO`/`REGLA_NEGOCIO` y 422 `VALIDACION` con detalle por campo,
  ademas de errores de red y tiempo de espera.
- **Compartidos** (`lib/shared/`): `Pagina<T>` (`{items,total,pagina,tamano}`) y
  utilidades `lectura_json.dart` (camelCase defensivo), `fecha_hora.dart`
  (`YYYY-MM-DD` e ISO-8601 tratando la falta de offset como UTC) y `moneda.dart`
  (lectura y formato de importes COP).
- **Pruebas** (`test/`): 54 pruebas unitarias de configuracion, serializacion,
  mapeo de errores y cliente HTTP con `MockClient` (sin servidor activo). Se
  elimino `test/widget_test.dart`, la plantilla del contador que referenciaba un
  `MyApp` inexistente.

**Criterio de cierre cumplido**: `dart format`, `flutter analyze` (sin issues) y
`flutter test` (54/54) en verde.

Pendiente para fases siguientes: widgets de estado (carga/vacio/error/exito), tema,
inyeccion de dependencias y almacenamiento/renovacion de tokens (Fase 1).

---

## Fase 1 - Autenticacion y sesion (COMPLETADA la capa de datos)

**Endpoints**: `POST /api/auth/login`, `POST /api/auth/refresh`,
`POST /api/auth/logout`, `POST /api/auth/me`.

Entregado (sin pantallas):

- **Modelos** (`lib/auth/models/`): `LoginRequest`, `AuthTokenResponse`
  (`token`/`refreshToken`/`tokenType`/`expiresIn`) y `Usuario`.
- **Persistencia** (`lib/auth/auth_storage.dart`): guarda/lee/borra los tokens con
  `shared_preferences` (Web, Android, Windows). En Web el respaldo es
  `localStorage`; riesgo aceptado en esta fase (access de vida corta + refresh
  rotativo). Evaluar almacenamiento seguro por plataforma antes de produccion.
- **Servicio** (`lib/auth/auth_service.dart`): `iniciarSesion`, `usuarioActual`,
  `cerrarSesion` (best-effort: limpia la sesion local aunque el servidor falle),
  `refrescar` y `restaurarSesion`. Persiste siempre el **ultimo** `refreshToken`
  recibido (rotacion del backend).
- **Interceptor** (`lib/core/network/`): `ApiClient` adjunta
  `Authorization: Bearer`, y ante un 401 renueva una vez y reintenta; si la
  renovacion falla, limpia la sesion y relanza el 401. El refresco es
  *single-flight* para no presentar el mismo refresh token dos veces (lo que
  revocaria la familia completa).
- **Pruebas** (`test/auth/`, `test/core/network/api_client_auth_test.dart`): 14
  pruebas del flujo de login, persistencia, rotacion, logout e interceptor con
  `MockClient` y `SharedPreferences` en memoria.

**Pendiente de la Fase 1** (UI): pantalla de login, guardas de ruta por rol
(`ADMIN`/`RECEPCION`), manejo visible de 429 y pantalla de cambio de contrasena.
Se posponen a la fase de UI (junto con el shell de la Fase 2).

**Criterio de cierre**: capa de datos y renovacion cubiertas por pruebas (68/68);
la verificacion contra la API real y las pantallas quedan para la fase de UI.

---

## Fase 2 - Login, estado de sesion y shell (COMPLETADA)

**Endpoints usados**: `POST /api/auth/login`, `GET /api/auth/me`,
`POST /api/auth/logout`, `POST /api/auth/refresh` (via interceptor).

Entregado:

- **Estado global** (`lib/auth/auth_controller.dart`, `lib/auth/auth_scope.dart`):
  `AuthController` ([ChangeNotifier] nativo, sin paquetes de estado) con
  `EstadoAuth` (`cargando` / `sinSesion` / `autenticado`), expuesto por
  `AuthScope` ([InheritedNotifier]). `restaurar()` valida la sesion persistida
  con `/me`; un refresco fallido devuelve la app al login (hook `alExpirar`).
- **Login** (`lib/screens/login_screen.dart`): formulario responsivo (usuario o
  correo + contrasena con mostrar/ocultar), estados de carga, error de
  credenciales (401), validacion (422) y rate limit (429). Detecta `@` para
  enviar `email` o `username`.
- **Shell** (`lib/screens/shell_screen.dart`, `lib/screens/modulos.dart`):
  `NavigationRail` en escritorio (>= 900 px, extendido >= 1200) y `Drawer` en
  pantallas angostas; menu filtrado por rol (ADMIN ve Usuarios y Auditoria;
  RECEPCION no), vista placeholder por modulo y logout con confirmacion.
- **Arranque** (`lib/main.dart`, `lib/app.dart`): compone `ApiClient` +
  `AuthService` + `AuthController` y decide entre carga, login y shell.

Decisiones visuales: solo Material 3 nativo (sin librerias de UI), un acento azul
(`ColorScheme.fromSeed`), layout centrado de ancho maximo 420 en login, y
navegacion lateral adaptativa. "Ocultar un boton no autoriza": el backend sigue
siendo la autoridad; la UI solo filtra lo visible.

**Pendiente de esta fase** (se difiere): dashboard con los indicadores
(`GET /api/dashboard`) y carga de catalogos (`GET /api/catalogos`) para poblar
desplegables. Endpoints confirmados en `docs/API_CONTRACT.md`; quedan para la
siguiente entrega de UI.

**Criterio de cierre**: `dart format`, `flutter analyze` (sin issues) y
`flutter test` (79/79) en verde, con pruebas de controlador de sesion y widgets
de login/shell.

---

## Fase 2b - Dashboard y catalogos (COMPLETADA)

**Endpoints**: `GET /api/dashboard`, `GET /api/catalogos`.

Entregado:

- **Catalogos** (`lib/catalogos/`): modelo `Catalogo` (`nombre`, `etiqueta`,
  `valores[]`) y `CatalogosService` con cache en memoria y carga unica
  (single-flight). Se precarga al entrar al shell (`ShellScreen`) y queda
  disponible para futuras pantallas via `AppScope` con `obtener(nombre)` y
  `valores(nombre)`, sin peticiones repetidas.
- **Dashboard** (`lib/dashboard/`): modelo `DashboardResumen` (los 8
  indicadores del contrato) y `DashboardService` para `GET /api/dashboard`.
  `DashboardView` renderiza tarjetas de Material 3 (icono + valor + etiqueta)
  en un `Wrap` responsivo, con estados de carga, error (con reintentar) y datos.
- **Integracion**: el modulo `Panel` del shell muestra el dashboard; los
  servicios se crean una vez en `HotelApp` y se exponen con `AppScope`
  ([InheritedWidget] nativo). El resto de modulos conserva el placeholder.
- **Pruebas** (`test/catalogos/`, `test/dashboard/`): 7 pruebas de parseo del
  dashboard, cache de catalogos, concurrencia y estados de la vista con mocks.

**Criterio de cierre cumplido**: `dart format`, `flutter analyze` (sin issues) y
`flutter test` (86/86) en verde. Sin librerias de graficos: tarjetas numericas
de Material.

Pendiente: formatos configurables de fecha/moneda en presentaciones futuras.

---

## Fase 3 - Habitaciones (COMPLETADA)

**Endpoints**: `GET/POST/PUT/DELETE /api/habitaciones`,
`PATCH .../estado`, `PATCH .../limpieza`.

Entregado:

- **Modelos y servicio** (`lib/habitaciones/`): `Habitacion` (parseo de
  `precioPorNoche` como numero COP) y `HabitacionPayload`; `HabitacionesService`
  con `listar` (filtros `estado`/`tipo`/`limpieza`), `crear`, `actualizar`,
  `cambiarEstado`, `cambiarLimpieza` y `eliminar`.
- **Vista** (`habitaciones_view.dart`): tarjetas responsivas (Wrap de `Card`
  M3), filtros por estado y tipo con `ChoiceChip` (valores desde los catalogos
  precargados), accion rapida de estado/limpieza via `PopupMenuButton`,
  formulario en dialogo para crear/editar (reutiliza catalogos) y eliminacion
  con confirmacion. Solo `ADMIN` ve crear/editar/eliminar.
- **Errores en UI**: SnackBar con `detail` del backend para 409
  (`CONFLICTO`/`REGLA_NEGOCIO`) y 403; en el formulario se muestran los errores
  por campo de 422 (`VALIDACION`).
- **Pruebas** (`test/habitaciones/`): 9 pruebas del servicio (parseo, filtros,
  metodos HTTP, propagacion de 409) y de la vista (listado, error+reintentar,
  dialogo admin, restriccion RECEPCION).

Decisiones de alcance: el backend **no pagina** habitaciones (arreglo completo) y
**no ofrece busqueda por texto** en `GET /api/habitaciones`, por lo que no se
invento paginacion ni buscador; solo los filtros confirmados.

**Criterio de cierre cumplido**: `dart format`, `flutter analyze` (sin issues) y
`flutter test` (95/95) en verde.

---

## Fase 4 - Huespedes (COMPLETADA)

**Endpoints**: `GET/POST/PUT/DELETE /api/huespedes`,
`GET /api/huespedes/{id}`, `GET /api/huespedes/{id}/reservas`.

Entregado:

- **Modelos y servicio** (`lib/huespedes/`): `Huesped` (con `nombreCompleto` y
  `documento`) y `HuespedPayload`; `HuespedesService` con `listar` paginado
  (`pagina`/`tamano`, `q`, `tipoDocumento`, `numeroDocumento`) usando la util
  generica `Pagina<T>` de la Fase 0, mas `crear`, `actualizar` y `eliminar`.
- **Vista** (`huespedes_view.dart`): listado paginado responsivo (tarjetas con
  iniciales, nombre y documento), barra de busqueda por nombre o documento
  (`q`), controles de paginacion previo/siguiente, detalle rapido en dialogo,
  y formulario en dialogo para registrar/editar (validaciones por contrato:
  documento 4-20 alfanumerico, telefono `\+?\d{7,15}`, correo y fecha de
  nacimiento no futura; integra el catalogo `tipos_documento`). Eliminar solo
  `ADMIN` y con confirmacion.
- **Errores en UI**: en el formulario se muestran los del 409 (`CONFLICTO`,
  documento duplicado) y 422 (`VALIDACION` por campo); el resto via SnackBar.
- **Pruebas** (`test/huespedes/`): 9 pruebas del servicio (parseo de pagina,
  query de busqueda, cuerpo de creacion, 409) y de la vista (listado, busqueda
  que re-consulta, estado de error, dialogo admin, restriccion RECEPCION).

Pendiente (se difiere a Fase 5): detalle del huesped con historial de reservas
(`GET /api/huespedes/{id}/reservas`), que se integrara junto al modulo de
reservas.

**Criterio de cierre cumplido**: `dart format`, `flutter analyze` (sin issues) y
`flutter test` (104/104) en verde.

---

## Fase 5 - Reservas, ciclo de vida principal (COMPLETADA)

**Endpoints**: `GET/POST/PUT /api/reservas`, `GET /api/reservas/{id}`,
`GET /api/reservas/disponibilidad`, y las acciones
`confirmar`, `cancelar`, `no-show`, `check-in`, `check-out`, `extender`.

Entregado:

- **Modelos** (`lib/reservas/models/`): `Reserva` (con resumen de `huesped` y
  `habitacion`, montos COP y fechas), `ReservaCheckOut` (resultado economico),
  `CrearReservaRequest` y `DisponibilidadConsulta`.
- **Servicio** (`lib/reservas/reservas_service.dart`): `listar` (paginado con
  filtros `estado`, `desde`, `hasta`), `disponibilidad`, `crear`, `obtener` y
  todas las transiciones de estado (`confirmar`, `cancelar` con `motivo`,
  `no-show`, `check-in`, `check-out`, `extender`).
- **Vista** (`lib/reservas/reservas_view.dart`): listado paginado con filtro por
  estado (`ChoiceChip` desde catalogos) y rango de fechas (pickers); dialogo de
  nueva reserva con busqueda de huesped, consulta de disponibilidad por rango y
  seleccion de habitacion; ficha/detalle con acciones contextuales por estado
  (`PENDIENTE`: Confirmar/Cancelar; `CONFIRMADA`: Check-in/No-show/Cancelar;
  `CHECK_IN`: Check-out/Extender; las de `CHECK_OUT`/`CANCELADA`/`NO_SHOW` se
  ocultan). El check-out muestra `totalCuenta`/`totalPagado`/`saldoPendiente`.
- **Errores en UI**: `detail` del backend en SnackBar para 409
  (`REGLA_NEGOCIO`/`CONFLICTO`) y 422 de las acciones; en el dialogo de creacion
  se muestran los errores por campo de 422 y la validacion local de
  `salida > entrada`.
- **Reutilizacion**: `BarraPaginacion` y `AvisoError` compartidos; utilidad
  `humanizar` centralizada en `shared/utils/formato.dart` (tambien aplicada en
  Habitaciones).
- **Pruebas** (`test/reservas/`): 11 pruebas del servicio (pagina+filtros,
  disponibilidad, creacion, check-out, cancelar/extender, 409) y de la vista
  (listado, filtro de estado que re-consulta, error+reintentar, acciones del
  detalle, dialogo de nueva reserva).

**Criterio de cierre cumplido**: `dart format`, `flutter analyze` (sin issues) y
`flutter test` (115/115) en verde.

Pendiente (Fase 6): consumos, pagos y cuenta dentro del detalle de reserva.

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
