import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { TemaContext, type Tema } from "./tema-context";

const CLAVE_TEMA = "hotel_web.tema";

function leerTemaGuardado(): Tema {
  try {
    const guardado = localStorage.getItem(CLAVE_TEMA);
    if (guardado === "claro" || guardado === "oscuro" || guardado === "sistema") {
      return guardado;
    }
  } catch {
    void 0;
  }
  return "sistema";
}

function prefiereOscuro(): boolean {
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export function TemaProvider({ children }: { children: ReactNode }) {
  const [tema, setTema] = useState<Tema>(leerTemaGuardado);
  const [sistemaOscuro, setSistemaOscuro] = useState(prefiereOscuro);

  useEffect(() => {
    const consulta = window.matchMedia("(prefers-color-scheme: dark)");
    const alCambiar = (evento: MediaQueryListEvent) => {
      setSistemaOscuro(evento.matches);
    };
    consulta.addEventListener("change", alCambiar);
    return () => consulta.removeEventListener("change", alCambiar);
  }, []);

  const oscuro = tema === "oscuro" || (tema === "sistema" && sistemaOscuro);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", oscuro);
    try {
      localStorage.setItem(CLAVE_TEMA, tema);
    } catch {
      void 0;
    }
  }, [oscuro, tema]);

  const alternarTema = useCallback(() => {
    setTema(oscuro ? "claro" : "oscuro");
  }, [oscuro]);

  const valor = useMemo(
    () => ({ tema, oscuro, alternarTema }),
    [tema, oscuro, alternarTema],
  );

  return (
    <TemaContext.Provider value={valor}>{children}</TemaContext.Provider>
  );
}
