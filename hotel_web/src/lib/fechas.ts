import { format, parseISO } from "date-fns";
import { es } from "date-fns/locale";

export function formatearFecha(iso: string): string {
  return format(parseISO(iso), "d 'de' MMMM 'de' yyyy", { locale: es });
}

export function formatearFechaHora(iso: string): string {
  return format(parseISO(iso), "d MMM yyyy, HH:mm", { locale: es });
}
