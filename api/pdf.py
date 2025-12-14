import json
import base64
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO


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

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 40
    c.setFont("Helvetica", 10)

    for log in logs:
        line = f"{log.get('workflow')} | {log.get('module')} | {log.get('status')} | {log.get('message')}"
        c.drawString(40, y, line[:120])
        y -= 15
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/pdf"
        },
        "body": base64.b64encode(pdf_bytes).decode("utf-8"),
        "isBase64Encoded": True
    }
