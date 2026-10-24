import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { limpiarSesion } from "@/api/session";

import { AuthProvider } from "./AuthProvider";
import { LoginPage } from "./LoginPage";

const fetchMock = vi.fn<typeof fetch>();

function respuestaJson(cuerpo: unknown, status = 200): Response {
  return new Response(JSON.stringify(cuerpo), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<h1>Panel</h1>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
  limpiarSesion();
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("flujo de login", () => {
  it("inicia sesion, guarda el refresh y navega al panel", async () => {
    const usuario = userEvent.setup();

    fetchMock.mockResolvedValueOnce(
      respuestaJson({
        token: "access-token",
        refreshToken: "refresh-token",
        tokenType: "bearer",
        expiresIn: 1800,
        id: 1,
        username: "admin",
        email: "admin@hotel.com",
        nombre: "Ana Perez",
        role: "ADMIN",
      }),
    );

    renderLogin();

    await usuario.type(
      screen.getByLabelText("Usuario o correo"),
      "admin",
    );
    await usuario.type(screen.getByLabelText("Contrasena"), "secreta123");

    await usuario.click(
      screen.getByRole("button", { name: "Mostrar contrasena" }),
    );
    expect(screen.getByLabelText("Contrasena")).toHaveAttribute(
      "type",
      "text",
    );

    await usuario.click(
      screen.getByRole("button", { name: "Iniciar sesion" }),
    );

    expect(
      await screen.findByRole("heading", { name: "Panel" }),
    ).toBeInTheDocument();
    expect(localStorage.getItem("hotel_web.refreshToken")).toBe(
      "refresh-token",
    );

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, opciones] = fetchMock.mock.calls[0];
    expect(String(url)).toContain("/api/auth/login");
    expect(opciones?.method).toBe("POST");
    expect(opciones?.body).toBe(
      JSON.stringify({ username: "admin", password: "secreta123" }),
    );
  });

  it("muestra un mensaje de error cuando las credenciales son invalidas", async () => {
    const usuario = userEvent.setup();

    fetchMock.mockResolvedValueOnce(
      respuestaJson(
        { detail: "Credenciales incorrectas", code: "NO_AUTORIZADO" },
        401,
      ),
    );

    renderLogin();

    await usuario.type(
      screen.getByLabelText("Usuario o correo"),
      "admin@hotel.com",
    );
    await usuario.type(screen.getByLabelText("Contrasena"), "mala");
    await usuario.click(
      screen.getByRole("button", { name: "Iniciar sesion" }),
    );

    expect(
      await screen.findByText("Usuario o contrasena incorrectos."),
    ).toBeInTheDocument();
    expect(localStorage.getItem("hotel_web.refreshToken")).toBeNull();
  });
});
