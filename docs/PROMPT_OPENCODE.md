# INSTRUCCIONES DE IMPLEMENTACIÓN Y REFACTORIZACIÓN - HOTEL FAST

## 1. ROL DEL AGENTE
Eres un Ingeniero de Software Senior experto en Backend con **Python (FastAPI, SQLAlchemy, Pydantic)** y Frontend con **Dart / Flutter**. 
Tu objetivo es refactorizar e implementar las funcionalidades de los módulos de **Recepción** (Room Rack, Reservas, Check-In/Check-Out, Huéspedes) y **Administración** (Consola de Usuarios, Control de Roles, Métricas) en el proyecto `Hotel_Fast`, migrando la estructura funcional y elevando el diseño visual al nivel de `Hotel-Gema`.

---

## 2. FLUJO DE TRABAJO CON GIT, PULL REQUESTS Y CI/CD (GITHUB ACTIONS)

Para cada tarea o sub-fase asignada, debes cumplir estrictamente el siguiente flujo de trabajo:

1. **Creación de Rama:**
   - Para cada tarea específica, crea y cámbiate a una rama descriptiva a partir de `main` (ej. `feat/room-rack-fastapi`, `feat/reserva-wizard-flutter`, `feat/admin-console`).
2. **Desarrollo y Commits:**
   - Realiza commits pequeños, atómicos y con mensajes claros en formato *Conventional Commits* (ej. `feat: add check-in endpoint`, `fix: update room rack layout`).
3. **Creación de Pull Request (PR):**
   - Una vez completada la tarea en la rama, abre/crea el Pull Request hacia la rama principal (`main`) describiendo los cambios realizados y los componentes probados.
4. **Verificación de CI/CD (GitHub Actions):**
   - Asegúrate de que las acciones en GitHub Actions ejecuten y superen con éxito los flujos de integración continua:
     - Pruebas unitarias/integración (`pytest`).
     - Aplicación exitosa de migraciones de base de datos (`alembic upgrade head`).
     - Linter y verificación de sintaxis (`flutter test` / `pytest`).
5. **Merge y Limpieza de Ramas:**
   - Una vez aprobada y fusionada (*merged*) la PR a `main` sin conflictos ni fallos en CI/CD, elimina la rama de función local y remota para mantener el repositorio limpio.

---

## 3. REGLAS BÁSICAS Y RESTRICCIONES DE CÓDIGO

1. **Arquitectura:**
   - Conserva la estructura existente: `app/` para el backend de FastAPI en Python y `hotel_front/` para el frontend de Flutter en Dart.
   - Respeta el flujo `Routers -> Services -> Schemas -> Models` en FastAPI, y `Services -> Views -> Models -> Widgets` en Flutter.
   - Toda la lógica de negocio (transiciones de estado, cálculos de tarifas, validaciones) debe residir en `app/services/` y no en los enrutadores (`routers`).

2. **Backend (Python / FastAPI):**
   - Usa exclusivamente Pydantic v2 para la validación de esquemas (`app/schemas/`).
   - Todos los endpoints deben retornar respuestas estructuradas e incluir códigos de estado HTTP apropiados (200, 201, 400, 404, 422).
   - No rompas las pruebas existentes (`tests/`).

3. **Frontend (Dart / Flutter):**
   - Mantén y reutiliza la configuración temática global de `lib/theme/app_theme.dart`.
   - Canaliza todas las peticiones HTTP mediante `ApiClient` (`lib/core/network/api_client.dart`) para conservar la gestión de tokens JWT.
   - Maneja los estados de Carga (`Loading`), Error (`AvisoError`) y Datos Vacíos (`EstadoVacio`) en todas las vistas.

---

## 4. TAREAS DE IMPLEMENTACIÓN LÓGICA Y ENDPOINTS

### FASE 1: BACKEND (Python - FastAPI / `app/`)

1. **Módulo de Recepción (Room Rack & Estados):**
   - Implementar `GET /api/v1/habitaciones/room-rack` en `app/routers/habitaciones.py` para devolver las habitaciones clasificadas por piso y estado (`DISPONIBLE`, `OCUPADA`, `MANTENIMIENTO`, `LIMPIEZA`).
   - Implementar `PATCH /api/v1/habitaciones/{id}/estado` en `app/services/habitacion_service.py` para permitir cambios manuales o automáticos de estado.

2. **Flujo Operativo de Reservas, Check-In y Check-Out:**
   - En `app/services/reserva_service.py`:
     - `POST /api/v1/reservas`: Crear reserva calculando `noches * tarifa_diaria`.
     - `POST /api/v1/reservas/{id}/check-in`: Cambiar reserva a `CHECK_IN`, habitación a `OCUPADA` e inicializar la `Cuenta` de hospedaje para consumos.
     - `POST /api/v1/reservas/{id}/check-out`: Verificar liquidación del saldo, pasar reserva a `CHECK_OUT` y la habitación automáticamente a `LIMPIEZA`.

3. **Módulo de Administración y Dashboard:**
   - En `app/routers/usuarios.py`: Restringir endpoints para que solo el rol `ADMINISTRADOR` pueda crear/editar usuarios y asignar roles.
   - En `app/routers/dashboard.py`: Exponer `GET /api/v1/dashboard/resumen` con métricas de ocupación (%), RevPAR, ingresos del día y balance de caja.

---

## 5. REFACTORIZACIÓN DE UI/UX EN FLUTTER (Dart / `hotel_front/lib/`)

Transforma las vistas simples de `Hotel_Fast` en una interfaz moderna, limpia y rica visualmente, igualando el nivel de `Hotel-Gema`:

1. **Estilo Visual e Identidad:**
   - Rediseña las pantallas principales usando tarjetas elevadas (`Card`), bordes suavizados (`BorderRadius.circular(16)`) y sombras sutiles.
   - Aplica contenedores estilo cristal o semi-transparentes (reutiliza `lib/widgets/cristal.dart`) y pastillas informativas de estado (`lib/widgets/pastilla_estado.dart`).

2. **Room Rack Visual (`lib/habitaciones/habitaciones_view.dart`):**
   - Reemplaza el listado plano por una **Matriz de Rejilla (`GridView.builder`)** interactiva agrupada por pisos.
   - Cada tarjeta de habitación debe mostrar en grande el número, tipo de cuarto, precio por noche e indicadores prominentes de color según su estado:
     - 🟢 **Disponible:** Verde suave / Esmeralda.
     - 🔴 **Ocupada:** Rojo / Coral (con el nombre del huésped actual o código de reserva).
     - 🟡 **Limpieza:** Amarillo / Ámbar.
     - ⚙️ **Mantenimiento:** Gris neutro.
   - Incluye micro-interacciones: al hacer tap/clic sobre la habitación, abre un modal con acciones inmediatas (Check-In directo, Ver Consumos, Limpieza Terminada).

3. **Wizard de Reservas (`lib/reservas/reservas_view.dart`):**
   - Estructura el proceso en un widget **`Stepper` de 3 pasos**:
     - **Paso 1:** Seleccionador de rango de fechas con vista previa de disponibilidad en tiempo real.
     - **Paso 2:** Ficha de datos del cliente (con autocompletado consultando `/api/v1/huespedes`).
     - **Paso 3:** Resumen financiero (subtotal, anticipo, saldo restante) estilizado como recibo previo.

4. **Consola de Administración y Dashboard (`lib/dashboard/` y `lib/usuarios/`):**
   - Muestra tarjetas de Métricas (KPI Cards) con íconos vectoriales, porcentajes de ocupación en barras de progreso y resúmenes monetarios formateados.
   - En la consola de usuarios (`lib/usuarios/usuarios_view.dart`), usa un `DataTable` moderno con switches de activación/desactivación e insignias de rol (`ADMINISTRADOR`, `RECEPCIONISTA`).

---

## 6. CRITERIOS DE ACEPTACIÓN
1. Todos los endpoints de Python/FastAPI deben responder correctamente y estar visibles en `/docs` (Swagger UI).
2. Las pantallas en Dart/Flutter deben refrescar su estado tras cada acción (check-in/check-out) sin errores visuales de desbordamiento (`overflows`).
3. Las migraciones de Alembic y pruebas automatizadas deben ejecutarse y pasar correctamente en GitHub Actions antes de aprobar cualquier Pull Request.
4. Tras la integración exitosa de cada PR, la rama de trabajo correspondiente debe quedar eliminada.