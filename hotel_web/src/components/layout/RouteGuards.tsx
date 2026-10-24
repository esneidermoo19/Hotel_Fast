import { Navigate, Outlet, useLocation } from "react-router";

import type { Rol } from "@/api/tipos";
import { PantallaCarga } from "@/components/estados/PantallaCarga";
import { useAuth } from "@/features/auth/auth-context";

export function RutaProtegida() {
  const { autenticado, cargando } = useAuth();
  const ubicacion = useLocation();

  if (cargando) {
    return <PantallaCarga />;
  }

  if (!autenticado) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ desde: `${ubicacion.pathname}${ubicacion.search}` }}
      />
    );
  }

  return <Outlet />;
}

export function RutaPublica() {
  const { autenticado, cargando } = useAuth();

  if (cargando) {
    return <PantallaCarga />;
  }

  if (autenticado) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}

export function RutaConRoles({ roles }: { roles: Rol[] }) {
  const { usuario, cargando } = useAuth();

  if (cargando) {
    return <PantallaCarga />;
  }

  if (!usuario) {
    return <Navigate to="/login" replace />;
  }

  if (!roles.includes(usuario.role)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
