import { spawnSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import openapiTS, { astToString } from "openapi-typescript";

const raizRepositorio = fileURLToPath(new URL("../..", import.meta.url));
const rutaSalida = fileURLToPath(new URL("../src/api/schema.d.ts", import.meta.url));
const rutaLocal = path.join(raizRepositorio, "openapi.json");
const usarRemoto =
  process.argv.includes("--remoto") || Boolean(process.env.OPENAPI_URL);

function resolverPython() {
  const candidatos =
    process.platform === "win32"
      ? [path.join(raizRepositorio, ".venv", "Scripts", "python.exe")]
      : [path.join(raizRepositorio, ".venv", "bin", "python")];
  return candidatos.find((candidato) => existsSync(candidato)) ?? "python";
}

let especificacion;

if (usarRemoto) {
  const entrada = new URL(
    process.env.OPENAPI_URL ?? "http://localhost:8000/openapi.json",
  );
  console.log(`Generando tipos desde ${entrada.href}`);
  especificacion = await (await fetch(entrada)).json();
} else {
  const existiaPrevio = existsSync(rutaLocal);
  const contenidoPrevio = existiaPrevio ? readFileSync(rutaLocal) : null;

  const resultado = spawnSync(
    resolverPython(),
    ["-m", "app.export_openapi"],
    {
      cwd: raizRepositorio,
      stdio: "inherit",
      shell: false,
    },
  );

  if (resultado.status !== 0) {
    console.error(
      "No se pudo exportar openapi.json. Verifica el entorno Python del backend.",
    );
    process.exit(1);
  }

  try {
    especificacion = JSON.parse(readFileSync(rutaLocal, "utf8"));
  } finally {
    if (contenidoPrevio !== null) {
      writeFileSync(rutaLocal, contenidoPrevio);
    } else {
      rmSync(rutaLocal, { force: true });
    }
  }
}

const ast = await openapiTS(especificacion);
mkdirSync(path.dirname(rutaSalida), { recursive: true });
writeFileSync(rutaSalida, astToString(ast), "utf8");
console.log(`Tipos de la API generados en ${rutaSalida}`);
