import atexit, threading
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

_executor = ThreadPoolExecutor(max_workers=1)  # un hilo dedicado solo para Playwright
_started = threading.Event()
_browser = None
_playwright = None
_lock = threading.Lock()

def _start_browser_in_worker():
    global _playwright, _browser
    _playwright = sync_playwright().start()
    _browser = _playwright.chromium.launch(headless=True, args=["--no-sandbox"])

def _ensure_started():
    if not _started.is_set():
        with _lock:
            if not _started.is_set():
                # iniciar Playwright/Chromium dentro del hilo del executor
                _executor.submit(_start_browser_in_worker).result()
                _started.set()
                atexit.register(_shutdown)

def _shutdown():
    # cerrar dentro del hilo del executor para evitar problemas de thread
    def _close():
        global _playwright, _browser
        try:
            if _browser:
                _browser.close()
            if _playwright:
                _playwright.stop()
        finally:
            _browser = None
            _playwright = None
    try:
        _executor.submit(_close).result(timeout=5)
    except Exception:
        pass

def _render_pdf_in_worker(html: str) -> bytes:
    # ¡OJO! Este código corre SIEMPRE en el hilo del executor
    context = _browser.new_context()
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

def html_to_pdf_bytes_playwright(html: str) -> bytes:
    _ensure_started()
    # ejecuta la tarea en el hilo dedicado (no en el hilo de la request)
    return _executor.submit(_render_pdf_in_worker, html).result()
