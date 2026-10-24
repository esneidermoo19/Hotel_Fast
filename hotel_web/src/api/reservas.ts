import { solicitar } from "./client";
import type { components } from "./schema";
export type Reserva = components["schemas"]["ReservaRead"];
export type DatosReserva = components["schemas"]["ReservaCreate"];
export type EstadoReserva = components["schemas"]["EstadoReserva"];
export type PaginaReservas = components["schemas"]["Pagina_ReservaRead_"];
export function listarReservas(pagina:number, estado?:EstadoReserva) { const p=new URLSearchParams({pagina:String(pagina),tamano:"10"}); if(estado)p.set("estado",estado); return solicitar<PaginaReservas>(`/api/reservas?${p}`); }
export function crearReserva(datos:DatosReserva) { return solicitar<Reserva>("/api/reservas",{method:"POST",body:JSON.stringify(datos)}); }
export function actuarReserva(id:number, accion:"confirmar"|"cancelar"|"no-show"|"check-in"|"check-out", motivo?:string) { return solicitar<unknown>(`/api/reservas/${id}/${accion}`,{method:"POST",...(motivo?{body:JSON.stringify({motivo})}:{})}); }
