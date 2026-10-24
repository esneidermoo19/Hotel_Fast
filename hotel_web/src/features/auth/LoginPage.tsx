import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Eye, EyeOff, Loader2, LockKeyhole, ShieldCheck } from "lucide-react";
import { useForm } from "react-hook-form";
import { useLocation, useNavigate } from "react-router";
import { z } from "zod";

import { mensajeDeError } from "@/api/errors";
import { EstadoError } from "@/components/estados/EstadoError";
import { Boton } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { useAuth } from "./auth-context";

const esquema = z.object({
  identificador: z
    .string()
    .trim()
    .min(1, "Ingresa tu usuario o correo.")
    .max(120, "El identificador es demasiado largo."),
  password: z.string().min(1, "Ingresa tu contrasena."),
});

type Formulario = z.infer<typeof esquema>;

interface EstadoNavegacion {
  desde?: string;
}

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const ubicacion = useLocation();
  const [mostrarPassword, setMostrarPassword] = useState(false);
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Formulario>({
    resolver: zodResolver(esquema),
    defaultValues: {
      identificador: "",
      password: "",
    },
  });

  const enviar = async (valores: Formulario) => {
    setErrorGeneral(null);
    const identificador = valores.identificador.trim();

    try {
      await login({
        ...(identificador.includes("@")
          ? { email: identificador }
          : { username: identificador }),
        password: valores.password,
      });

      const destino =
        (ubicacion.state as EstadoNavegacion | null)?.desde ?? "/";
      navigate(destino, { replace: true });
    } catch (error) {
      setErrorGeneral(mensajeDeError(error));
    }
  };

  return (
    <div className="fondo-login flex min-h-screen items-center justify-center px-4 py-8 sm:py-12">
      <div className="grid w-full max-w-[1100px] overflow-hidden rounded-2xl border border-border bg-card/85 shadow-2xl backdrop-blur lg:grid-cols-2">
        <section className="relative hidden flex-col justify-between gap-10 bg-gradient-to-br from-primary/15 via-transparent to-primary/10 p-12 lg:flex">
          <div>
            <span className="inline-block h-1 w-14 rounded-full bg-primary" />
            <p className="mt-6 font-display text-4xl leading-tight text-foreground">
              Hotel Fast
            </p>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-muted-foreground">
              La operacion diaria del hotel, ordenada en un solo lugar. Una
              base clara para recepcion, reservas y gestion.
            </p>
          </div>

          <ul className="space-y-3 text-sm text-muted-foreground">
            <li className="flex items-center gap-3">
              <ShieldCheck className="h-4 w-4 text-primary" aria-hidden />
              Acceso restringido al personal autorizado.
            </li>
            <li className="flex items-center gap-3">
              <LockKeyhole className="h-4 w-4 text-primary" aria-hidden />
              Sesion protegida con renovacion automatica.
            </li>
          </ul>

          <p className="text-xs uppercase tracking-[0.2em] text-primary">
            Midnight &amp; Champagne
          </p>
        </section>

        <section className="p-6 sm:p-10 lg:p-12">
          <div className="mb-8 lg:hidden">
            <span className="inline-block h-1 w-12 rounded-full bg-primary" />
            <p className="mt-4 font-display text-3xl text-foreground">
              Hotel Fast
            </p>
          </div>

          <div className="max-w-md">
            <h1 className="font-display text-2xl text-foreground sm:text-3xl">
              Iniciar sesion
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Ingresa con tu usuario o correo para continuar.
            </p>

            <form
              onSubmit={handleSubmit(enviar)}
              noValidate
              className="mt-8 space-y-5"
            >
              <div className="space-y-2">
                <Label htmlFor="identificador">Usuario o correo</Label>
                <Input
                  id="identificador"
                  autoFocus
                  autoComplete="username"
                  placeholder="admin o admin@hotel.com"
                  aria-invalid={errors.identificador ? "true" : "false"}
                  aria-describedby={
                    errors.identificador ? "error-identificador" : undefined
                  }
                  {...register("identificador")}
                />
                {errors.identificador ? (
                  <p
                    id="error-identificador"
                    className="text-sm text-destructive"
                  >
                    {errors.identificador.message}
                  </p>
                ) : null}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Contrasena</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={mostrarPassword ? "text" : "password"}
                    autoComplete="current-password"
                    placeholder="Tu contrasena"
                    className="pr-11"
                    aria-invalid={errors.password ? "true" : "false"}
                    aria-describedby={
                      errors.password ? "error-password" : undefined
                    }
                    {...register("password")}
                  />
                  <button
                    type="button"
                    onClick={() => setMostrarPassword((valor) => !valor)}
                    className="absolute inset-y-0 right-0 flex w-11 items-center justify-center rounded-r-md text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    aria-label={
                      mostrarPassword
                        ? "Ocultar contrasena"
                        : "Mostrar contrasena"
                    }
                    title={
                      mostrarPassword
                        ? "Ocultar contrasena"
                        : "Mostrar contrasena"
                    }
                  >
                    {mostrarPassword ? (
                      <EyeOff className="h-4 w-4" aria-hidden />
                    ) : (
                      <Eye className="h-4 w-4" aria-hidden />
                    )}
                  </button>
                </div>
                {errors.password ? (
                  <p id="error-password" className="text-sm text-destructive">
                    {errors.password.message}
                  </p>
                ) : null}
              </div>

              {errorGeneral ? (
                <EstadoError titulo="No se pudo iniciar sesion" mensaje={errorGeneral} />
              ) : null}

              <Boton type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                    Ingresando...
                  </>
                ) : (
                  "Iniciar sesion"
                )}
              </Boton>
            </form>
          </div>
        </section>
      </div>
    </div>
  );
}
