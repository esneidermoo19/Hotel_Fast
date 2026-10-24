import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useNavigate } from "react-router";

import {
  cambiarContrasena,
  cerrarSesion,
  iniciarSesion,
  obtenerPerfil,
  type Credenciales,
} from "@/api/auth";
import {
  guardarTokens,
  limpiarSesion,
  obtenerRefreshToken,
  renovarSesion,
  establecerManejadorExpiracion,
} from "@/api/session";
import type { UsuarioSesion } from "@/api/tipos";

import { AuthContext } from "./auth-context";

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [usuario, setUsuario] = useState<UsuarioSesion | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    let activo = true;

    const restaurar = async () => {
      if (!obtenerRefreshToken()) {
        if (activo) {
          setCargando(false);
        }
        return;
      }

      const renovado = await renovarSesion();
      if (!renovado) {
        if (activo) {
          setCargando(false);
        }
        return;
      }

      try {
        const perfil = await obtenerPerfil();
        if (activo) {
          setUsuario(perfil);
        }
      } catch {
        limpiarSesion();
      } finally {
        if (activo) {
          setCargando(false);
        }
      }
    };

    void restaurar();

    return () => {
      activo = false;
    };
  }, []);

  useEffect(() => {
    establecerManejadorExpiracion(() => {
      setUsuario(null);
      navigate("/login", { replace: true });
    });

    return () => establecerManejadorExpiracion(null);
  }, [navigate]);

  const login = useCallback(async (credenciales: Credenciales) => {
    const respuesta = await iniciarSesion(credenciales);
    guardarTokens(respuesta.token, respuesta.refreshToken);
    setUsuario({
      id: respuesta.id,
      username: respuesta.username,
      email: respuesta.email,
      nombre: respuesta.nombre,
      role: respuesta.role,
    });
  }, []);

  const logout = useCallback(async () => {
    const actual = obtenerRefreshToken();
    try {
      if (actual) {
        await cerrarSesion(actual);
      }
    } finally {
      limpiarSesion();
      setUsuario(null);
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  const cambiarPassword = useCallback(
    async (actual: string, nueva: string) => {
      const respuesta = await cambiarContrasena(actual, nueva);
      limpiarSesion();
      setUsuario(null);
      navigate("/login", { replace: true });
      return respuesta.mensaje;
    },
    [navigate],
  );

  const valor = useMemo(
    () => ({
      usuario,
      cargando,
      autenticado: usuario !== null,
      login,
      logout,
      cambiarPassword,
    }),
    [usuario, cargando, login, logout, cambiarPassword],
  );

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}
