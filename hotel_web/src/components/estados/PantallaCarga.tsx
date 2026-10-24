import { EstadoCarga } from "./EstadoCarga";

export function PantallaCarga() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <EstadoCarga mensaje="Verificando sesion..." />
    </div>
  );
}
