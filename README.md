# Monitoring Library

This repository contains a simple Python library to monitor services and send alerts to a Microsoft Power Automate webhook.

## Usage

```
from monitorlib.monitor import Service, HealthResult, check_services

# Define a health check function

def ping_api():
    # Example health check
    return HealthResult(healthy=True, message="API responded")

services = [
    Service('example_service', ping_api, alert_on_success=False),
]

check_services(services, '<webhook-url>')
```

Each health check function should return a `HealthResult` containing a
`healthy` boolean and an informational `message`.

## Running Tests

Tests are written with `pytest`.

```
pytest
```

## Sending a Test Notification

Run the helper script to send a sample message to your Teams channel using
the configured webhook URL. The script prints a confirmation on success or
the error message returned if the request fails. It looks for a `WEBHOOK_URL`
environment variable but will fall back to the test value defined in
`tests/test_monitor.py`. The notification payload now includes `attachments`
under `body` to match the flow's expectations. If no run appears in your
Power Automate history, double-check the webhook URL and make sure your flow
is configured to read `triggerBody().body.attachments`.

```
python send_teams_notification.py
```

