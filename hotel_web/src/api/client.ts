import { construirUrlApi } from "./config";
import { ApiError, mapearError } from "./errors";
import {
  notificarExpiracionSesion,
  obtenerAccessToken,
  renovarSesion,
} from "./session";

const TIEMPO_LIMITE_MS = 15_000;

export interface OpcionesSolicitud extends Omit<RequestInit, "signal"> {
  autenticada?: boolean;
  reintentar?: boolean;
}

export async function solicitar<T>(
  ruta: string,
  opciones: OpcionesSolicitud = {},
): Promise<T> {
  const {
    autenticada = true,
    reintentar = true,
    headers,
    ...resto
  } = opciones;

  const controlador = new AbortController();
  const temporizador = setTimeout(
    () => controlador.abort(),
    TIEMPO_LIMITE_MS,
  );

  const headersFinales = new Headers(headers);
  if (!headersFinales.has("Accept")) {
    headersFinales.set("Accept", "application/json");
  }
  const esFormData =
    typeof FormData !== "undefined" && resto.body instanceof FormData;
  if (resto.body != null && !esFormData && !headersFinales.has("Content-Type")) {
    headersFinales.set("Content-Type", "application/json");
  }
  const token = obtenerAccessToken();
  if (autenticada && token && !headersFinales.has("Authorization")) {
    headersFinales.set("Authorization", `Bearer ${token}`);
  }

  try {
    const respuesta = await fetch(construirUrlApi(ruta), {
      ...resto,
      headers: headersFinales,
      signal: controlador.signal,
    });

    if (respuesta.status === 401 && autenticada && reintentar) {
      const renovado = await renovarSesion();
      if (renovado) {
        return solicitar<T>(ruta, { ...opciones, reintentar: false });
      }
      notificarExpiracionSesion();
    }

    if (!respuesta.ok) {
      throw await mapearError(respuesta);
    }

    if (respuesta.status === 204) {
      return undefined as T;
    }

    return (await respuesta.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(
        "El servidor tardo demasiado en responder.",
        "TIEMPO_AGOTADO",
        0,
      );
    }
    throw new ApiError(
      "No se pudo conectar con el servidor.",
      "RED",
      0,
    );
  } finally {
    clearTimeout(temporizador);
  }
}
