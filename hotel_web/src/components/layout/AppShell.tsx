import { useState, type ReactNode } from "react";
import {
  BedDouble,
  CalendarDays,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  ScrollText,
  ShieldCheck,
  Sun,
  Users,
  X,
  type LucideIcon,
} from "lucide-react";
import { NavLink, Outlet, useLocation } from "react-router";

import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Boton } from "@/components/ui/button";
import { useAuth } from "@/features/auth/auth-context";
import { cn } from "@/lib/utils";

import { useTema } from "./tema-context";

interface ItemNavegacion {
  to: string;
  label: string;
  icon: LucideIcon;
  soloAdmin?: boolean;
}

const NAVEGACION: ItemNavegacion[] = [
  { to: "/", label: "Panel", icon: LayoutDashboard },
  { to: "/habitaciones", label: "Habitaciones", icon: BedDouble },
  { to: "/huespedes", label: "Huespedes", icon: Users },
  { to: "/reservas", label: "Reservas", icon: CalendarDays },
  { to: "/usuarios", label: "Usuarios", icon: ShieldCheck, soloAdmin: true },
  { to: "/auditoria", label: "Auditoria", icon: ScrollText, soloAdmin: true },
];

function Marca() {
  return (
    <div className="flex items-center gap-3 px-4 py-5">
      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-sm font-bold text-primary-foreground">
        HF
      </span>
      <div>
        <p className="font-display text-lg leading-none text-foreground">
          Hotel Fast
        </p>
        <p className="mt-1 text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
          Gestion hotelera
        </p>
      </div>
    </div>
  );
}

function Navegacion({
  items,
  onNavegar,
}: {
  items: ItemNavegacion[];
  onNavegar?: () => void;
}) {
  return (
    <nav className="space-y-1 px-3 py-3" aria-label="Navegacion principal">
      {items.map((item) => {
        const Icono = item.icon;
        return (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            onClick={onNavegar}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )
            }
          >
            <Icono className="h-4 w-4" aria-hidden />
            <span>{item.label}</span>
          </NavLink>
        );
      })}
    </nav>
  );
}

function ContenidoMenu({
  items,
  children,
  onNavegar,
}: {
  items: ItemNavegacion[];
  children?: ReactNode;
  onNavegar?: () => void;
}) {
  return (
    <>
      <Marca />
      <div className="min-h-0 flex-1 overflow-y-auto">
        <Navegacion items={items} onNavegar={onNavegar} />
        {children}
      </div>
    </>
  );
}

export function AppShell() {
  const { usuario, logout } = useAuth();
  const { oscuro, alternarTema } = useTema();
  const ubicacion = useLocation();
  const [menuAbierto, setMenuAbierto] = useState(false);

  const items = NAVEGACION.filter(
    (item) => !item.soloAdmin || usuario?.role === "ADMIN",
  );

  const itemActual = items.find((item) =>
    item.to === "/"
      ? ubicacion.pathname === "/"
      : ubicacion.pathname === item.to ||
        ubicacion.pathname.startsWith(`${item.to}/`),
  );

  const etiquetaRol =
    usuario?.role === "ADMIN" ? "Administrador" : "Recepcion";
  const nombreVisible = usuario?.nombre?.trim() || usuario?.username || "Usuario";

  return (
    <div className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col border-r border-border bg-card lg:flex">
        <ContenidoMenu items={items} />
        <div className="border-t border-border p-4 text-xs leading-relaxed text-muted-foreground">
          Base web conectada al API de Hotel Fast.
        </div>
      </aside>

      {menuAbierto ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMenuAbierto(false)}
          aria-label="Cerrar menu"
        />
      ) : null}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-border bg-card transition-transform duration-200 lg:hidden",
          menuAbierto ? "translate-x-0" : "-translate-x-full",
        )}
        aria-hidden={!menuAbierto}
      >
        <div className="flex items-center justify-between border-b border-border pr-2">
          <Marca />
          <Boton
            variant="ghost"
            size="icon"
            onClick={() => setMenuAbierto(false)}
            aria-label="Cerrar menu"
          >
            <X className="h-4 w-4" aria-hidden />
          </Boton>
        </div>
        <ContenidoMenu
          items={items}
          onNavegar={() => setMenuAbierto(false)}
        />
      </aside>

      <div className="flex min-h-screen flex-col lg:pl-64">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-2 border-b border-border bg-background/85 px-4 backdrop-blur sm:gap-3 sm:px-6">
          <Boton
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setMenuAbierto(true)}
            aria-label="Abrir menu"
          >
            <Menu className="h-5 w-5" aria-hidden />
          </Boton>

          <div className="min-w-0 flex-1">
            <p className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
              Hotel Fast
            </p>
            <h1 className="truncate text-base font-semibold text-foreground sm:text-lg">
              {itemActual?.label ?? "Panel"}
            </h1>
          </div>

          <Boton
            variant="ghost"
            size="icon"
            onClick={alternarTema}
            aria-label={
              oscuro ? "Activar tema claro" : "Activar tema oscuro"
            }
            title={oscuro ? "Activar tema claro" : "Activar tema oscuro"}
          >
            {oscuro ? (
              <Sun className="h-5 w-5" aria-hidden />
            ) : (
              <Moon className="h-5 w-5" aria-hidden />
            )}
          </Boton>

          <div className="flex items-center gap-3 border-l border-border pl-3">
            <Avatar nombre={nombreVisible} />
            <div className="hidden min-w-0 sm:block">
              <p className="max-w-[160px] truncate text-sm font-medium">
                {nombreVisible}
              </p>
              <Badge variant="gold" className="mt-1">
                {etiquetaRol}
              </Badge>
            </div>
          </div>

          <Boton
            variant="ghost"
            size="icon"
            onClick={() => {
              void logout();
            }}
            aria-label="Cerrar sesion"
            title="Cerrar sesion"
          >
            <LogOut className="h-5 w-5" aria-hidden />
          </Boton>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
