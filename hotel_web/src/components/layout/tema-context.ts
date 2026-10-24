import { createContext, useContext } from "react";

export type Tema = "claro" | "oscuro" | "sistema";

export interface ContextoTema {
  tema: Tema;
  oscuro: boolean;
  alternarTema: () => void;
}

export const TemaContext = createContext<ContextoTema | null>(null);

export function useTema(): ContextoTema {
  const contexto = useContext(TemaContext);
  if (!contexto) {
    throw new Error("useTema debe usarse dentro de TemaProvider");
  }
  return contexto;
}
