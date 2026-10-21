import { createContext, useContext } from "react";

import type { Credenciales } from "@/api/auth";
import type { UsuarioSesion } from "@/api/tipos";

export interface ContextoAuth {
  usuario: UsuarioSesion | null;
  cargando: boolean;
  autenticado: boolean;
  login: (credenciales: Credenciales) => Promise<void>;
  logout: () => Promise<void>;
  cambiarPassword: (actual: string, nueva: string) => Promise<string>;
}

export const AuthContext = createContext<ContextoAuth | null>(null);

export function useAuth(): ContextoAuth {
  const contexto = useContext(AuthContext);
  if (!contexto) {
    throw new Error("useAuth debe usarse dentro de AuthProvider");
  }
  return contexto;
}
