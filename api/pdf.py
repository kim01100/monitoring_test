import json
import base64
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def handler(request):
    if request.method != "POST":
        return {"statusCode": 405, "body": "Method not allowed"}

    data = json.loads(request.body)
    entries = data.get("entries", [])

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 40
    c.setFont("Helvetica", 10)

    for e in entries:
        line = f"{e.get('workflow')} | {e.get('module')} | {e.get('status')} | {e.get('message')}"
        c.drawString(40, y, line[:120])
        y -= 14
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
