# Contrato de la API - Hotel Fast

Documento generado a partir del backend FastAPI existente (rama `main`) y del
esquema OpenAPI real, regenerado desde el codigo con `app.openapi()`. No describe
funcionalidades que el backend no implemente.

- Titulo: `Hotel Fast - API de gestion hotelera`
- Version: `1.0.0` - OpenAPI `3.1.0`
- Fuente de verdad: `app/main.py`, `app/routers/*`, `app/schemas/*`, `app/models/*`
- Esquema exportable con: `python -m app.export_openapi` (escribe `openapi.json`)

> Nota: el `openapi.json` versionado en el repositorio esta **desactualizado**
> (no incluye reservas, check-in/out, cuentas, dashboard ni reportes). El contrato
> de este documento se obtuvo regenerando el esquema desde el codigo.

---

## 1. Convenciones generales

- **Prefijo**: la mayoria de rutas cuelga de `/api`. Excepciones confirmadas:
  `GET /docs`, `GET /openapi.json` (Swagger UI y esquema, sin prefijo).
- **JSON en camelCase**: los schemas heredan de `CamelCaseSchema` (alias `toCamel`).
  El campo del cuerpo y de las respuestas se envia en camelCase
  (`precioPorNoche`, `refreshToken`, `numeroHuespedes`, `fechaEntrada`, ...).
- **Identificadores**: enteros autoincrementales (`id`, `huespedId`, etc.).
- **Contenido**: `Content-Type: application/json` y `Accept: application/json`.
- **Paginacion** (solo listas marcadas como paginadas):
  - Query: `pagina` (>= 1, default 1) y `tamano` (1..100, default 20).
  - Respuesta: `{ "items": [...], "total": int, "pagina": int, "tamano": int }`.
- **Listas sin paginar**: devuelven un arreglo plano (`lista` completa).
- **Fechas de estancia**: `date` en formato ISO `YYYY-MM-DD` (`fechaEntrada`, `fechaSalida`).
- **Marcas de tiempo**: `datetime` en ISO-8601 (`createdAt`, `checkInReal`, `fechaPago`,
  `anuladoEn`). En base de datos se almacenan con zona UTC; ver seccion 3.
- **Dinero**: `Decimal` (BD `Numeric(12,2)`) en **COP**. Se serializa a JSON como
  **numero** (se aplica `float` en los serializers), p. ej. `120.5`. No se envia
  simbolo de moneda ni cadena de texto.
- **Reglas de "hoy" y semanas**: usan zona `America/Bogota` (`app/core/tiempo.py`).
- **Autenticacion**: `Authorization: Bearer <access_token>` (esquema HTTPBearer).

---

## 2. Sobre de error uniforme

Todas las respuestas de error usan:

```json
{ "detail": "Credenciales incorrectas", "code": "NO_AUTORIZADO" }
```

Los errores de validacion (422) agregan `errors` con detalle por campo (nombres en camelCase):

```json
{
  "detail": "Datos invalidos: ...",
  "code": "VALIDACION",
  "errors": [{ "campo": "precioPorNoche", "mensaje": "...", "tipo": "greater_than" }]
}
```

Codigos y estados reales (ver `app/core/errors.py`):

| code | HTTP | Significado |
| --- | --- | --- |
| `VALIDACION` | 422 | Datos o parametros invalidos |
| `NO_AUTORIZADO` | 401 | Credenciales incorrectas (incluye `WWW-Authenticate: Bearer`) |
| `TOKEN_INVALIDO` | 401 | Access token ausente/invalido/expirado |
| `REFRESH_TOKEN_INVALIDO` | 401 | Refresh token invalido, expirado, rotado o de familia revocada |
| `SIN_PERMISOS` | 403 | Rol sin permisos |
| `NO_ENCONTRADO` | 404 | Recurso inexistente |
| `CONFLICTO` | 409 | Conflicto con el estado actual |
| `REGLA_NEGOCIO` | 409 | Regla de negocio violada (subclase de conflicto) |
| `DEMASIADAS_SOLICITUDES` | 429 | Rate limit (incluye `Retry-After: 60`) |
| `NO_DISPONIBLE` | 503 | `GET /api/health` sin BD |
| `BASE_DATOS` | 503 | Error de base de datos |

---

## 3. Fechas, hora y formatos

- `date` (estancia, filtros `desde`/`hasta`, `fechaNacimiento`): `YYYY-MM-DD`.
- `datetime` (marcas): ISO-8601. El backend normaliza a UTC y `auditoria.created_at`
  se devuelve con `tzinfo=UTC`.
  - **Pendiente de verificar**: con SQLite de desarrollo algunos `datetime` pueden
    llegar sin offset (`2026-10-08T14:30:00` en vez de `...Z`). En produccion
    (PostgreSQL, `DateTime(timezone=True)`) se espera offset UTC. El cliente no
    debe asumir la zona: interpretar lo que llegue y, si no trae offset, tratarlo
    como UTC.
- Filtros `desde`/`hasta` de reservas y auditoria son **fechas inclusivas** en
  `America/Bogota` (se convierten a limites UTC en el backend).
- Montos: numero JSON, 2 decimales, COP.

---

## 4. Autenticacion y sesiones

Implementacion real (`app/routers/auth.py`, `app/core/security.py`,
`app/services/refresh_token_service.py`):

- Esquema: **JWT** firmado con `HS256` (`SECRET_KEY`). El access token lleva
  `sub` (id de usuario), `role` y `exp`.
- **Access token**: expira segun `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30 min).
  El login/refresh devuelven `expiresIn` en **segundos** (default `1800`).
- **Refresh token**: cadena aleatoria opaca (32 bytes, `token_urlsafe`), no JWT.
  Se guarda solo su hash SHA-256. Expira segun `REFRESH_TOKEN_EXPIRE_DAYS`
  (default en codigo 30; `.env.example` sugiere 7 - depende del entorno).
- **Rotacion**: `POST /api/auth/refresh` emite un refresh nuevo e invalida el anterior
  (misma familia). Reutilizar un token rotado revoca **toda la familia** (posible robo).
  El cliente debe guardar siempre el ultimo `refreshToken` recibido.
- **Logout**: `POST /api/auth/logout` revoca el refresh token enviado (idempotente, 204).
  No revoca el access token (sigue valido hasta expirar; es lo normal en JWT).
- **Cambiar contrasena**: revoca **todas** las sesiones del usuario.
- **Usuario desactivado**: no puede iniciar sesion y sus sesiones se revocan.
- **Rate limit**: login y refresh limitados a `LOGIN_RATE_LIMIT_PER_MINUTE`
  (default 5/min por IP). Al exceder: 429 `DEMASIADAS_SOLICITUDES`.

### Endpoints de autenticacion

| Metodo | Ruta | Auth | Cuerpo | Respuesta |
| --- | --- | --- | --- | --- |
| POST | `/api/auth/login` | No | `{ username?, email?, password }` (requiere al menos uno de username/email) | 200 `LoginResponse` |
| POST | `/api/auth/refresh` | No (usa refresh token) | `{ refreshToken }` | 200 `TokenPair` |
| POST | `/api/auth/logout` | No (usa refresh token) | `{ refreshToken }` | 204 sin cuerpo |
| POST | `/api/auth/cambiar-password` | Bearer | `{ passwordActual, passwordNuevo }` | 200 `{ mensaje }` |
| GET | `/api/auth/me` | Bearer | - | 200 `UsuarioRead` |

**LoginResponse**:
`token`, `refreshToken`, `tokenType` (`"bearer"`), `expiresIn` (int segundos),
`id`, `username`, `email`, `nombre`, `role`.

**TokenPair** (refresh): `token`, `refreshToken`, `tokenType`, `expiresIn`.

Errores: login `401 NO_AUTORIZADO`; refresh/logout `401 REFRESH_TOKEN_INVALIDO`;
cambiar-password `401 TOKEN_INVALIDO` / `422 VALIDACION`; ambos de login/refresh `429`.

Reglas de contrasena (crear usuario y cambiar-password): minimo 8 y maximo 128
caracteres, al menos una letra y al menos un numero.

---

## 5. Roles y permisos

Unicos roles existentes (`RolUsuario`): `ADMIN` y `RECEPCION`.

- `ADMIN`: todo.
- `RECEPCION`: operacion diaria. No puede gestionar usuarios, catalogos de
  creacion/edicion/eliminacion de habitaciones, ni anular pagos/consumos.

| Recurso | ADMIN | RECEPCION |
| --- | --- | --- |
| Habitaciones: consultar | Si | Si |
| Habitaciones: crear/editar/eliminar | Si | No (`403 SIN_PERMISOS`) |
| Habitaciones: cambiar estado/limpieza | Si | Si |
| Huespedes: listar/crear/editar | Si | Si |
| Huespedes: eliminar | Si | No |
| Reservas (todas las operaciones) | Si | Si |
| Consumos: listar/crear | Si | Si |
| Consumos: anular | Si | No |
| Pagos: listar/crear | Si | Si |
| Pagos: anular | Si | No |
| Cuentas: consultar | Si | Si |
| Dashboard | Si | Si |
| Usuarios (todas) | Si | No |
| Auditoria | Si | No |
| Catalogos | Si | Si (cualquier usuario autenticado) |

---

## 6. Catalogo de endpoints

### 6.1 Salud

| Metodo | Ruta | Auth | Respuesta / errores |
| --- | --- | --- | --- |
| GET | `/api/health` | No | 200 `{ "status": "ok" }`; 503 `NO_DISPONIBLE` si la BD falla |

### 6.2 Habitaciones (`/api/habitaciones`)

| Metodo | Ruta | Auth | Notas |
| --- | --- | --- | --- |
| GET | `/api/habitaciones` | Bearer (ADMIN/RECEPCION) | Arreglo completo. Filtros: `estado`, `tipo`, `limpieza` |
| GET | `/api/habitaciones/{habitacionId}` | Bearer | 404 si no existe |
| POST | `/api/habitaciones` | ADMIN | 201. 409 si el `numero` ya existe |
| PUT | `/api/habitaciones/{habitacionId}` | ADMIN | Reemplazo con `HabitacionUpdate` (= Create) |
| PATCH | `/api/habitaciones/{habitacionId}/estado` | Bearer | Cuerpo `{ estado }` |
| PATCH | `/api/habitaciones/{habitacionId}/limpieza` | Bearer | Cuerpo `{ limpieza }` (permitido aunque `OCUPADA`) |
| DELETE | `/api/habitaciones/{habitacionId}` | ADMIN | 204. 409 si tiene reservas futuras |

**HabitacionCreate/Update**: `numero` (> 0), `tipo`, `capacidad` (>= 1),
`precioPorNoche` (> 0, 2 decimales), `estado` (default `DISPONIBLE`),
`descripcion` (opcional).

**HabitacionRead**: lo anterior + `id`, `limpieza`, `createdAt`, `updatedAt`.
`precioPorNoche` en JSON es numero.

### 6.3 Huespedes (`/api/huespedes`) - paginado

| Metodo | Ruta | Auth | Notas |
| --- | --- | --- | --- |
| GET | `/api/huespedes` | Bearer | Paginado. Query: `q`, `tipoDocumento`, `numeroDocumento`, `pagina`, `tamano` |
| GET | `/api/huespedes/{huespedId}` | Bearer | 404 si no existe |
| POST | `/api/huespedes` | Bearer | 201. 409 documento duplicado (unico por tipo) |
| PUT | `/api/huespedes/{huespedId}` | Bearer | 409 documento duplicado |
| DELETE | `/api/huespedes/{huespedId}` | ADMIN | 204. 409 si tiene reservas |
| GET | `/api/huespedes/{huespedId}/reservas` | Bearer | Paginado; orden por entrada descendente |

**HuespedCreate/Update**: `tipoDocumento`, `numeroDocumento` (4-20 alfanumericos),
`nombres` (1-120), `apellidos` (1-120), `email` (opcional), `telefono`
(opcional, `^\+?\d{7,15}$`), `nacionalidad` (opcional, <=80), `fechaNacimiento`
(opcional, no futura), `direccion` (opcional), `observaciones` (opcional).

**HuespedRead**: lo anterior + `id`, `createdAt`, `updatedAt`.

**HuespedResumen** (usado dentro de reservas): `id`, `nombres`, `apellidos`,
`tipoDocumento`, `numeroDocumento`.

**ReservaDeHuespedRead**: `id`, `codigo`, `habitacionId`, `fechaEntrada`,
`fechaSalida`, `estado`.

### 6.4 Reservas (`/api/reservas`)

| Metodo | Ruta | Auth | Notas |
| --- | --- | --- | --- |
| GET | `/api/reservas/disponibilidad` | Bearer | Ruta fija declarada antes de `/{id}`. Query: `entrada`, `salida`, `huespedes` (default 1), `tipo` |
| POST | `/api/reservas` | Bearer | 201, estado inicial `PENDIENTE` |
| GET | `/api/reservas` | Bearer | Paginado. Query: `estado`, `habitacionId`, `huespedId`, `desde`, `hasta`, `pagina`, `tamano` |
| GET | `/api/reservas/{reservaId}` | Bearer | 404 |
| PUT | `/api/reservas/{reservaId}` | Bearer | Editable solo en `PENDIENTE`/`CONFIRMADA` |
| POST | `/api/reservas/{reservaId}/confirmar` | Bearer | `PENDIENTE` -> `CONFIRMADA` |
| POST | `/api/reservas/{reservaId}/cancelar` | Bearer | Cuerpo `{ motivo }` (3-500) |
| POST | `/api/reservas/{reservaId}/no-show` | Bearer | `CONFIRMADA` -> `NO_SHOW` |
| POST | `/api/reservas/{reservaId}/check-in` | Bearer | `CONFIRMADA` -> `CHECK_IN`, habitacion `OCUPADA` |
| POST | `/api/reservas/{reservaId}/check-out` | Bearer | `CHECK_IN` -> `CHECK_OUT`, habitacion `SUCIA`. Respuesta `CheckOutRead` |
| POST | `/api/reservas/{reservaId}/extender` | Bearer | Solo en `CHECK_IN`. Cuerpo `{ nuevaFechaSalida }` |

**ReservaCreate**: `huespedId` (>=1), `habitacionId` (>=1), `fechaEntrada`,
`fechaSalida`, `numeroHuespedes` (>=1), `observaciones` (opcional, <=1000).

**ReservaUpdate**: todos los campos anteriores opcionales (comportamiento de
actualizacion parcial aunque el metodo sea PUT).

**ReservaRead**: `id`, `codigo`, `huesped` (`HuespedResumen`), `habitacion`
(`HabitacionResumen`), `fechaEntrada`, `fechaSalida`, `numeroHuespedes`, `estado`,
`precioNocheAplicado`, `totalEstimado`, `observaciones`, `motivoCancelacion`,
`checkInReal`, `checkOutReal`, `creadaPor`, `createdAt`, `updatedAt`.

**HabitacionResumen** (disponibilidad y reserva): `id`, `numero`, `tipo`,
`capacidad`, `precioPorNoche`.

**CheckOutRead** = `ReservaRead` + `totalCuenta`, `totalPagado`, `saldoPendiente`.

Reglas relevantes:
- Una salida el mismo dia que otra entrada **no** se considera solapamiento.
- `CANCELADA` y `NO_SHOW` no bloquean disponibilidad.
- La entrada no puede ser anterior a "hoy" en Bogota.
- La fecha de salida debe ser posterior a la de entrada.
- El precio por noche se **congela** al crear; cambiar fechas/habitacion recalcula.
- Extender no revalida estado de la habitacion ni que la salida actual siga en el futuro.

Errores tipicos: `403 SIN_PERMISOS`, `404 NO_ENCONTRADO`, `409 CONFLICTO`
(transicion invalida, solapamiento, capacidad, rango, entrada en el pasado),
`422 VALIDACION`.

### 6.5 Consumos (`/api/reservas/{reservaId}/consumos`) - paginado

| Metodo | Ruta | Auth | Notas |
| --- | --- | --- | --- |
| GET | `/api/reservas/{reservaId}/consumos` | Bearer | Paginado. Query `soloVigentes` (bool, default false) |
| POST | `/api/reservas/{reservaId}/consumos` | Bearer | 201. Solo si la reserva esta en `CHECK_IN` |
| POST | `/api/reservas/{reservaId}/consumos/{consumoId}/anular` | ADMIN | Cuerpo `{ motivoAnulacion }` |

**ConsumoCreate**: `descripcion` (1-200), `cantidad` (> 0), `precioUnitario` (> 0, 2 dec).
**ConsumoAnular**: `motivoAnulacion` (1-500).
**ConsumoRead**: `id`, `reservaId`, `descripcion`, `cantidad`, `precioUnitario`,
`total` (calculado = `precioUnitario * cantidad`), `anulado`, `registradoPor`,
`anuladoPor`, `anuladoEn`, `motivoAnulacion`, `createdAt`, `updatedAt`.

### 6.6 Pagos (`/api/reservas/{reservaId}/pagos`) - paginado

| Metodo | Ruta | Auth | Notas |
| --- | --- | --- | --- |
| GET | `/api/reservas/{reservaId}/pagos` | Bearer | Paginado. Query `soloVigentes` (bool, default false) |
| POST | `/api/reservas/{reservaId}/pagos` | Bearer | 201. Permitido salvo `CANCELADA` y `NO_SHOW` |
| POST | `/api/reservas/{reservaId}/pagos/{pagoId}/anular` | ADMIN | Cuerpo `{ motivoAnulacion }` |

**PagoCreate**: `monto` (> 0, 2 dec), `metodo` (`MetodoPago`), `tipo` (`TipoPago`),
`referencia` (opcional, <=100), `fechaPago` (datetime opcional).
**PagoAnular**: `motivoAnulacion` (1-500).
**PagoRead**: `id`, `reservaId`, `monto`, `metodo`, `tipo`, `referencia`, `anulado`,
`motivoAnulacion`, `fechaPago`, `registradoPor`, `anuladoPor`, `anuladoEn`,
`createdAt`, `updatedAt`.

### 6.7 Cuentas

| Metodo | Ruta | Auth | Respuesta |
| --- | --- | --- | --- |
| GET | `/api/cuentas/{reservaId}` | Bearer (ADMIN/RECEPCION) | 200 `CuentaRead`; 404 si no existe la reserva |

**CuentaRead**: `totalAlojamiento` (noches x precio aplicado),
`totalConsumosVigentes` (consumos no anulados), `totalPagosVigentes` (pagos no
anulados, excluye `REEMBOLSO`), `saldoPendiente`
(`alojamiento + consumos - pagos`), `detalleConsumos[]`, `detallePagos[]`.

### 6.8 Dashboard

| Metodo | Ruta | Auth | Respuesta |
| --- | --- | --- | --- |
| GET | `/api/dashboard` | Bearer (ADMIN/RECEPCION) | 200 `DashboardRead` |

**DashboardRead**: `reservasActivas` (PENDIENTE+CONFIRMADA+CHECK_IN),
`reservasPendientesCheckIn` (PENDIENTE+CONFIRMADA), `huespedesAlojados`
(suma de huespedes en CHECK_IN), `checkOutsDelDia` (por `checkOutReal` del dia
en Bogota), `habitacionesDisponibles`, `habitacionesOcupadas`,
`habitacionesEnMantenimiento`, `cuentasConSaldoPendiente`.

### 6.9 Usuarios (`/api/usuarios`) - solo ADMIN

| Metodo | Ruta | Notas |
| --- | --- | --- |
| GET | `/api/usuarios` | Paginado. Query: `rol`, `activo`, `q`, `soloActivos`, `pagina`, `tamano` |
| GET | `/api/usuarios/{usuarioId}` | 404 |
| POST | `/api/usuarios` | 201; 409 username/email existente |
| PUT | `/api/usuarios/{usuarioId}` | 409 reglas (ultimo admin, duplicados) |
| POST | `/api/usuarios/{usuarioId}/desactivar` | 409 reglas |
| POST | `/api/usuarios/{usuarioId}/reactivar` | - |
| DELETE | `/api/usuarios/{usuarioId}` | 204; 409 si es la propia cuenta |

> **Quirk verificado**: el parametro de listado se llama literalmente
> `solo_activos` (con guion bajo), no `soloActivos`. El resto de parametros son
> de una sola palabra (`rol`, `activo`, `q`) o camelCase.

**UsuarioRead**: `id`, `username`, `email`, `nombre`, `role`, `activo`,
`createdAt`, `updatedAt`.

**UsuarioCrear**: `username` (3-64, `^[A-Za-z0-9._-]+$`), `email`, `nombre`
(1-120), `password` (regla de fortaleza), `role` (default `RECEPCION`).

**UsuarioActualizar**: todos opcionales (`username`, `email`, `nombre`, `role`, `activo`).

Reglas: no se puede desactivar ni degradar al ultimo ADMIN activo; no se puede
modificar la propia cuenta en esa pantalla; un usuario desactivado no puede
iniciar sesion.

### 6.10 Auditoria (`/api/auditoria`) - solo ADMIN, paginado

| Metodo | Ruta | Notas |
| --- | --- | --- |
| GET | `/api/auditoria` | Query: `entidad`, `entidadId`, `accion`, `usuarioId`, `desde`, `hasta`, `pagina`, `tamano` |

Orden descendente por `createdAt`/`id`. `desde` > `hasta` devuelve
422 `VALIDACION`. Los campos sensibles del detalle se guardan como `[REDACTADO]`.

**AuditoriaRead**: `id`, `usuarioId` (nullable), `accion`, `entidad`,
`entidadId` (nullable), `ip` (nullable), `detalle` (objeto JSON o null), `createdAt`.

### 6.11 Catalogos (`/api/catalogos`) - cualquier usuario autenticado

| Metodo | Ruta | Respuesta |
| --- | --- | --- |
| GET | `/api/catalogos` | Arreglo de `CatalogoRead` |
| GET | `/api/catalogos/{nombre}` | `CatalogoRead`; 404 si no existe |

**CatalogoRead**: `nombre`, `etiqueta`, `valores[]` (lista de strings).

Nombres reales de catalogo (usar estos para poblar desplegables):

| nombre | etiqueta |
| --- | --- |
| `roles` | Roles de usuario |
| `tipos_habitacion` | Tipos de habitacion |
| `estados_habitacion` | Estados de habitacion |
| `estados_limpieza` | Estados de limpieza |
| `estados_reserva` | Estados de reserva |
| `metodos_pago` | Metodos de pago |
| `tipos_pago` | Tipos de pago |
| `tipos_turno` | Tipos de turno |
| `tipos_documento` | Tipos de documento |

> No existe un catalogo `tipos_consumo` (el README lo menciona, pero el codigo no).

---

## 7. Enums (estados y valores confirmados)

- **RolUsuario**: `ADMIN`, `RECEPCION`
- **TipoDocumento**: `CC`, `CE`, `PASAPORTE`, `TI`, `OTRO`
- **TipoHabitacion**: `SIMPLE`, `DOBLE`, `SUITE`, `PRESIDENCIAL`
- **EstadoHabitacion**: `DISPONIBLE`, `OCUPADA`, `MANTENIMIENTO`
- **EstadoLimpieza**: `LIMPIA`, `SUCIA`
- **EstadoReserva**: `PENDIENTE`, `CONFIRMADA`, `CHECK_IN`, `CHECK_OUT`, `CANCELADA`, `NO_SHOW`
- **MetodoPago**: `EFECTIVO`, `TARJETA`, `TRANSFERENCIA`, `OTRO`
- **TipoPago**: `ABONO`, `PAGO_FINAL`, `REEMBOLSO`
- **TipoTurno**: `MANANA`, `TARDE`, `NOCHE`, `PERSONALIZADO`

---

## 8. CORS para Flutter Web

Configurado en `app/main.py` con `CORSMiddleware`:

- `allow_origins = settings.cors_origins` (variable `CORS_ORIGINS`, lista JSON).
  Valor por defecto y en `.env.example`: `["http://localhost:5173"]`.
- `allow_origin_regex = settings.resolved_cors_origin_regex`: variable opcional
  `CORS_ORIGIN_REGEX`. En **desarrollo**, si no se define, se usa
  `^https?://(localhost|127\.0\.0\.1)(:\d+)?$`, que admite cualquier puerto de
  Flutter Web local. En **produccion** es `None` salvo que se configure de forma
  explicita, de modo que `CORS_ORIGINS` sigue siendo la fuente de verdad.
- `allow_credentials = True`
- `allow_methods = ["*"]`, `allow_headers = ["*"]`

Implicaciones para el frontend:

- En desarrollo, Flutter Web puede correr en cualquier puerto sin tocar la
  configuracion (localhost y 127.0.0.1 aceptados).
- En produccion hay que declarar el origen real (esquema + host + puerto) en
  `CORS_ORIGINS`; con `allow_credentials = True` **no se puede usar `"*"`**.
- La autenticacion es por header `Authorization` (no cookies), por lo que en
  teoria no se necesitan credenciales CORS; aun asi el backend las permite.

---

## 9. Pendientes de verificar / riesgos del contrato

1. **`openapi.json` versionado esta desactualizado**. No usarlo como fuente; se
   regenera con `python -m app.export_openapi`.
2. **Zona horaria de `datetime`**: con SQLite puede llegar sin offset. Confirmar
   el formato exacto en produccion (PostgreSQL).
3. **`REFRESH_TOKEN_EXPIRE_DAYS`**: el codigo default es 30 y `.env.example` usa 7.
   Confirmar el valor de cada entorno.
4. **CORS real**: confirmar los dominios de produccion declarados en
   `CORS_ORIGINS` (vive en `.env`, que no se inspecciona). Desarrollo ya esta
   cubierto por la regex local.
5. **`reportes` y `horarios`**: los routers existen pero **no exponen ningun
   endpoint** (`app/routers/reportes.py` y `horarios.py` solo declaran el prefijo).
   El frontend no puede implementar esas pantallas todavia.
6. **Discrepancia de estados de error**: resuelta; `REGLA_NEGOCIO` es **409** y
   `AGENTS.md` ya lo refleja.
7. **Parametro `solo_activos`**: resuelto; el listado de usuarios usa
   `soloActivos` (camelCase), consistente con el resto del API.
8. **Health** no requiere auth; el resto de recursos si.
9. El backend no expone endpoints de "olvide mi contrasena", registro publico ni
   cierre de todas las sesiones (solo cambiar-password revoca las propias).
