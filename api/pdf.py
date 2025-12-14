import os
import json
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

MONITOR_SECRET = os.environ.get("MONITOR_SECRET")
BASE_URL = os.environ.get("BASE_URL")

def handler(request):
    monitor_key = request.headers.get("x-monitor-key")
    if monitor_key != MONITOR_SECRET:
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Unauthorized"})
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed"})
        }

    try:
        payload = json.loads(request.body)
        logs = payload.get("entries", [])
    except Exception:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON"})
        }

    if not logs:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "No entries"})
        }

    filename = f"monitoring_{uuid.uuid4()}.pdf"
    path = f"/tmp/{filename}"

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica", 10)
    y = height - 40

    for log in logs:
        line = f"{log.get('workflow')} | {log.get('module')} | {log.get('status')} | {log.get('message')}"
        c.drawString(40, y, line[:120])
        y -= 15
        if y < 40:
            c.showPage()
            y = height - 40

    c.save()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "pdf_url": f"{BASE_URL}/api/download/{filename}"
        })
    }
