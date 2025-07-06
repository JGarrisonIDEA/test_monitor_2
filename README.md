# Monitoring Library

This repository contains a simple Python library to monitor services and send alerts to a Microsoft Power Automate webhook.

## Usage

```
from monitorlib.monitor import Service, HealthResult, check_services
from example_checks import ping_example

# ``ping_example`` performs a real HTTP GET request to ``https://example.com``
# and returns a ``HealthResult`` based on the response status.

services = [
    Service('example_service', ping_example, alert_on_success=False),
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


## Running the API Server

A small Flask application is provided in `api_server.py` to expose the
`check_services` function over HTTP. Install Flask and then run the server:

```bash
pip install flask
python api_server.py  # listens on port 8000
```

If you prefer the `flask run` command, set the `FLASK_APP` environment

variable and specify the host and port. Binding to `0.0.0.0` allows
access from outside the local machine (useful if you're running in WSL
or a container):

```bash
FLASK_APP=api_server.py flask run --host 0.0.0.0 -p 8000

```

Send a POST request with the webhook URL and service definitions. Each
service includes a dotted `module:function` path for its health check.

```bash
curl -X POST http://localhost:8000/check \
  -H 'Content-Type: application/json' \
  -d '{
        "webhook_url": "<webhook-url>",
        "services": [
          {"name": "example_service", "check": "example_checks:ping_example", "alert_on_success": false}
        ]
      }'
```


Replace `example_checks:ping_example` with the path to your own health check
function. If the module or function cannot be imported, the server responds
with `400 Bad Request` and an error message.


The API will return a JSON object mapping service names to their status.
