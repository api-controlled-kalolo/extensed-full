# pdf_engine.py
from playwright.sync_api import sync_playwright
import atexit, threading

_playwright = None
_browser = None
_lock = threading.Lock()

def _shutdown():
    global _playwright, _browser
    try:
        if _browser:
            _browser.close()
        if _playwright:
            _playwright.stop()
    finally:
        _browser = None
        _playwright = None

def _get_browser():
    global _playwright, _browser
    if _browser is None:
        with _lock:
            if _browser is None:
                _playwright = sync_playwright().start()
                # Si corres como root (Docker), agrega --no-sandbox
                _browser = _playwright.chromium.launch(headless=True, args=["--no-sandbox"])
                atexit.register(_shutdown)
    return _browser

def html_to_pdf_bytes_playwright(html: str) -> bytes:
    browser = _get_browser()
    context = browser.new_context()
    try:
        page = context.new_page()
        page.set_content(html, wait_until="load")
        pdf = page.pdf(
            format="A4",
            margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
            print_background=True,
        )
        return pdf
    finally:
        context.close()