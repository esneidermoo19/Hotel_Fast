import type { components } from "./schema";

export type LoginResponse = components["schemas"]["LoginResponse"];
export type TokenPair = components["schemas"]["TokenPair"];
export type Usuario = components["schemas"]["UsuarioRead"];
export type UsuarioSesion = Pick<
  Usuario,
  "id" | "username" | "email" | "nombre" | "role"
>;
export type Rol = Usuario["role"];
