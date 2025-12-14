import os
import json
import base64
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

TMP_DIR = "/tmp"

def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": "Method not allowed"
        }

    try:
        payload = json.loads(request.body)
        logs = payload.get("entries", [])
    except Exception:
        return {
            "statusCode": 400,
            "body": "Invalid JSON"
        }

    if not logs:
        return {
            "statusCode": 400,
            "body": "No entries"
        }

    filename = f"monitoring_{uuid.uuid4()}.pdf"
    filepath = os.path.join(TMP_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, height - 2 * cm, "Monitoring Export")

    y = height - 4 * cm
    c.setFont("Helvetica", 9)

    for log in logs:
        if y < 2 * cm:
            c.showPage()
            c.setFont("Helvetica", 9)
            y = height - 2 * cm

        line = (
            f"{log.get('workflow','')} | "
            f"{log.get('module','')} | "
            f"{log.get('status','')} | "
            f"{log.get('message','')}"
        )

        c.drawString(2 * cm, y, line[:120])
        y -= 0.6 * cm

    c.save()

    with open(filepath, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "filename": filename,
            "file_base64": pdf_base64
        })
    }
