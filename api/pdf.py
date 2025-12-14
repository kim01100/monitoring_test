import json
import os
import base64
from http.server import BaseHTTPRequestHandler
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

TMP_DIR = "/tmp"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        payload = json.loads(body)
        entries = payload.get("entries", [])

        filepath = os.path.join(TMP_DIR, "monitoring.pdf")

        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        y = height - 40
        c.setFont("Helvetica", 10)

        for e in entries:
            line = f"{e.get('workflow')} | {e.get('module')} | {e.get('status')} | {e.get('message')}"
            c.drawString(40, y, line[:100])
            y -= 14
            if y < 40:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 40

        c.save()

        with open(filepath, "rb") as f:
            pdf_b64 = base64.b64encode(f.read()).decode()

        response = json.dumps({
            "filename": "monitoring.pdf",
            "content_base64": pdf_b64
        }).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
