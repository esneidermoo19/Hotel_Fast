import { describe, expect, it } from "vitest";

import { resolverUrlMedia } from "./media";

describe("resolverUrlMedia", () => {
  it("resuelve rutas relativas contra la base de la API", () => {
    expect(resolverUrlMedia("/media/habitacion.jpg")).toBe(
      "http://localhost:8000/media/habitacion.jpg",
    );
    expect(resolverUrlMedia("media/habitacion.jpg")).toBe(
      "http://localhost:8000/media/habitacion.jpg",
    );
  });

  it("respeta URLs absolutas y devuelve null para vacios", () => {
    expect(resolverUrlMedia("https://cdn.hotel.com/foto.jpg")).toBe(
      "https://cdn.hotel.com/foto.jpg",
    );
    expect(resolverUrlMedia(null)).toBeNull();
    expect(resolverUrlMedia("   ")).toBeNull();
  });
});
