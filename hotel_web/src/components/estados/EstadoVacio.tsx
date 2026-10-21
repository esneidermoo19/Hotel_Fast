import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

export interface EstadoVacioProps {
  titulo: string;
  descripcion?: string;
  icono?: LucideIcon;
  className?: string;
}

export function EstadoVacio({
  titulo,
  descripcion,
  icono: Icono,
  className,
}: EstadoVacioProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-card/60 px-6 py-14 text-center",
        className,
      )}
    >
      {Icono ? (
        <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Icono className="h-6 w-6" aria-hidden />
        </span>
      ) : null}
      <h3 className="text-base font-semibold">{titulo}</h3>
      {descripcion ? (
        <p className="mt-2 max-w-md text-sm text-muted-foreground">
          {descripcion}
        </p>
      ) : null}
    </div>
  );
}
