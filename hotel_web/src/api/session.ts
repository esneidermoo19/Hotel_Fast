import { construirUrlApi } from "./config";
import type { TokenPair } from "./tipos";

const CLAVE_REFRESH = "hotel_web.refreshToken";
const TIEMPO_LIMITE_MS = 15_000;

let accessToken: string | null = null;
let refreshToken: string | null = null;
let refrescoEnCurso: Promise<boolean> | null = null;
let alExpirarSesion: (() => void) | null = null;
let expiracionNotificada = false;

function leerRefreshGuardado(): string | null {
  try {
    return localStorage.getItem(CLAVE_REFRESH);
  } catch {
    return null;
  }
}

export function obtenerAccessToken(): string | null {
  return accessToken;
}

export function obtenerRefreshToken(): string | null {
  if (refreshToken === null) {
    refreshToken = leerRefreshGuardado();
  }
  return refreshToken;
}

export function guardarTokens(token: string, nuevoRefreshToken: string): void {
  accessToken = token;
  refreshToken = nuevoRefreshToken;
  expiracionNotificada = false;
  try {
    localStorage.setItem(CLAVE_REFRESH, nuevoRefreshToken);
  } catch {
    void 0;
  }
}

export function limpiarSesion(): void {
  accessToken = null;
  refreshToken = null;
  try {
    localStorage.removeItem(CLAVE_REFRESH);
  } catch {
    void 0;
  }
}

export function establecerManejadorExpiracion(
  manejador: (() => void) | null,
): void {
  alExpirarSesion = manejador;
}

export function notificarExpiracionSesion(): void {
  if (expiracionNotificada) {
    return;
  }
  expiracionNotificada = true;
  alExpirarSesion?.();
}

async function ejecutarRefresco(): Promise<boolean> {
  const actual = obtenerRefreshToken();

  if (!actual) {
    return false;
  }

  const controlador = new AbortController();
  const temporizador = setTimeout(
    () => controlador.abort(),
    TIEMPO_LIMITE_MS,
  );

  try {
    const respuesta = await fetch(construirUrlApi("/api/auth/refresh"), {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refreshToken: actual }),
      signal: controlador.signal,
    });

    if (!respuesta.ok) {
      limpiarSesion();
      return false;
    }

    const datos = (await respuesta.json()) as TokenPair;
    guardarTokens(datos.token, datos.refreshToken);
    return true;
  } catch {
    limpiarSesion();
    return false;
  } finally {
    clearTimeout(temporizador);
  }
}

export function renovarSesion(): Promise<boolean> {
  if (refrescoEnCurso) {
    return refrescoEnCurso;
  }

  refrescoEnCurso = ejecutarRefresco().finally(() => {
    refrescoEnCurso = null;
  });

  return refrescoEnCurso;
}
