export const API_URL = (
  import.meta.env.VITE_API_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

export function construirUrlApi(ruta: string): string {
  const normalizada = ruta.startsWith("/") ? ruta : `/${ruta}`;
  return `${API_URL}${normalizada}`;
}
