import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

export interface EstadoCargaProps {
  mensaje?: string;
  className?: string;
}

export function EstadoCarga({
  mensaje = "Cargando...",
  className,
}: EstadoCargaProps) {
  return (
    <div
      role="status"
      className={cn(
        "flex items-center justify-center gap-3 py-10 text-sm text-muted-foreground",
        className,
      )}
    >
      <Loader2 className="h-5 w-5 animate-spin text-primary" aria-hidden />
      <span>{mensaje}</span>
    </div>
  );
}
