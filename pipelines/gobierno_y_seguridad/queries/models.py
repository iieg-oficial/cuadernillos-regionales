from datetime import date

from sqlalchemy import Date, Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DelitosVw(Base):
    __tablename__ = "delitos_vw"

    id: Mapped[int] = mapped_column(primary_key=True)
    delito: Mapped[str | None] = mapped_column(String)
    bien_afectado: Mapped[str | None] = mapped_column(String)
    violencia: Mapped[str | None] = mapped_column(String)
    zona_geografica: Mapped[str | None] = mapped_column(String)
    municipio: Mapped[str | None] = mapped_column(String)
    cvegeo: Mapped[str | None] = mapped_column(String)
    colonia: Mapped[str | None] = mapped_column(String)
    calle: Mapped[str | None] = mapped_column(String)
    cruce: Mapped[str | None] = mapped_column(String)
    hora: Mapped[str | None] = mapped_column(String)
    longitud: Mapped[float | None] = mapped_column(Float)
    latitud: Mapped[float | None] = mapped_column(Float)
    fecha_denuncia: Mapped[date | None] = mapped_column(Date)
    fecha_actualizacion: Mapped[date | None] = mapped_column(Date)
