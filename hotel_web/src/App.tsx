import { Navigate, Route, Routes } from "react-router";

import { AppShell } from "@/components/layout/AppShell";
import {
  RutaConRoles,
  RutaProtegida,
  RutaPublica,
} from "@/components/layout/RouteGuards";
import { LoginPage } from "@/features/auth/LoginPage";
import { AuditoriaPage } from "@/features/auditoria/AuditoriaPage";
import { HabitacionesPage } from "@/features/habitaciones/HabitacionesPage";
import { HuespedesPage } from "@/features/huespedes/HuespedesPage";
import { ReservasPage } from "@/features/reservas/ReservasPage";
import { UsuariosPage } from "@/features/usuarios/UsuariosPage";
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
          <Route path="habitaciones" element={<HabitacionesPage />} />
          <Route path="huespedes" element={<HuespedesPage />} />
          <Route path="reservas" element={<ReservasPage />} />
          <Route element={<RutaConRoles roles={["ADMIN"]} />}>
            <Route path="usuarios" element={<UsuariosPage />} />
            <Route path="auditoria" element={<AuditoriaPage />} />
          </Route>
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
