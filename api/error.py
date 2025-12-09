import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME")  # Monitoring
MONITOR_SECRET = os.environ.get("MONITOR_SECRET")            # 🔐 Secret obligatoire


class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        # 🔐 Sécurité : secret obligatoire
        if self.headers.get("x-monitor-key") != MONITOR_SECRET:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"Unauthorized")
            return

        # Lire JSON Make
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)

        try:
            body = json.loads(raw)
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Invalid JSON: {e}".encode())
            return

        # URL Airtable
        url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }

        # Champs EXACTS pour une erreur
        fields = {
            "Workflow": body.get("Workflow", ""),
            "Module": body.get("Module", ""),
            "Sensor": "🔴 Error",         # 🔥 Icône rouge
            "Status": "🔴 Failed",      # 🔥 Icône rouge
            "Message": body.get("Message", "")
        }

        data = {"fields": fields}
        payload = json.dumps(data).encode()

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            urllib.request.urlopen(req)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Airtable error: {e}".encode())

