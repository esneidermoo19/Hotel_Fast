import json
from pathlib import Path

from app.main import app


def main() -> None:
    ruta = Path(__file__).resolve().parent.parent / "openapi.json"
    ruta.write_text(
        json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Especificacion OpenAPI exportada en {ruta}")


if __name__ == "__main__":
    main()
