from typing import Iterable, Sequence

from django.http import HttpResponse
from openpyxl import Workbook


EXCEL_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _autosize_columns(worksheet, minimum: int = 12) -> None:
    """Ajusta el ancho de las columnas según el contenido."""
    for column_cells in worksheet.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter
        for cell in column_cells:
            value = cell.value
            length = len(str(value)) if value is not None else 0
            if length > max_length:
                max_length = length
        worksheet.column_dimensions[column_letter].width = max(max_length + 2, minimum)


def build_workbook(sheet_title: str, headers: Sequence[str], rows: Iterable[Sequence]) -> Workbook:
    """Crea un Workbook con los encabezados y filas proporcionados."""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet_title
    worksheet.append(headers)

    for row in rows:
        worksheet.append(list(row))

    _autosize_columns(worksheet)
    return workbook


def workbook_to_response(workbook: Workbook, filename: str) -> HttpResponse:
    """Genera una respuesta HTTP con un Workbook listo para descarga."""
    response = HttpResponse(content_type=EXCEL_CONTENT_TYPE)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response
