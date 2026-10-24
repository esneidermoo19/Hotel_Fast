import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...entradas: ClassValue[]): string {
  return twMerge(clsx(entradas));
}

export function iniciales(nombre: string): string {
  const partes = nombre.trim().split(/\s+/).filter(Boolean);

  if (partes.length === 0) {
    return "?";
  }

  if (partes.length === 1) {
    return partes[0].charAt(0).toUpperCase();
  }

  const primera = partes[0].charAt(0);
  const ultima = partes[partes.length - 1].charAt(0);
  return `${primera}${ultima}`.toUpperCase();
}
