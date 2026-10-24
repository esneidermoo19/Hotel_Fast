import { LayoutDashboard } from "lucide-react";

import { EstadoVacio } from "@/components/estados/EstadoVacio";
import { formatearFecha } from "@/lib/fechas";

export function PanelPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[0.16em] text-primary">
          {formatearFecha(new Date().toISOString())}
        </p>
        <h2 className="mt-2 font-display text-2xl text-foreground sm:text-3xl">
          Bienvenido a Hotel Fast
        </h2>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          La base del frontend web ya esta conectada al API. Desde aqui se
          organizaran la operacion diaria y los indicadores del hotel.
        </p>
      </header>

      <EstadoVacio
        icono={LayoutDashboard}
        titulo="Panel en preparacion"
        descripcion="Los indicadores y accesos rapidos se implementaran en una tarea posterior. Mientras tanto, usa el menu para recorrer los modulos disponibles."
      />
    </div>
  );
}
