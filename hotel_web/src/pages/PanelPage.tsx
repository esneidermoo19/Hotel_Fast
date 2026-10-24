import { useQuery } from "@tanstack/react-query";
import {
  BedDouble,
  CalendarCheck,
  CalendarClock,
  CircleDollarSign,
  DoorOpen,
  LogOut,
  Users,
  type LucideIcon,
} from "lucide-react";

import { obtenerResumenDashboard } from "@/api/dashboard";
import { mensajeDeError } from "@/api/errors";
import { EstadoCarga } from "@/components/estados/EstadoCarga";
import { EstadoError } from "@/components/estados/EstadoError";
import { Card, CardContent } from "@/components/ui/card";
import { formatearFecha } from "@/lib/fechas";

const formatoMoneda = new Intl.NumberFormat("es-CO", {
  style: "currency",
  currency: "COP",
  maximumFractionDigits: 0,
});

const formatoNumero = new Intl.NumberFormat("es-CO");

export function PanelPage() {
  const consulta = useQuery({
    queryKey: ["dashboard"],
    queryFn: obtenerResumenDashboard,
  });

  const resumen = consulta.data;

  return (
    <div className="animate-fade-in space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[0.16em] text-primary">
          {formatearFecha(new Date().toISOString())}
        </p>
        <h2 className="mt-2 font-display text-2xl text-foreground sm:text-3xl">
          Bienvenido a Hotel Fast
        </h2>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          Resumen de la operación del hotel para hoy.
        </p>
      </header>

      {consulta.isPending ? (
        <EstadoCarga mensaje="Cargando indicadores del hotel..." />
      ) : null}

      {consulta.isError ? (
        <EstadoError
          titulo="No se pudieron cargar los indicadores"
          mensaje={mensajeDeError(consulta.error)}
          onReintentar={() => void consulta.refetch()}
        />
      ) : null}

      {resumen ? (
        <>
          <section
            aria-label="Indicadores operativos"
            className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
          >
            <Indicador
              etiqueta="Reservas activas"
              valor={formatoNumero.format(resumen.reservasActivas)}
              detalle="Pendientes, confirmadas o alojadas"
              icono={CalendarCheck}
            />
            <Indicador
              etiqueta="Llegadas pendientes"
              valor={formatoNumero.format(resumen.reservasPendientesCheckIn)}
              detalle="Reservas que aún no registran entrada"
              icono={CalendarClock}
            />
            <Indicador
              etiqueta="Huéspedes alojados"
              valor={formatoNumero.format(resumen.huespedesAlojados)}
              detalle="Personas con check-in registrado"
              icono={Users}
            />
            <Indicador
              etiqueta="Ocupación"
              valor={`${formatoNumero.format(resumen.tasaOcupacion)}%`}
              detalle={`${resumen.habitacionesOcupadas} ocupadas de ${resumen.habitacionesOcupadas + resumen.habitacionesDisponibles} operativas`}
              icono={BedDouble}
            />
          </section>

          <section
            aria-label="Estado de habitaciones"
            className="grid gap-4 sm:grid-cols-3"
          >
            <Indicador
              etiqueta="Habitaciones disponibles"
              valor={formatoNumero.format(resumen.habitacionesDisponibles)}
              detalle="Listas para asignación"
              icono={DoorOpen}
            />
            <Indicador
              etiqueta="Check-outs de hoy"
              valor={formatoNumero.format(resumen.checkOutsDelDia)}
              detalle="Salidas registradas hoy"
              icono={LogOut}
            />
            <Indicador
              etiqueta="En mantenimiento"
              valor={formatoNumero.format(resumen.habitacionesEnMantenimiento)}
              detalle="Fuera de operación"
              icono={BedDouble}
            />
          </section>

          <section
            aria-label="Indicadores financieros"
            className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
          >
            <Indicador
              etiqueta="Ingresos de hoy"
              valor={formatoMoneda.format(resumen.ingresosDelDia)}
              detalle="Recaudo neto registrado hoy"
              icono={CircleDollarSign}
            />
            <Indicador
              etiqueta="Cuentas con saldo pendiente"
              valor={formatoNumero.format(resumen.cuentasConSaldoPendiente)}
              detalle="Cuentas con saldo por cobrar"
              icono={CircleDollarSign}
            />
            <Indicador
              etiqueta="RevPAR de hoy"
              valor={formatoMoneda.format(resumen.revpar)}
              detalle="Ingreso por habitación operativa"
              icono={CircleDollarSign}
            />
            <Indicador
              etiqueta="Balance de caja"
              valor={formatoMoneda.format(resumen.balanceCaja)}
              detalle="Saldo neto acumulado"
              icono={CircleDollarSign}
            />
          </section>
        </>
      ) : null}
    </div>
  );
}

interface IndicadorProps {
  etiqueta: string;
  valor: string;
  detalle: string;
  icono: LucideIcon;
}

function Indicador({ etiqueta, valor, detalle, icono: Icono }: IndicadorProps) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-sm text-muted-foreground">{etiqueta}</p>
            <p className="mt-3 break-words text-2xl font-semibold tabular-nums text-foreground">
              {valor}
            </p>
          </div>
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
            <Icono className="h-5 w-5" aria-hidden />
          </span>
        </div>
        <p className="mt-3 text-xs text-muted-foreground">{detalle}</p>
      </CardContent>
    </Card>
  );
}
