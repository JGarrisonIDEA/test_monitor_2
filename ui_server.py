import os
import json
from typing import List, Dict, Any
from flask import Flask, render_template, request
import urllib.request

# URL of the monitoring API server
API_URL = os.environ.get("API_URL", "http://localhost:8000/check")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None
    if request.method == "POST":
        webhook_url = request.form.get("webhook_url")
        service_names = request.form.getlist("service_name")
        service_checks = request.form.getlist("service_check")
        alert_flags = request.form.getlist("alert_on_success")

        services: List[Dict[str, Any]] = []
        for name, check, alert in zip(service_names, service_checks, alert_flags):
            if name and check:
                services.append({
                    "name": name,
                    "check": check,
                    "alert_on_success": alert == "on",
                })

        payload = json.dumps({"webhook_url": webhook_url, "services": services}).encode("utf-8")
        req = urllib.request.Request(API_URL, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                results = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            error = str(exc)

    return render_template("index.html", results=results, error=error)

def main() -> None:
    app.run(host="0.0.0.0", port=int(os.environ.get("UI_PORT", 5000)))

if __name__ == "__main__":
    main()
