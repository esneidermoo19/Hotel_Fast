import type { LucideIcon } from "lucide-react";

import { EstadoVacio } from "@/components/estados/EstadoVacio";

export interface ModuloPendientePageProps {
  titulo: string;
  descripcion: string;
  icono: LucideIcon;
}

export function ModuloPendientePage({
  titulo,
  descripcion,
  icono,
}: ModuloPendientePageProps) {
  return (
    <div className="animate-fade-in space-y-6">
      <header>
        <h2 className="font-display text-2xl text-foreground sm:text-3xl">
          {titulo}
        </h2>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          {descripcion}
        </p>
      </header>

      <EstadoVacio
        icono={icono}
        titulo={`${titulo} en preparacion`}
        descripcion="La base de navegacion, sesion y cliente HTTP esta lista. Este modulo se implementara en una tarea posterior."
      />
    </div>
  );
}
