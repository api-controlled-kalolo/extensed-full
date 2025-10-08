"""Funciones auxiliares para trabajar con el dataset oficial de ubigeo.

El archivo `ventas/data/ubigeo.csv` proviene del proyecto público
`jmcastagnetto/ubigeo-peru`, el cual consolida los códigos UBIGEO
publicados por RENIEC e INEI. Se utilizan los nombres oficiales de
departamentos, provincias y distritos.
"""

from __future__ import annotations

import csv
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from django.conf import settings


CSV_FILENAME = "ubigeo.csv"
CSV_RELATIVE_PATH = Path("ventas") / "data" / CSV_FILENAME


class UbigeoDataError(RuntimeError):
    """Señala problemas al cargar o procesar el dataset de ubigeo."""


def _dataset_path() -> Path:
    base_dir = Path(settings.BASE_DIR)
    return base_dir / CSV_RELATIVE_PATH


def _normalize_key(value: str) -> str:
    """Normaliza texto para comparaciones insensibles a mayúsculas y tildes."""

    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value.strip())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).casefold()


def _iter_rows() -> Iterable[Dict[str, str]]:
    path = _dataset_path()
    if not path.exists():
        raise UbigeoDataError(
            "No se encontró el dataset de ubigeo en %s. Asegúrate de descargarlo." % path
        )

    with path.open(encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            nombre_completo = row.get("Nombrecompleto", "")
            parts = [part.strip() for part in nombre_completo.split("/")]
            # Se esperan exactamente: Departamento / Provincia / Distrito
            if len(parts) != 3:
                continue

            department, province, district = parts
            if not province:
                # Filtramos la fila del departamento puro (sin provincia ni distrito)
                continue

            name = (row.get("Nombre") or "").strip()
            reniec = (row.get("reniec") or "").strip()
            inei = (row.get("inei") or "").strip()
            code = reniec or inei

            yield {
                "department": department,
                "province": province,
                "district": district,
                "name": name,
                "code": code,
            }


@lru_cache()
def _build_index() -> Dict[str, object]:
    provinces: List[Dict[str, str]] = []
    province_by_value: Dict[str, Dict[str, str]] = {}
    province_by_key: Dict[str, Dict[str, str]] = {}
    districts_by_province: Dict[str, List[Dict[str, str]]] = {}
    district_by_value: Dict[str, Dict[str, str]] = {}
    district_by_keys: Dict[Tuple[str, str], Dict[str, str]] = {}

    for row in _iter_rows():
        department = row["department"]
        province = row["province"]
        district = row["district"]
        code = row["code"]

        province_value = f"{department}|{province}"

        if not district:
            province_record = {
                "value": province_value,
                "label": f"{department} — {province}",
                "department": department,
                "name": province,
                "code": code,
            }
            provinces.append(province_record)
            province_by_value[province_value] = province_record
            province_by_key[_normalize_key(province)] = province_record
            continue

        district_value = f"{province_value}|{district}"
        district_record = {
            "value": district_value,
            "label": district,
            "department": department,
            "province": province,
            "name": district,
            "code": code,
        }
        districts_by_province.setdefault(province_value, []).append(district_record)
        district_by_value[district_value] = district_record
        district_by_keys[(_normalize_key(province), _normalize_key(district))] = district_record

    provinces.sort(key=lambda item: (item["department"], item["name"]))
    for items in districts_by_province.values():
        items.sort(key=lambda item: item["name"])

    return {
        "provinces": provinces,
        "province_by_value": province_by_value,
        "province_by_key": province_by_key,
        "districts_by_province": districts_by_province,
        "district_by_value": district_by_value,
        "district_by_keys": district_by_keys,
    }


def get_province_choices() -> List[Tuple[str, str]]:
    """Retorna una lista de opciones (value, label) para provincias peruanas."""

    index = _build_index()
    return [(record["value"], record["label"]) for record in index["provinces"]]


def get_district_choices(province_value: str) -> List[Tuple[str, str]]:
    """Retorna las opciones de distrito asociadas a una provincia (value, label)."""

    if not province_value:
        return []
    index = _build_index()
    entries = index["districts_by_province"].get(province_value, [])
    return [(record["value"], record["label"]) for record in entries]


def is_valid_province_value(province_value: str) -> bool:
    if not province_value:
        return False
    index = _build_index()
    return province_value in index["province_by_value"]


def is_valid_district_value(district_value: str) -> bool:
    if not district_value:
        return False
    index = _build_index()
    return district_value in index["district_by_value"]


def parse_province_value(province_value: str) -> Tuple[str, str]:
    """Separa el valor de provincia en (departamento, provincia)."""

    parts = [part.strip() for part in (province_value or "").split("|")]
    if len(parts) != 2 or not all(parts):
        raise ValueError("Formato de provincia inválido")
    return parts[0], parts[1]


def parse_district_value(district_value: str) -> Tuple[str, str, str]:
    """Separa el valor de distrito en (departamento, provincia, distrito)."""

    parts = [part.strip() for part in (district_value or "").split("|")]
    if len(parts) != 3 or not all(parts):
        raise ValueError("Formato de distrito inválido")
    return parts[0], parts[1], parts[2]


def find_province_value(province_name: str) -> Optional[str]:
    """Obtiene el `value` correspondiente a un nombre de provincia (insensible a tildes)."""

    if not province_name:
        return None
    index = _build_index()
    record = index["province_by_key"].get(_normalize_key(province_name))
    if record:
        return record["value"]
    return None


def find_district_value(province_value: str, district_name: str) -> Optional[str]:
    """Obtiene el `value` para un distrito dentro de la provincia indicada."""

    if not province_value or not district_name:
        return None
    try:
        _, province_name = parse_province_value(province_value)
    except ValueError:
        return None

    index = _build_index()
    record = index["district_by_keys"].get(
        (_normalize_key(province_name), _normalize_key(district_name))
    )
    if record:
        return record["value"]
    return None


def ensure_district_matches_province(province_value: str, district_value: str) -> bool:
    """Valida que un distrito pertenezca a la provincia seleccionada."""

    if not (is_valid_province_value(province_value) and is_valid_district_value(district_value)):
        return False

    try:
        province_parts = parse_province_value(province_value)
        district_parts = parse_district_value(district_value)
    except ValueError:
        return False

    return province_parts[0] == district_parts[0] and province_parts[1] == district_parts[1]


def get_department_name_for_province(province_name: str) -> Optional[str]:
    """Retorna el nombre del departamento al que pertenece una provincia."""

    if not province_name:
        return None
    index = _build_index()
    record = index["province_by_key"].get(_normalize_key(province_name))
    if record:
        return record["department"]
    return None
