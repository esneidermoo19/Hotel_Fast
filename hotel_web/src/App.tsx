import {
  BedDouble,
  CalendarDays,
  ScrollText,
  ShieldCheck,
  Users,
} from "lucide-react";
import { Navigate, Route, Routes } from "react-router";

import { AppShell } from "@/components/layout/AppShell";
import {
  RutaConRoles,
  RutaProtegida,
  RutaPublica,
} from "@/components/layout/RouteGuards";
import { LoginPage } from "@/features/auth/LoginPage";
import { ModuloPendientePage } from "@/pages/ModuloPendientePage";
import { PanelPage } from "@/pages/PanelPage";

export default function App() {
  return (
    <Routes>
      <Route element={<RutaPublica />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      <Route element={<RutaProtegida />}>
        <Route element={<AppShell />}>
          <Route index element={<PanelPage />} />
          <Route
            path="habitaciones"
            element={
              <ModuloPendientePage
                titulo="Habitaciones"
                descripcion="Consulta y administracion del inventario de habitaciones."
                icono={BedDouble}
              />
            }
          />
          <Route
            path="huespedes"
            element={
              <ModuloPendientePage
                titulo="Huespedes"
                descripcion="Registro y consulta de los huespedes del hotel."
                icono={Users}
              />
            }
          />
          <Route
            path="reservas"
            element={
              <ModuloPendientePage
                titulo="Reservas"
                descripcion="Gestion de reservas, llegadas y salidas."
                icono={CalendarDays}
              />
            }
          />

          <Route element={<RutaConRoles roles={["ADMIN"]} />}>
            <Route
              path="usuarios"
              element={
                <ModuloPendientePage
                  titulo="Usuarios"
                  descripcion="Administracion de cuentas y roles del personal."
                  icono={ShieldCheck}
                />
              }
            />
            <Route
              path="auditoria"
              element={
                <ModuloPendientePage
                  titulo="Auditoria"
                  descripcion="Consulta del historial de acciones del sistema."
                  icono={ScrollText}
                />
              }
            />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
