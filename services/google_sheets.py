import os, json
from typing import List, Any, Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES_READONLY = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SCOPES_READWRITE = ["https://www.googleapis.com/auth/spreadsheets"]

def _build_credentials(read_write: bool):
    scopes = SCOPES_READWRITE if read_write else SCOPES_READONLY
    # 1) Credenciales por contenido JSON (prod)
    sa_json = os.getenv("GCP_SA_JSON")
    if sa_json:
        info = json.loads(sa_json)
        return service_account.Credentials.from_service_account_info(info, scopes=scopes)
    # 2) Credenciales por ruta a archivo (dev)
    sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if sa_path:
        return service_account.Credentials.from_service_account_file(sa_path, scopes=scopes)
    raise RuntimeError("Faltan credenciales: define GCP_SA_JSON o GOOGLE_APPLICATION_CREDENTIALS")

def _service(read_write: bool):
    creds = _build_credentials(read_write)
    return build("sheets", "v4", credentials=creds).spreadsheets()

# ===== Lectura =====
def read_range(spreadsheet_id: str, range_name: str) -> List[List[Any]]:
    """Lee un rango (ej: 'Hoja1!A2:D100')."""
    res = _service(False).values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    return res.get("values", [])

def read_ranges(spreadsheet_id: str, ranges: List[str]) -> Dict[str, List[List[Any]]]:
    """Lee varios rangos en una sola llamada (batchGet)."""
    res = _service(False).values().batchGet(spreadsheetId=spreadsheet_id, ranges=ranges).execute()
    out = {}
    for vr in res.get("valueRanges", []):
        out[vr.get("range", "")] = vr.get("values", [])
    return out

# ===== Escritura =====
def write_range(spreadsheet_id: str, range_name: str, values: List[List[Any]], value_input="RAW") -> int:
    """Escribe un rango (reemplaza celdas)."""
    res = _service(True).values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption=value_input,
        body={"values": values},
    ).execute()
    return int(res.get("updatedCells", 0))

def write_ranges(spreadsheet_id: str, data: Dict[str, List[List[Any]]], value_input="RAW") -> int:
    """Escribe varios rangos (batchUpdate). data = { 'Hoja1!A2:D2': [[...]], 'Hoja2!A1:B1': [[...]] }"""
    data_list = [{"range": k, "values": v} for k, v in data.items()]
    res = _service(True).values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"valueInputOption": value_input, "data": data_list},
    ).execute()
    return int(res.get("totalUpdatedCells", 0))

def append_rows(spreadsheet_id: str, range_name: str, rows: List[List[Any]], value_input="RAW") -> int:
    """Agrega filas al final del rango (append)."""
    res = _service(True).values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,  # ej: 'Hoja1!A:Z'
        valueInputOption=value_input,
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()
    updates = res.get("updates", {})
    return int(updates.get("updatedCells", 0))
