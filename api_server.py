import os
from importlib import import_module
from typing import Any, Callable, List

from flask import Flask, request, jsonify

from monitorlib.monitor import Service, check_services

app = Flask(__name__)


def load_callable(path: str) -> Callable[[], Any]:
    """Load a callable from a ``module:function`` style path."""
    module_name, func_name = path.split(":", 1)
    module = import_module(module_name)
    return getattr(module, func_name)


@app.route("/check", methods=["POST"])
def check() -> Any:
    data = request.get_json(force=True)
    services_data = data.get("services", [])
    webhook_url = data.get("webhook_url")

    services: List[Service] = []
    for svc in services_data:
        name = svc["name"]
        path = svc["check"]
        alert_on_success = svc.get("alert_on_success", False)
        health_fn = load_callable(path)
        services.append(Service(name, health_fn, alert_on_success))

    statuses = check_services(services, webhook_url)
    return jsonify(statuses)


def main() -> None:
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


if __name__ == "__main__":
    main()
