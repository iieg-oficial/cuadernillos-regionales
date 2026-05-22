from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DenueBase(DeclarativeBase):
    pass


class CatActualizaciones(DenueBase):
    __tablename__ = "cat_actualizaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_actualizacion: Mapped[date] = mapped_column(Date, nullable=False, unique=True)


class CatLocalidades(DenueBase):
    __tablename__ = "cat_localidades"
    __table_args__ = (
        UniqueConstraint(
            "municipio_id", "entidad_id", "localidad_id", name="uq_localidades_clave"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cve_geo_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    localidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    municipio_id: Mapped[int] = mapped_column(Integer, nullable=False)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    localidad: Mapped[str | None] = mapped_column(Text, nullable=True)


class CatSectores(DenueBase):
    __tablename__ = "cat_sectores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    sector: Mapped[str] = mapped_column(Text, nullable=False)


class CatSubsectores(DenueBase):
    __tablename__ = "cat_subsectores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    subsector: Mapped[str] = mapped_column(Text, nullable=False)


class CatRamas(DenueBase):
    __tablename__ = "cat_ramas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    rama: Mapped[str] = mapped_column(Text, nullable=False)


class CatSubramas(DenueBase):
    __tablename__ = "cat_subramas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    subrama: Mapped[str] = mapped_column(Text, nullable=False)


class CatClasesActividad(DenueBase):
    __tablename__ = "cat_clases_actividad"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    clase: Mapped[str] = mapped_column(Text, nullable=False)


class CatRangosPersonal(DenueBase):
    __tablename__ = "cat_rangos_personal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class CatTiposEstablecimientos(DenueBase):
    __tablename__ = "cat_tipos_establecimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class StgEstablecimientos(DenueBase):
    __tablename__ = "stg_establecimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    actualizacion_id: Mapped[int] = mapped_column(
        ForeignKey("cat_actualizaciones.id"), primary_key=True
    )
    nombre_establecimiento: Mapped[str] = mapped_column(Text, nullable=False)
    razon_social: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitud: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_alta: Mapped[date | None] = mapped_column(Date, nullable=True)
    nombre_asentamiento: Mapped[str | None] = mapped_column(Text, nullable=True)
    ageb: Mapped[str | None] = mapped_column(Text, nullable=True)
    localidad_id: Mapped[int | None] = mapped_column(
        ForeignKey("cat_localidades.id"), nullable=True
    )
    sector_id: Mapped[int | None] = mapped_column(
        ForeignKey("cat_sectores.id"), nullable=True
    )
    subsector_id: Mapped[int | None] = mapped_column(
        ForeignKey("cat_subsectores.id"), nullable=True
    )
    rama_id: Mapped[int | None] = mapped_column(
        ForeignKey("cat_ramas.id"), nullable=True
    )
    subrama_id: Mapped[int | None] = mapped_column(
        ForeignKey("cat_subramas.id"), nullable=True
    )
    clase_actividad_id: Mapped[int | None] = mapped_column(
        ForeignKey("cat_clases_actividad.id"), nullable=True
    )
    rango_personal_id: Mapped[int | None] = mapped_column(
        ForeignKey("cat_rangos_personal.id"), nullable=True
    )
    tipo_establecimiento_id: Mapped[int | None] = mapped_column(
        ForeignKey("cat_tipos_establecimientos.id"), nullable=True
    )
