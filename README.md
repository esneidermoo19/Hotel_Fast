# Hotel La Orquídea API

Backend REST para el PMS del hotel, construido con FastAPI, SQLAlchemy 2 y PostgreSQL.

## Requisitos

- Python 3.12
- Docker Compose, o una instancia PostgreSQL 16 accesible

## Configuración local

En PowerShell, crea un entorno virtual e instala las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Copia `.env.example` a `.env` solo si todavía no tienes un `.env`; si ya existe, agrega las variables que falten sin reemplazar tus valores. Para Docker, configura la misma clave en `POSTGRES_PASSWORD` y `DATABASE_URL`, y usa el puerto publicado indicado por `POSTGRES_PORT`. Para una instalación PostgreSQL local, configura `DATABASE_URL` con su usuario, clave y puerto (normalmente `5432`). No publiques `.env` ni guardes credenciales reales en el repositorio.

## PostgreSQL y migraciones

Arranca PostgreSQL en Docker con `docker compose up -d`. El puerto publicado por defecto es `5433` para permitir que conviva con una instalación local que use `5432`; `POSTGRES_PORT` permite cambiarlo. `DATABASE_URL` debe apuntar a la instancia elegida.

Aplica las migraciones:

```powershell
python -m alembic upgrade head
```

## Usuario inicial

Define las variables `SEED_ADMIN_EMAIL`, `SEED_ADMIN_USERNAME`, `SEED_ADMIN_NOMBRE`, `SEED_ADMIN_PASSWORD` y sus equivalentes `SEED_RECEPCION_*` en `.env`. El script crea ambos usuarios sin incluir contraseñas fijas en el código.

```powershell
python -m app.seed
```

## API y validaciones

Inicia la API:

```powershell
uvicorn app.main:app --reload
```

Ejecuta las pruebas y el linter:

```powershell
python -m pytest
ruff check .
```

## Ejemplos HTTP

Obtén un token; las credenciales se configuran con las variables de seed y no se guardan en el repositorio:

```powershell
$login = curl.exe -s -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin@ejemplo.com","email":"admin@ejemplo.com","password":"TU_CLAVE_ADMIN"}' | ConvertFrom-Json
$token = $login.token
```

El login devuelve además un `refreshToken`. El access token caduca a los 30 minutos; para renovarlo se rota el refresh token:

```powershell
$refresh = curl.exe -s -X POST http://localhost:8000/api/auth/refresh -H "Content-Type: application/json" -d "{\"refreshToken\":\"$($login.refreshToken)\"}" | ConvertFrom-Json
$token = $refresh.token
```

Cada rotación emite un refresh token nuevo e invalida el anterior. Presentar un token ya rotado se trata como robo de credenciales y revoca la familia completa de la sesión, por lo que el cliente debe guardar siempre el último `refreshToken` recibido. `POST /api/auth/logout` revoca el token recibido.

## Usuarios, auditoría y catálogos

`/api/usuarios` es exclusivo de `ADMIN` (crear, editar, desactivar, reactivar, eliminar). Un usuario desactivado no puede iniciar sesión y sus sesiones abiertas se revocan de inmediato. No se puede desactivar ni degradar al último administrador activo, ni modificar la propia cuenta desde esa pantalla.

`POST /api/auth/cambiar-password` permite a cualquier usuario autenticado cambiar su propia contraseña; al hacerlo se revocan el resto de sus sesiones. Exige contraseña actual y una nueva que cumpla la regla de fortaleza (mínimo 8 caracteres, al menos una letra y un número).

`GET /api/catalogos` devuelve los valores admitidos por el backend —roles, tipos y estados de habitación, estados de reserva, métodos de pago, tipos de consumo y tipos de documento— para que el frontend no los duplique. Requiere autenticación, no rol `ADMIN`.

`GET /api/auditoria` (solo `ADMIN`) lista la bitácora en orden descendente, filtrable por `entidad`, `entidad_id` y `accion`. Las contraseñas y los tokens nunca se registran: los campos sensibles se guardan como `[REDACTADO]`.

## Errores

Todas las respuestas de error usan el mismo sobre, con un `code` estable para el frontend:

```json
{ "detail": "Credenciales incorrectas", "code": "NO_AUTORIZADO" }
```

Los errores de validación (422) añaden el detalle por campo, con los nombres en camelCase:

```json
{ "detail": "Datos invalidos: ...", "code": "VALIDACION", "errors": [{ "campo": "precioPorNoche", "mensaje": "...", "tipo": "greater_than" }] }
```

Códigos en uso: `VALIDACION`, `NO_AUTORIZADO`, `TOKEN_INVALIDO`, `REFRESH_TOKEN_INVALIDO`, `SIN_PERMISOS`, `NO_ENCONTRADO`, `CONFLICTO`, `DEMASIADAS_SOLICITUDES`, `NO_DISPONIBLE`, `BASE_DATOS`.

## Límite de intentos

`POST /api/auth/login` y `POST /api/auth/refresh` aceptan como máximo `LOGIN_RATE_LIMIT` intentos por minuto y IP (por defecto `5/minute`). Al superarlo responden 429 con `code: DEMASIADAS_SOLICITUDES`.

Crea una habitación y cambia su estado usando el token:

```powershell
$habitacion = curl.exe -s -X POST http://localhost:8000/api/habitaciones -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d '{"numero":101,"tipo":"DOBLE","capacidad":2,"precioPorNoche":120.50}' | ConvertFrom-Json
curl.exe -i -X PATCH "http://localhost:8000/api/habitaciones/$($habitacion.id)/estado" -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d '{"estado":"OCUPADA"}'
```