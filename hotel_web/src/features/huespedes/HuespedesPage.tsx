import { useEffect, useState, type ReactNode } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Loader2, Pencil, Plus, Search, X } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import {
  actualizarHuesped,
  crearHuesped,
  listarHuespedes,
  type DatosHuesped,
  type Huesped,
  type TipoDocumento,
} from "@/api/huespedes";
import { mensajeDeError } from "@/api/errors";
import { EstadoCarga } from "@/components/estados/EstadoCarga";
import { EstadoError } from "@/components/estados/EstadoError";
import { EstadoVacio } from "@/components/estados/EstadoVacio";
import { Boton } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const TAMANO_PAGINA = 10;
const tiposDocumento: { valor: TipoDocumento; etiqueta: string }[] = [
  { valor: "CC", etiqueta: "Cédula de ciudadanía" },
  { valor: "CE", etiqueta: "Cédula de extranjería" },
  { valor: "PASAPORTE", etiqueta: "Pasaporte" },
  { valor: "TI", etiqueta: "Tarjeta de identidad" },
  { valor: "OTRO", etiqueta: "Otro" },
];

const esquemaHuesped = z.object({
  tipoDocumento: z.enum(["CC", "CE", "PASAPORTE", "TI", "OTRO"]),
  numeroDocumento: z
    .string()
    .trim()
    .regex(/^[A-Za-z0-9]{4,20}$/, "Usa de 4 a 20 letras o números."),
  nombres: z.string().trim().min(1, "Ingresa los nombres.").max(120),
  apellidos: z.string().trim().min(1, "Ingresa los apellidos.").max(120),
  email: z
    .string()
    .trim()
    .refine(
      (valor) => !valor || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor),
      "Ingresa un correo válido.",
    ),
  telefono: z
    .string()
    .trim()
    .refine(
      (valor) => !valor || /^\+?\d{7,15}$/.test(valor),
      "Usa entre 7 y 15 dígitos; puedes incluir + al inicio.",
    ),
  nacionalidad: z.string().trim().max(80),
  fechaNacimiento: z.string(),
  direccion: z.string().trim(),
  observaciones: z.string().trim(),
});

type ValoresHuesped = z.infer<typeof esquemaHuesped>;

const valoresVacios: ValoresHuesped = {
  tipoDocumento: "CC",
  numeroDocumento: "",
  nombres: "",
  apellidos: "",
  email: "",
  telefono: "",
  nacionalidad: "",
  fechaNacimiento: "",
  direccion: "",
  observaciones: "",
};

const etiquetasDocumento: Record<TipoDocumento, string> = {
  CC: "Cédula de ciudadanía",
  CE: "Cédula de extranjería",
  PASAPORTE: "Pasaporte",
  TI: "Tarjeta de identidad",
  OTRO: "Otro",
};

function comoDatosApi(valores: ValoresHuesped): DatosHuesped {
  return {
    tipoDocumento: valores.tipoDocumento,
    numeroDocumento: valores.numeroDocumento.trim(),
    nombres: valores.nombres.trim(),
    apellidos: valores.apellidos.trim(),
    email: valores.email.trim() || null,
    telefono: valores.telefono.trim() || null,
    nacionalidad: valores.nacionalidad.trim() || null,
    fechaNacimiento: valores.fechaNacimiento || null,
    direccion: valores.direccion.trim() || null,
    observaciones: valores.observaciones.trim() || null,
  };
}

function comoValoresFormulario(huesped: Huesped): ValoresHuesped {
  return {
    tipoDocumento: huesped.tipoDocumento,
    numeroDocumento: huesped.numeroDocumento,
    nombres: huesped.nombres,
    apellidos: huesped.apellidos,
    email: huesped.email ?? "",
    telefono: huesped.telefono ?? "",
    nacionalidad: huesped.nacionalidad ?? "",
    fechaNacimiento: huesped.fechaNacimiento ?? "",
    direccion: huesped.direccion ?? "",
    observaciones: huesped.observaciones ?? "",
  };
}

export function HuespedesPage() {
  const clienteConsultas = useQueryClient();
  const [busqueda, setBusqueda] = useState("");
  const [busquedaAplicada, setBusquedaAplicada] = useState("");
  const [pagina, setPagina] = useState(1);
  const [formularioAbierto, setFormularioAbierto] = useState(false);
  const [huespedEditando, setHuespedEditando] = useState<Huesped | null>(null);

  useEffect(() => {
    const temporizador = window.setTimeout(() => {
      setBusquedaAplicada(busqueda.trim());
      setPagina(1);
    }, 300);
    return () => window.clearTimeout(temporizador);
  }, [busqueda]);

  const consulta = useQuery({
    queryKey: ["huespedes", busquedaAplicada, pagina],
    queryFn: () =>
      listarHuespedes({ q: busquedaAplicada, pagina, tamano: TAMANO_PAGINA }),
  });

  const formulario = useForm<ValoresHuesped>({
    resolver: zodResolver(esquemaHuesped),
    defaultValues: valoresVacios,
  });

  const mutacion = useMutation({
    mutationFn: (valores: ValoresHuesped) => {
      const datos = comoDatosApi(valores);
      return huespedEditando
        ? actualizarHuesped(huespedEditando.id, datos)
        : crearHuesped(datos);
    },
    onSuccess: async () => {
      await clienteConsultas.invalidateQueries({ queryKey: ["huespedes"] });
      setPagina(1);
      setFormularioAbierto(false);
      setHuespedEditando(null);
      formulario.reset(valoresVacios);
    },
  });

  const abrirNuevo = () => {
    mutacion.reset();
    setHuespedEditando(null);
    formulario.reset(valoresVacios);
    setFormularioAbierto(true);
  };

  const abrirEdicion = (huesped: Huesped) => {
    mutacion.reset();
    setHuespedEditando(huesped);
    formulario.reset(comoValoresFormulario(huesped));
    setFormularioAbierto(true);
  };

  const cerrarFormulario = () => {
    setFormularioAbierto(false);
    setHuespedEditando(null);
    mutacion.reset();
    formulario.reset(valoresVacios);
  };

  const datos = consulta.data;
  const paginas = Math.max(1, Math.ceil((datos?.total ?? 0) / TAMANO_PAGINA));

  return (
    <div className="animate-fade-in space-y-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="font-display text-2xl text-foreground sm:text-3xl">
            Huéspedes
          </h2>
          <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
            Consulta y actualiza el registro de huéspedes del hotel.
          </p>
        </div>
        <Boton type="button" onClick={abrirNuevo}>
          <Plus className="h-4 w-4" aria-hidden />
          Nuevo huésped
        </Boton>
      </header>

      {formularioAbierto ? (
        <Card>
          <CardHeader className="flex-row items-start justify-between gap-4">
            <div>
              <CardTitle>
                {huespedEditando ? "Editar huésped" : "Registrar huésped"}
              </CardTitle>
              <CardDescription className="mt-2">
                Completa los datos de identificación y contacto.
              </CardDescription>
            </div>
            <Boton
              type="button"
              variant="ghost"
              size="icon"
              onClick={cerrarFormulario}
              aria-label="Cerrar formulario"
            >
              <X className="h-4 w-4" aria-hidden />
            </Boton>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={formulario.handleSubmit((valores) => mutacion.mutate(valores))}
              noValidate
              className="space-y-5"
            >
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <CampoHuesped id="tipoDocumento" etiqueta="Tipo de documento" error={formulario.formState.errors.tipoDocumento?.message}>
                  <select
                    id="tipoDocumento"
                    className={claseSelect}
                    aria-invalid={Boolean(formulario.formState.errors.tipoDocumento)}
                    {...formulario.register("tipoDocumento")}
                  >
                    {tiposDocumento.map((tipo) => (
                      <option key={tipo.valor} value={tipo.valor}>
                        {tipo.etiqueta}
                      </option>
                    ))}
                  </select>
                </CampoHuesped>
                <CampoHuesped id="numeroDocumento" etiqueta="Número de documento" error={formulario.formState.errors.numeroDocumento?.message}>
                  <Input
                    id="numeroDocumento"
                    autoComplete="off"
                    aria-invalid={Boolean(formulario.formState.errors.numeroDocumento)}
                    aria-describedby={formulario.formState.errors.numeroDocumento ? "numeroDocumento-error" : undefined}
                    {...formulario.register("numeroDocumento")}
                  />
                </CampoHuesped>
                <CampoHuesped id="nombres" etiqueta="Nombres" error={formulario.formState.errors.nombres?.message}>
                  <Input id="nombres" autoComplete="given-name" aria-invalid={Boolean(formulario.formState.errors.nombres)} aria-describedby={formulario.formState.errors.nombres ? "nombres-error" : undefined} {...formulario.register("nombres")} />
                </CampoHuesped>
                <CampoHuesped id="apellidos" etiqueta="Apellidos" error={formulario.formState.errors.apellidos?.message}>
                  <Input id="apellidos" autoComplete="family-name" aria-invalid={Boolean(formulario.formState.errors.apellidos)} aria-describedby={formulario.formState.errors.apellidos ? "apellidos-error" : undefined} {...formulario.register("apellidos")} />
                </CampoHuesped>
                <CampoHuesped id="email" etiqueta="Correo electrónico" error={formulario.formState.errors.email?.message}>
                  <Input id="email" type="email" autoComplete="email" aria-invalid={Boolean(formulario.formState.errors.email)} aria-describedby={formulario.formState.errors.email ? "email-error" : undefined} {...formulario.register("email")} />
                </CampoHuesped>
                <CampoHuesped id="telefono" etiqueta="Teléfono" error={formulario.formState.errors.telefono?.message}>
                  <Input id="telefono" type="tel" autoComplete="tel" aria-invalid={Boolean(formulario.formState.errors.telefono)} aria-describedby={formulario.formState.errors.telefono ? "telefono-error" : undefined} {...formulario.register("telefono")} />
                </CampoHuesped>
                <CampoHuesped id="nacionalidad" etiqueta="Nacionalidad" error={formulario.formState.errors.nacionalidad?.message}>
                  <Input id="nacionalidad" {...formulario.register("nacionalidad")} />
                </CampoHuesped>
                <CampoHuesped id="fechaNacimiento" etiqueta="Fecha de nacimiento" error={formulario.formState.errors.fechaNacimiento?.message}>
                  <Input id="fechaNacimiento" type="date" autoComplete="bday" {...formulario.register("fechaNacimiento")} />
                </CampoHuesped>
                <CampoHuesped id="direccion" etiqueta="Dirección" error={formulario.formState.errors.direccion?.message}>
                  <Input id="direccion" autoComplete="street-address" {...formulario.register("direccion")} />
                </CampoHuesped>
                <div className="space-y-2 sm:col-span-2 lg:col-span-3">
                  <Label htmlFor="observaciones">Observaciones</Label>
                  <textarea id="observaciones" rows={3} className={claseTextarea} {...formulario.register("observaciones")} />
                </div>
              </div>

              {mutacion.isError ? (
                <EstadoError
                  titulo="No se pudo guardar el huésped"
                  mensaje={mensajeDeError(mutacion.error)}
                />
              ) : null}

              <div className="flex flex-wrap justify-end gap-3">
                <Boton type="button" variant="outline" onClick={cerrarFormulario}>
                  Cancelar
                </Boton>
                <Boton type="submit" disabled={mutacion.isPending}>
                  {mutacion.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                      Guardando...
                    </>
                  ) : huespedEditando ? (
                    "Guardar cambios"
                  ) : (
                    "Registrar huésped"
                  )}
                </Boton>
              </div>
            </form>
          </CardContent>
        </Card>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Directorio de huéspedes</CardTitle>
          <CardDescription>
            Busca por nombre, apellido o número de documento.
          </CardDescription>
          <div className="relative mt-3 max-w-lg">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" aria-hidden />
            <Input
              type="search"
              value={busqueda}
              onChange={(evento) => setBusqueda(evento.target.value)}
              placeholder="Buscar huésped..."
              aria-label="Buscar huéspedes"
              className="pl-9"
            />
          </div>
        </CardHeader>
        <CardContent>
          {consulta.isPending ? <EstadoCarga mensaje="Cargando huéspedes..." /> : null}
          {consulta.isError ? (
            <EstadoError
              titulo="No se pudo cargar el directorio"
              mensaje={mensajeDeError(consulta.error)}
              onReintentar={() => void consulta.refetch()}
            />
          ) : null}

          {datos && datos.items.length === 0 ? (
            <EstadoVacio
              titulo={busquedaAplicada ? "No encontramos huéspedes" : "Aún no hay huéspedes registrados"}
              descripcion={
                busquedaAplicada
                  ? "Prueba con otro nombre o documento."
                  : "Registra el primer huésped para que aparezca en este directorio."
              }
            />
          ) : null}

          {datos && datos.items.length > 0 ? (
            <>
              <div className="overflow-x-auto rounded-md border border-border">
                <table className="w-full min-w-[760px] text-left text-sm">
                  <thead className="bg-muted/60 text-xs uppercase tracking-wide text-muted-foreground">
                    <tr>
                      <th scope="col" className="px-4 py-3 font-medium">Huésped</th>
                      <th scope="col" className="px-4 py-3 font-medium">Documento</th>
                      <th scope="col" className="px-4 py-3 font-medium">Contacto</th>
                      <th scope="col" className="px-4 py-3 font-medium">Nacionalidad</th>
                      <th scope="col" className="px-4 py-3 font-medium"><span className="sr-only">Acciones</span></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {datos.items.map((huesped) => (
                      <tr key={huesped.id} className="hover:bg-muted/30">
                        <td className="px-4 py-3">
                          <p className="font-medium text-foreground">{huesped.nombres} {huesped.apellidos}</p>
                          <p className="mt-1 text-xs text-muted-foreground">ID {huesped.id}</p>
                        </td>
                        <td className="px-4 py-3">
                          <p>{etiquetasDocumento[huesped.tipoDocumento]}</p>
                          <p className="mt-1 text-xs text-muted-foreground">{huesped.numeroDocumento}</p>
                        </td>
                        <td className="px-4 py-3">
                          <p>{huesped.email || "Sin correo"}</p>
                          <p className="mt-1 text-xs text-muted-foreground">{huesped.telefono || "Sin teléfono"}</p>
                        </td>
                        <td className="px-4 py-3">{huesped.nacionalidad || "—"}</td>
                        <td className="px-4 py-3 text-right">
                          <Boton
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => abrirEdicion(huesped)}
                            aria-label={`Editar a ${huesped.nombres} ${huesped.apellidos}`}
                          >
                            <Pencil className="h-4 w-4" aria-hidden />
                            Editar
                          </Boton>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="mt-4 flex flex-col gap-3 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
                <p>
                  {datos.total === 1 ? "1 huésped" : `${datos.total} huéspedes`} · Página {datos.pagina} de {paginas}
                </p>
                <div className="flex gap-2">
                  <Boton
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={pagina <= 1 || consulta.isFetching}
                    onClick={() => setPagina((actual) => Math.max(1, actual - 1))}
                  >
                    <ChevronLeft className="h-4 w-4" aria-hidden />
                    Anterior
                  </Boton>
                  <Boton
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={pagina >= paginas || consulta.isFetching}
                    onClick={() => setPagina((actual) => Math.min(paginas, actual + 1))}
                  >
                    Siguiente
                    <ChevronRight className="h-4 w-4" aria-hidden />
                  </Boton>
                </div>
              </div>
            </>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}

const claseSelect =
  "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background";
const claseTextarea =
  "flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background";

interface CampoHuespedProps {
  id: string;
  etiqueta: string;
  error?: string;
  children: ReactNode;
}

function CampoHuesped({ id, etiqueta, error, children }: CampoHuespedProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{etiqueta}</Label>
      {children}
      {error ? (
        <p id={`${id}-error`} className="text-sm text-destructive">
          {error}
        </p>
      ) : null}
    </div>
  );
}
