import os, requests

GOTENBERG_URL = os.getenv("GOTENBERG_URL", "").rstrip("/")
if not GOTENBERG_URL:
    raise RuntimeError("Falta GOTENBERG_URL")

def html_to_pdf_bytes_gotenberg(html: str) -> bytes:
    files = {"files": ("index.html", html.encode("utf-8"), "text/html")}
    data = {
        "marginTop": "10mm", "marginRight": "10mm",
        "marginBottom": "10mm", "marginLeft": "10mm",
        "printBackground": "true",
        "paperWidth": "8.27", "paperHeight": "11.69"  # A4 en pulgadas
    }
    r = requests.post(f"{GOTENBERG_URL}/forms/chromium/convert/html",
                      files=files, data=data, timeout=60)
    r.raise_for_status()
    return r.content
