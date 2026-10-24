import { solicitar } from "./client";
import type { components } from "./schema";
export type UsuarioAdmin = components["schemas"]["UsuarioRead"];
export type CrearUsuario = components["schemas"]["UsuarioCrear"];
export type ActualizarUsuario = components["schemas"]["UsuarioActualizar"];
export type RolUsuario = components["schemas"]["RolUsuario"];
export type PaginaUsuarios = components["schemas"]["Pagina_UsuarioRead_"];
export function listarUsuarios(q:string,pagina:number) { const p=new URLSearchParams({pagina:String(pagina),tamano:"10",soloActivos:"false"}); if(q.trim())p.set("q",q.trim()); return solicitar<PaginaUsuarios>(`/api/usuarios?${p}`); }
export function crearUsuario(datos:CrearUsuario) { return solicitar<UsuarioAdmin>("/api/usuarios",{method:"POST",body:JSON.stringify(datos)}); }
export function actualizarUsuario(id:number,datos:ActualizarUsuario) { return solicitar<UsuarioAdmin>(`/api/usuarios/${id}`,{method:"PUT",body:JSON.stringify(datos)}); }
export function cambiarActivoUsuario(id:number,activo:boolean) { return solicitar<UsuarioAdmin>(`/api/usuarios/${id}/${activo?"reactivar":"desactivar"}`,{method:"POST"}); }
