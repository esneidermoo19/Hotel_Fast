import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { solicitar } from "./client";
import { ApiError } from "./errors";
import {
  establecerManejadorExpiracion,
  guardarTokens,
  limpiarSesion,
  obtenerRefreshToken,
} from "./session";

const fetchMock = vi.fn<typeof fetch>();

function respuestaJson(cuerpo: unknown, status = 200): Response {
  return new Response(JSON.stringify(cuerpo), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function urlDe(entrada: RequestInfo | URL): string {
  if (typeof entrada === "string") {
    return entrada;
  }
  if (entrada instanceof URL) {
    return entrada.toString();
  }
  return entrada.url;
}

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
  limpiarSesion();
  localStorage.clear();
  establecerManejadorExpiracion(null);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("cliente HTTP", () => {
  it("mapea el sobre de error a ApiError con mensaje en espanol", async () => {
    fetchMock.mockResolvedValueOnce(
      respuestaJson(
        { detail: "No existe", code: "NO_ENCONTRADO" },
        404,
      ),
    );

    const error = await solicitar("/api/huespedes/99").catch(
      (fallo: unknown) => fallo,
    );

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({
      code: "NO_ENCONTRADO",
      status: 404,
      message: "No se encontro el recurso solicitado.",
    });
  });

  it("renueva una sola vez ante 401 concurrentes y reintenta", async () => {
    let llamadasRefresh = 0;

    fetchMock.mockImplementation(async (entrada, opciones) => {
      const url = urlDe(entrada);

      if (url.endsWith("/api/auth/refresh")) {
        llamadasRefresh += 1;
        return respuestaJson({
          token: "token-nuevo",
          refreshToken: "refresh-nuevo",
          tokenType: "bearer",
          expiresIn: 1800,
        });
      }

      const headers = new Headers(opciones?.headers);
      if (headers.get("Authorization") === "Bearer token-nuevo") {
        return respuestaJson({ ok: true });
      }

      return respuestaJson(
        { detail: "Token invalido", code: "TOKEN_INVALIDO" },
        401,
      );
    });

    guardarTokens("token-viejo", "refresh-viejo");

    const [primera, segunda] = await Promise.all([
      solicitar<{ ok: boolean }>("/api/huespedes"),
      solicitar<{ ok: boolean }>("/api/reservas"),
    ]);

    expect(llamadasRefresh).toBe(1);
    expect(primera).toEqual({ ok: true });
    expect(segunda).toEqual({ ok: true });
    expect(obtenerRefreshToken()).toBe("refresh-nuevo");
  });

  it("cierra la sesion y notifica cuando el refresh falla", async () => {
    const alExpirar = vi.fn();
    establecerManejadorExpiracion(alExpirar);

    fetchMock.mockImplementation(async (entrada) => {
      const url = urlDe(entrada);

      if (url.endsWith("/api/auth/refresh")) {
        return respuestaJson(
          { detail: "Refresh invalido", code: "REFRESH_TOKEN_INVALIDO" },
          401,
        );
      }

      return respuestaJson(
        { detail: "Token invalido", code: "TOKEN_INVALIDO" },
        401,
      );
    });

    guardarTokens("token-viejo", "refresh-viejo");

    await expect(solicitar("/api/huespedes")).rejects.toBeInstanceOf(ApiError);
    expect(alExpirar).toHaveBeenCalledTimes(1);
    expect(obtenerRefreshToken()).toBeNull();
  });
});
