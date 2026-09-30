# Hotel La Orquídea API

Backend REST para el PMS del hotel, construido con FastAPI, SQLAlchemy 2 y PostgreSQL.

## Requisitos

- Python 3.12

## Configuración local

En PowerShell, crea un entorno virtual e instala las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Copia `.env.example` a `.env`; si ya existe, agrega las variables que falten sin reemplazar tus valores. `DATABASE_URL` debe apuntar a `sqlite:///./hotel_pms.db` para desarrollo local.

Inicializa la base de datos de desarrollo:

```powershell
python -m app.dev_db
```

Si las variables de seed están definidas en `.env`, carga los usuarios iniciales:

```powershell
python -m app.seed
```

Inicia la API:

```powershell
uvicorn app.main:app --reload
```

Ejecuta las pruebas y el linter:

```powershell
python -m pytest
ruff check .
```

## Migraciones y PostgreSQL

Las migraciones y el esquema de producción se verifican únicamente en **GitHub Actions** contra una instancia real de PostgreSQL. En local se usa SQLite con `app.dev_db` para crear las tablas de desarrollo rápido; el esquema de producción real se genera con Alembic.

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