# AGENTS.md — Hotel Fast Frontend

## 1. Objetivo

Desarrollar el frontend del sistema de gestión hotelera Hotel Fast con Flutter y Dart.

La primera plataforma objetivo es Web. El mismo proyecto debe poder compilarse posteriormente para Android (APK) y Windows Desktop.

El backend existente utiliza FastAPI y PostgreSQL. El frontend consume la API HTTP; nunca accede directamente a la base de datos.

## 2. Regla principal

Antes de implementar una funcionalidad:

1. Lee este archivo.
2. Consulta `docs/API_CONTRACT.md` si existe.
3. Revisa únicamente los archivos del backend necesarios para confirmar los endpoints, esquemas, permisos y reglas de negocio relacionados con la tarea.
4. Si el contrato no está documentado o hay dudas, inspecciona el backend original. No inventes endpoints, campos, estados ni respuestas.
5. Implementa solamente el alcance solicitado.

No vuelvas a analizar todo el backend en cada tarea si la documentación existente es suficiente.

## 3. Reglas de arquitectura

* Mantener separación entre presentación, estado, modelos y servicios HTTP.
* Evitar concentrar la aplicación en `main.dart`.
* Reutilizar componentes visuales, validadores y servicios.
* Centralizar la configuración de la API.
* Centralizar el tratamiento de errores HTTP.
* Mantener las pantallas independientes de los detalles de transporte.
* No duplicar en Dart las reglas de negocio que pertenecen a FastAPI.
* Usar nombres descriptivos y código tipado.
* Evitar dependencias innecesarias.
* Mantener compatibilidad con Web, Android y Windows.
* No modificar archivos de plataformas nativas salvo que sea necesario y esté justificado.

## 4. API y configuración

* La API existente es la fuente de verdad.
* Documentar las rutas confirmadas en `docs/API_CONTRACT.md`.
* No asumir que todos los endpoints utilizan el prefijo `/api`.
* No asumir nombres de campos o formatos de fecha.
* No guardar contraseñas ni tokens en código fuente.
* No incluir secretos en Git.
* Configurar la URL base mediante configuración por entorno o compilación.
* En producción, utilizar HTTPS.
* Implementar correctamente los estados HTTP, errores de red, expiración de sesión y respuestas inesperadas.
* No desactivar la validación de certificados TLS.

Para Flutter Web, tener en cuenta CORS configurado en FastAPI. Nunca solucionar errores CORS desactivando la seguridad del navegador.

## 5. Autenticación y permisos

* Inspeccionar el mecanismo de autenticación real del backend.
* Confirmar los endpoints de login, refresh y logout antes de implementarlos.
* No asumir que el backend utiliza JWT si no está confirmado.
* No asumir que existe refresh token rotation.
* Proteger las rutas privadas de la interfaz.
* Tratar la autorización del backend como la autoridad definitiva.
* No almacenar credenciales ni tokens en almacenamiento web inseguro sin evaluar el riesgo.
* No confundir ocultar un botón con validar permisos en el servidor.

## 6. Interfaz de usuario

* Idioma de la interfaz: español.
* Diseño profesional para un sistema de gestión hotelera.
* Navegación lateral en escritorio y adaptación para pantallas pequeñas.
* Diseño responsive para Web.
* Estados de carga, vacío, error y éxito.
* Formularios con validación y mensajes comprensibles.
* Confirmación antes de operaciones destructivas.
* Tablas con paginación y filtros solo cuando el backend los soporte.
* Formatos de moneda y fechas configurables; no asumir campos monetarios ni zona horaria.
* Accesibilidad básica: contraste, navegación por teclado y etiquetas claras.

## 7. Calidad y pruebas

Después de cada tarea:

1. Ejecutar `dart format` sobre los archivos modificados.
2. Ejecutar `flutter analyze`.
3. Ejecutar las pruebas pertinentes con `flutter test`.
4. Corregir los errores introducidos por el cambio.
5. No afirmar que las pruebas pasaron si no se ejecutaron.
6. No eliminar pruebas para conseguir un resultado exitoso.

Añadir pruebas para servicios HTTP, modelos, validaciones y widgets cuando corresponda.

## 8. Control de cambios

* Inspeccionar `git status` antes de trabajar.
* No sobrescribir cambios del usuario.
* No eliminar archivos existentes sin justificación.
* No hacer commits, push ni despliegues salvo petición expresa.
* No añadir paquetes sin comprobar que son necesarios y compatibles.

## 9. Gestión del contexto

* Trabajar por tareas pequeñas y delimitadas.
* Consultar archivos concretos en lugar de leer carpetas completas sin necesidad.
* Reutilizar la documentación existente.
* No volver a explicar ni implementar módulos ya terminados.
* Actualizar `docs/FRONTEND_PLAN.md` al completar una fase.
* Actualizar `docs/API_CONTRACT.md` cuando se confirmen contratos relevantes.
* Registrar decisiones importantes, problemas pendientes y pruebas ejecutadas.

## 10. Entrega obligatoria por tarea

Al finalizar, informar brevemente:

* Archivos creados o modificados.
* Funcionalidad implementada.
* Endpoints utilizados y cómo se verificaron.
* Comandos y pruebas ejecutadas con resultados reales.
* Problemas pendientes.
* Siguiente paso recomendado.

No implementar funcionalidades ajenas al alcance solicitado.
