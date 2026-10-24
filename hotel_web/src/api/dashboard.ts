import { solicitar } from "./client";
import type { DashboardRead } from "./tipos";

export function obtenerResumenDashboard(): Promise<DashboardRead> {
  return solicitar<DashboardRead>("/api/dashboard");
}
