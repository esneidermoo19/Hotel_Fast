import { solicitar } from "./client";
import type { LoginResponse, Usuario } from "./tipos";

export interface Credenciales {
  username?: string;
  email?: string;
  password: string;
}

export function iniciarSesion(
  credenciales: Credenciales,
): Promise<LoginResponse> {
  return solicitar<LoginResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(credenciales),
    autenticada: false,
  });
}

export function cerrarSesion(refreshToken: string): Promise<void> {
  return solicitar<void>("/api/auth/logout", {
    method: "POST",
    body: JSON.stringify({ refreshToken }),
    autenticada: false,
  });
}

export function obtenerPerfil(): Promise<Usuario> {
  return solicitar<Usuario>("/api/auth/me");
}

export function cambiarContrasena(
  passwordActual: string,
  passwordNuevo: string,
): Promise<{ mensaje: string }> {
  return solicitar<{ mensaje: string }>("/api/auth/cambiar-password", {
    method: "POST",
    body: JSON.stringify({ passwordActual, passwordNuevo }),
  });
}
