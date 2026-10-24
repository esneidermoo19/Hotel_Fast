import { solicitar } from "./client";
import type { components } from "./schema";
export type Habitacion = components["schemas"]["HabitacionRead"];
export type DatosHabitacion = components["schemas"]["HabitacionCreate"];
export type EstadoHabitacion = components["schemas"]["EstadoHabitacion"];
export type EstadoLimpieza = components["schemas"]["EstadoLimpieza"];
export type TipoHabitacion = components["schemas"]["TipoHabitacion"];
export function listarHabitaciones() { return solicitar<Habitacion[]>("/api/habitaciones"); }
export function crearHabitacion(datos: DatosHabitacion) { return solicitar<Habitacion>("/api/habitaciones", { method: "POST", body: JSON.stringify(datos) }); }
export function actualizarHabitacion(id: number, datos: DatosHabitacion) { return solicitar<Habitacion>(`/api/habitaciones/${id}`, { method: "PUT", body: JSON.stringify(datos) }); }
export function actualizarEstadoHabitacion(id: number, estado: EstadoHabitacion) { return solicitar<Habitacion>(`/api/habitaciones/${id}/estado`, { method: "PATCH", body: JSON.stringify({ estado }) }); }
export function actualizarLimpiezaHabitacion(id: number, limpieza: EstadoLimpieza) { return solicitar<Habitacion>(`/api/habitaciones/${id}/limpieza`, { method: "PATCH", body: JSON.stringify({ limpieza }) }); }
