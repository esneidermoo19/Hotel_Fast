import { solicitar } from "./client";
import type { components } from "./schema";
export type EventoAuditoria = components["schemas"]["AuditoriaRead"];
export type PaginaAuditoria = components["schemas"]["Pagina_AuditoriaRead_"];
export interface FiltrosAuditoria { entidad?:string; accion?:string; desde?:string; hasta?:string; pagina:number; }
export function listarAuditoria(f:FiltrosAuditoria) { const p=new URLSearchParams({pagina:String(f.pagina),tamano:"20"}); for(const k of ["entidad","accion","desde","hasta"] as const) if(f[k])p.set(k,f[k]!); return solicitar<PaginaAuditoria>(`/api/auditoria?${p}`); }
