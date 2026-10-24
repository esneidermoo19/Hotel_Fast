import type { HTMLAttributes } from "react";

import { cn, iniciales } from "@/lib/utils";

export interface AvatarProps extends HTMLAttributes<HTMLSpanElement> {
  nombre: string;
}

export function Avatar({ nombre, className, ...props }: AvatarProps) {
  return (
    <span
      className={cn(
        "flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-primary/30 bg-primary/10 text-sm font-semibold text-primary",
        className,
      )}
      title={nombre.trim() || "Usuario"}
      aria-label={nombre.trim() || "Usuario"}
      {...props}
    >
      {iniciales(nombre)}
    </span>
  );
}
