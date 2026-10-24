import { solicitar } from "./client";
import type { components } from "./schema";

export type Huesped = components["schemas"]["HuespedRead"];
export type DatosHuesped = components["schemas"]["HuespedCreate"];
export type TipoDocumento = components["schemas"]["TipoDocumento"];
export type PaginaHuespedes = components["schemas"]["Pagina_HuespedRead_"];

export interface FiltrosHuespedes {
  q?: string;
  pagina: number;
  tamano: number;
}

export function listarHuespedes({ q, pagina, tamano }: FiltrosHuespedes) {
  const parametros = new URLSearchParams({
    pagina: String(pagina),
    tamano: String(tamano),
  });
  if (q?.trim()) {
    parametros.set("q", q.trim());
  }
  return solicitar<PaginaHuespedes>(`/api/huespedes?${parametros.toString()}`);
}

export function crearHuesped(datos: DatosHuesped) {
  return solicitar<Huesped>("/api/huespedes", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export function actualizarHuesped(id: number, datos: DatosHuesped) {
  return solicitar<Huesped>(`/api/huespedes/${id}`, {
    method: "PUT",
    body: JSON.stringify(datos),
  });
}
