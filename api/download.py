import os
import base64

TMP_DIR = "/tmp"

def handler(request):
    filename = request.query.get("file")

    if not filename:
        return {
            "statusCode": 400,
            "body": "Missing file parameter"
        }

    filepath = os.path.join(TMP_DIR, filename)

    if not os.path.exists(filepath):
        return {
            "statusCode": 404,
            "body": "File not found"
        }

    with open(filepath, "rb") as f:
        content = f.read()

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/pdf",
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
        "body": base64.b64encode(content).decode("utf-8"),
        "isBase64Encoded": True
    }
