import { AlertTriangle } from "lucide-react";

import { Boton } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface EstadoErrorProps {
  titulo?: string;
  mensaje: string;
  onReintentar?: () => void;
  className?: string;
}

export function EstadoError({
  titulo = "Ocurrio un problema",
  mensaje,
  onReintentar,
  className,
}: EstadoErrorProps) {
  return (
    <div
      role="alert"
      className={cn(
        "flex flex-col items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm sm:flex-row sm:items-center sm:justify-between",
        className,
      )}
    >
      <div className="flex items-start gap-3">
        <AlertTriangle
          className="mt-0.5 h-5 w-5 shrink-0 text-destructive"
          aria-hidden
        />
        <div>
          <p className="font-medium text-foreground">{titulo}</p>
          <p className="mt-0.5 text-muted-foreground">{mensaje}</p>
        </div>
      </div>
      {onReintentar ? (
        <Boton variant="outline" size="sm" onClick={onReintentar}>
          Reintentar
        </Boton>
      ) : null}
    </div>
  );
}
