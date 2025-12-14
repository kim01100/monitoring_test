import os
import json
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

MONITOR_SECRET = os.environ.get("MONITOR_SECRET", "")
BASE_URL = os.environ.get("BASE_URL", "")
TMP_DIR = "/tmp"


def build_pdf(entries):
    pdf_id = str(uuid.uuid4())
    filename = f"monitoring_{pdf_id}.pdf"
    filepath = os.path.join(TMP_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, height - 2 * cm, "Monitoring Export")

    c.setFont("Helvetica", 9)
    c.drawString(
        2 * cm,
        height - 2.8 * cm,
        f"Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
    )

    y = height - 4 * cm
    c.setFont("Helvetica", 9)

    for log in entries:
        if y < 2 * cm:
            c.showPage()
            c.setFont("Helvetica", 9)
            y = height - 2 * cm

        line = (
            f"{log.get('workflow', '')} | "
            f"{log.get('module', '')} | "
            f"{log.get('status', '')} | "
            f"{log.get('message', '')}"
        )
        c.drawString(2 * cm, y, line[:120])
        y -= 0.6 * cm

    c.save()
    return filename


class Handler(BaseHTTPRequestHandler):
    def _json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        # Security
        key = self.headers.get("x-monitor-key", "")
        if not key or key != MONITOR_SECRET:
            return self._json(401, {"error": "Unauthorized"})

        # Read body
        try:
            length = int(self.headers.get("content-length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw) if raw else {}
        except Exception:
            return self._json(400, {"error": "Invalid JSON"})

        entries = payload.get("entries", [])
        if not isinstance(entries, list) or len(entries) == 0:
            return self._json(400, {"error": "No entries provided"})

        # PDF
        filename = build_pdf(entries)

        # NOTE: lien "placeholder" tant qu'on n'a pas ajouté /api/download
        pdf_url = f"{BASE_URL}/api/download/{filename}" if BASE_URL else filename

        return self._json(200, {"pdf_url": pdf_url})
