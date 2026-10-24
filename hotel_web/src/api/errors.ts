export interface ErrorCampo {
  campo: string;
  mensaje: string;
  tipo?: string;
}

interface SobreError {
  detail?: string;
  code?: string;
  errors?: ErrorCampo[];
}

const MENSAJES_POR_CODIGO: Record<string, string> = {
  VALIDACION: "Revisa los datos ingresados.",
  NO_AUTORIZADO: "Usuario o contrasena incorrectos.",
  TOKEN_INVALIDO: "La sesion expiro. Inicia sesion de nuevo.",
  REFRESH_TOKEN_INVALIDO: "La sesion expiro. Inicia sesion de nuevo.",
  SIN_PERMISOS: "No tienes permisos para realizar esta accion.",
  NO_ENCONTRADO: "No se encontro el recurso solicitado.",
  CONFLICTO: "La operacion entra en conflicto con el estado actual.",
  REGLA_NEGOCIO: "La operacion no cumple una regla de negocio.",
  FORMATO_IMAGEN_INVALIDO: "El formato de la imagen no es valido.",
  IMAGEN_MUY_GRANDE: "La imagen supera el tamano maximo permitido.",
  MAXIMO_IMAGENES: "La habitacion alcanzo el maximo de imagenes.",
  DEMASIADAS_SOLICITUDES:
    "Demasiadas solicitudes. Espera un momento e intenta de nuevo.",
  NO_DISPONIBLE: "El servicio no esta disponible en este momento.",
  BASE_DATOS: "Ocurrio un error en la base de datos.",
  TIEMPO_AGOTADO: "El servidor tardo demasiado en responder.",
  RED: "No se pudo conectar con el servidor.",
};

const MENSAJE_GENERICO = "Ocurrio un error inesperado.";

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly errores: ErrorCampo[];

  constructor(
    mensaje: string,
    code: string,
    status: number,
    errores: ErrorCampo[] = [],
  ) {
    super(mensaje);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.errores = errores;
  }
}

export function mensajePorCodigo(
  code: string | undefined,
  respaldo?: string,
): string {
  if (code && MENSAJES_POR_CODIGO[code]) {
    return MENSAJES_POR_CODIGO[code];
  }
  return respaldo?.trim() || MENSAJE_GENERICO;
}

export async function mapearError(respuesta: Response): Promise<ApiError> {
  let sobre: SobreError = {};

  try {
    sobre = (await respuesta.json()) as SobreError;
  } catch {
    sobre = {};
  }

  const errores = Array.isArray(sobre.errors) ? sobre.errors : [];
  const mensaje =
    errores.length > 0
      ? errores.map((error) => error.mensaje).join(" ")
      : mensajePorCodigo(sobre.code, sobre.detail);

  return new ApiError(
    mensaje,
    sobre.code ?? "ERROR_DESCONOCIDO",
    respuesta.status,
    errores,
  );
}

export function mensajeDeError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return MENSAJE_GENERICO;
}
