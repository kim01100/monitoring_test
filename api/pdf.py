import os
import json
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# =========================
# Environment variables
# =========================
MONITOR_SECRET = os.environ.get("MONITOR_SECRET")
BASE_URL = os.environ.get("BASE_URL")

AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")      # Monitoring
AIRTABLE_TABLE_NAME_2 = os.environ.get("AIRTABLE_TABLE_NAME_2")  # Monitoring_Exports

TMP_DIR = "/tmp"  # compatible Vercel


def handler(request):
    # =========================
    # Security
    # =========================
    auth = request.headers.get("authorization")
    if not auth or auth != f"Bearer {MONITOR_SECRET}":
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

    # =========================
    # Payload
    # =========================
    try:
        payload = json.loads(request.body)
        logs = payload.get("entries", [])
        title = payload.get("title", "Monitoring Report")
    except Exception:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON payload"})
        }

    if not logs:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "No logs provided"})
        }

    # =========================
    # PDF generation
    # =========================
    pdf_id = str(uuid.uuid4())
    filename = f"monitoring_{pdf_id}.pdf"
    filepath = os.path.join(TMP_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, height - 2 * cm, title)

    c.setFont("Helvetica", 9)
    c.drawString(
        2 * cm,
        height - 2.8 * cm,
        f"Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
    )

    y = height - 4 * cm
    c.setFont("Helvetica", 9)

    for log in logs:
        if y < 2 * cm:
            c.showPage()
            c.setFont("Helvetica", 9)
            y = height - 2 * cm

        line = (
            f"[{log.get('date', '')}] "
            f"{log.get('workflow', '')} | "
            f"{log.get('module', '')} | "
            f"{log.get('status', '')} | "
            f"{log.get('message', '')}"
        )

        c.drawString(2 * cm, y, line[:120])
        y -= 0.6 * cm

    c.save()

    # =========================
    # Response
    # =========================
    pdf_url = f"{BASE_URL}/api/download/{filename}"

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "pdf_url": pdf_url,
            "table_source": AIRTABLE_TABLE_NAME,
            "export_table": AIRTABLE_TABLE_NAME_2
        })
    }
