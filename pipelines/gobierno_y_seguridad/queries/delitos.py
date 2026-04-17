from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from pipelines.gobierno_y_seguridad.queries.models import DelitosVw


def get_conteo_por_municipio_anio(session: Session) -> list[dict]:
    stmt = (
        select(
            DelitosVw.cvegeo,
            DelitosVw.municipio,
            extract("year", DelitosVw.fecha_denuncia).label("anio"),
            func.count().label("total"),
        )
        .where(DelitosVw.cvegeo.isnot(None))
        .where(DelitosVw.fecha_denuncia.isnot(None))
        .group_by(
            DelitosVw.cvegeo,
            DelitosVw.municipio,
            extract("year", DelitosVw.fecha_denuncia),
        )
        .order_by(DelitosVw.cvegeo, extract("year", DelitosVw.fecha_denuncia))
    )
    return [row._asdict() for row in session.execute(stmt)]
