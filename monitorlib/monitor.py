from dataclasses import dataclass
from typing import Callable, List, Dict, Any
import json
import urllib.request

@dataclass
class HealthResult:
    """Result object returned from a service health check."""

    healthy: bool
    message: str


@dataclass
class Service:
    name: str
    check_health: Callable[[], HealthResult]
    alert_on_success: bool = False

def send_webhook_alert(
    webhook_url: str, service_name: str, message: str, healthy: bool
) -> None:
    """Send an alert to the Power Automate webhook."""

    status_text = "UP" if healthy else "DOWN"
    card = {
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.3",
            "body": [
                {
                    "type": "TextBlock",
                    "size": "Large",
                    "weight": "Bolder",
                    "text": service_name,
                },
                {"type": "TextBlock", "text": message},
                {"type": "TextBlock", "text": f"Status: {status_text}"},
            ],
        },
    }

    # The Power Automate flow expects attachments under triggerBody().body
    payload = {"body": {"attachments": [card]}}

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        # Consume response to ensure request is sent
        response.read()

def check_services(services: List[Service], webhook_url: str) -> Dict[str, Any]:
    """Run health checks for a list of services and optionally send alerts."""

    statuses: Dict[str, Any] = {}
    for service in services:
        try:
            result = service.check_health()
            healthy = result.healthy
            message = result.message
        except Exception as e:
            healthy = False
            message = str(e)
            statuses[service.name] = {"healthy": healthy, "message": message}
        else:
            statuses[service.name] = {"healthy": healthy, "message": message}

        if not healthy or service.alert_on_success:
            send_webhook_alert(webhook_url, service.name, message, healthy)

    return statuses
