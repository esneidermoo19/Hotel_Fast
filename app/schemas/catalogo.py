from app.schemas.base import CamelCaseSchema


class CatalogoRead(CamelCaseSchema):
    nombre: str
    etiqueta: str
    valores: list[str]
