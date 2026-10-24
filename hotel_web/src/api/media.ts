import { API_URL } from "./config";

export function resolverUrlMedia(
  url: string | null | undefined,
): string | null {
  if (!url) {
    return null;
  }

  const limpia = url.trim();
  if (!limpia) {
    return null;
  }

  if (/^(https?:|data:|blob:)/i.test(limpia)) {
    return limpia;
  }

  return `${API_URL}${limpia.startsWith("/") ? "" : "/"}${limpia}`;
}
