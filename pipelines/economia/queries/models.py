from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DenueBase(DeclarativeBase):
    pass


class Actualizaciones(DenueBase):
    __tablename__ = "actualizaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False, unique=True)


class Localidades(DenueBase):
    __tablename__ = "localidades"
    __table_args__ = (
        UniqueConstraint(
            "municipio_id", "entidad_id", "clave_localidad", name="uq_localidades_clave"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cve_geo_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    clave_localidad: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    localidad: Mapped[str | None] = mapped_column(Text, nullable=True)


class ActividadesEconomicas(DenueBase):
    __tablename__ = "actividades_economicas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    nombre_actividad_economica: Mapped[str] = mapped_column(Text, nullable=False)


class RangosPersonal(DenueBase):
    __tablename__ = "rangos_personal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class Establecimientos(DenueBase):
    __tablename__ = "establecimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    actualizacion_id: Mapped[int] = mapped_column(
        ForeignKey("actualizaciones.id"), primary_key=True
    )
    nombre_establecimiento: Mapped[str] = mapped_column(Text, nullable=False)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    localidad_id: Mapped[int | None] = mapped_column(
        ForeignKey("localidades.id"), nullable=True
    )
    actividad_economica_id: Mapped[int | None] = mapped_column(
        ForeignKey("actividades_economicas.id"), nullable=True
    )
    rango_personal_id: Mapped[int | None] = mapped_column(
        ForeignKey("rangos_personal.id"), nullable=True
    )
