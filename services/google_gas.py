import base64, requests
import os

def subir_pdf_a_gas(pdf_bytes: bytes, nombre_pdf: str) -> dict:
    payload = {
        "filename": nombre_pdf,
        "mimeType": "application/pdf",
        "base64": base64.b64encode(pdf_bytes).decode("utf-8"),
    }
    # Puedes pasar el secreto por header o por querystring ?key=
    r = requests.post(
        os.getenv("GAS_ENDPOINT_URL_GESTION_ACTAS"), json=payload,
        headers={"X-Api-Key": os.getenv("GAS_ENDPOINT_APIKEY_GESTION_ACTAS")},
        timeout=30
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"GAS error: {data}")
    return data
