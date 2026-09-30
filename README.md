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

Crea una habitación y cambia su estado usando el token:

```powershell
$habitacion = curl.exe -s -X POST http://localhost:8000/api/habitaciones -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d '{"numero":101,"tipo":"DOBLE","capacidad":2,"precioPorNoche":120.50}' | ConvertFrom-Json
curl.exe -i -X PATCH "http://localhost:8000/api/habitaciones/$($habitacion.id)/estado" -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d '{"estado":"OCUPADA"}'
```