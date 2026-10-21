# Hotel Web - convenciones

Cliente web de Hotel Fast: Vite + React + TypeScript estricto, conectado al API
FastAPI del repositorio. Esta tarea es solo la base: autenticacion, shell,
tema y estados reutilizables. Los modulos de negocio se implementan despues.

## Stack y versiones

- React 19.3.1, TypeScript 5.9.3, Vite 7.3.7, Node 24 (`.nvmrc`; `engines` >= 22.12).
- Tailwind CSS 3.4.19 + shadcn/ui (componentes en `src/components/ui`).
- react-router 7.18.4, @tanstack/react-query 5.104.5, react-hook-form 7.90.0,
  zod 4.6.7, @hookform/resolvers 5.9.2, lucide-react, date-fns (locale es).
- Dependencias fijadas con version exacta y `package-lock.json` versionado.
  No agregues dependencias nuevas sin confirmacion.

## Estructura

```
src/
  api/            cliente HTTP, errores, sesion, tipos generados y helpers
  components/     UI reutilizable (ui/ = shadcn), layout y estados
  features/       modulos por dominio (auth/)
  lib/            utilidades sin estado (cn, iniciales, fechas)
  pages/          pantallas de la base
  test/           setup de Vitest
scripts/          generacion de tipos OpenAPI
```

- Nombres de componentes y funciones en espanol; infraestructura en ingles solo
  cuando lo exige una libreria. Identificadores en ASCII, sin tildes.
- Un componente por archivo. Solo logica de presentacion en `pages/` y `components/`.
- No dupliques reglas de negocio del backend: el frontend solo refleja el contrato.
- No modifiques `app/` (backend) ni `hotel_front/` (Flutter). Fuera de `hotel_web/`
  solo se tocan `.dockerignore`, `.gitignore` y `.github/workflows/`.

## Variables de entorno

- `VITE_API_URL` (default `http://localhost:8000`). Copia `.env.example` a `.env`.
- El token de acceso vive en memoria; el refresh token en `localStorage`
  (`hotel_web.refreshToken`). No guardes tokens en otros lugares.

## Tipos de la API

`python -m app.export_openapi` escribe `openapi.json` en la raiz. El script lo
restaura (o lo elimina si no existia) despues de leerlo, para no ensuciar el
arbol de trabajo.

```bash
npm run api:types           # exporta openapi.json y genera src/api/schema.d.ts
npm run api:types -- --remoto   # usa http://localhost:8000/openapi.json
```

El script usa `.venv` del backend si existe; si no, `python` del PATH. Requiere
las dependencias de Python del backend. Regenera y revisa `src/api/schema.d.ts`
cuando cambie el contrato; no lo edites a mano.

## Comandos

```bash
npm ci
npm run dev
npm run lint
npm run typecheck
npm test
npm run build
```

Los cuatro ultimos deben pasar antes de cerrar una tarea. Tests con Vitest +
Testing Library (jsdom); mockea `fetch`, no llames al backend real.

## Tema y accesibilidad

- Paleta Midnight + Champagne Gold con tokens HSL en `src/index.css`
  (`:root` y `.dark`). No uses colores sueltos en componentes.
- Contraste verificado (WCAG AA >= 4.5:1):
  - Claro: texto/fondo 16.57:1, muted/fondo 6.07:1, boton primario 6.13:1.
  - Oscuro: texto/fondo 16.84:1, muted/fondo 8.65:1, primario/fondo 9.05:1.
- Todo control interactivo conserva foco visible (`focus-visible:ring`), labels
  asociados y textos alternativos en iconos.

## Reglas de esta base

- No implementar modulos de negocio todavia: las rutas muestran estados de
  "en preparacion" hasta la tarea correspondiente.
- Rutas protegidas: sin sesion redirige a `/login`; Usuarios y Auditoria exigen
  rol `ADMIN`.
- Un unico refresh compartido ante 401 concurrentes y un solo reintento. Si el
  refresh falla, se limpia la sesion y se redirige al login.
