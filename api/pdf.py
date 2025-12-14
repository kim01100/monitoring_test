import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

TMP_DIR = "/tmp"

def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": "Method not allowed"
        }

    try:
        payload = json.loads(request.body)
        entries = payload.get("entries", [])
    except Exception:
        return {
            "statusCode": 400,
            "body": "Invalid JSON"
        }

    if not entries:
        return {
            "statusCode": 400,
            "body": "No entries"
        }

    filename = "monitoring.pdf"
    filepath = os.path.join(TMP_DIR, filename)

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

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "filename": filename
        })
    }
