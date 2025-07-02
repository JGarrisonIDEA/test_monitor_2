from unittest import mock
import os
import sys
import json

# Ensure the package can be imported when running tests directly on Windows
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from monitorlib.monitor import (
    Service,
    HealthResult,
    send_webhook_alert,
    check_services,
)

WEBHOOK_URL = "https://prod-94.westus.logic.azure.com:443/workflows/05433b6b6a0c46e4bcf1eaa6223186e8/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=zG3QskuPLy-muAWRZnfXr__apYD_1nO1i90o_IYbUBQ"


def test_send_webhook_alert():
    with mock.patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value.read.return_value = b""
        with mock.patch("urllib.request.Request") as Request:
            send_webhook_alert(WEBHOOK_URL, "service", "msg", True)
            assert urlopen.called
            data = json.loads(Request.call_args[1]["data"].decode())
            card_body = data["body"]["attachments"][0]["content"]["body"]
            assert card_body[0]["text"] == "service"
            assert "Status: UP" in card_body[2]["text"]


def test_check_services_alerts_on_conditions():
    service_ok = Service(
        "good_service",
        lambda: HealthResult(True, "ok"),
        alert_on_success=True,
    )
    service_bad = Service("bad_service", lambda: HealthResult(False, "fail"))

    with mock.patch('monitorlib.monitor.send_webhook_alert') as alert:
        statuses = check_services([service_ok, service_bad], WEBHOOK_URL)
        assert statuses["good_service"]["healthy"] is True
        assert statuses["good_service"]["message"] == "ok"
        assert statuses["bad_service"]["healthy"] is False
        assert statuses["bad_service"]["message"] == "fail"
        # Should be called twice: once for each service
        assert alert.call_count == 2


def test_check_services_handles_exceptions():
    def bad():
        raise RuntimeError("boom")

    service = Service("explode", bad)

    with mock.patch("monitorlib.monitor.send_webhook_alert") as alert:
        statuses = check_services([service], WEBHOOK_URL)
        assert statuses["explode"]["healthy"] is False
        assert "boom" in statuses["explode"]["message"]
        alert.assert_called_once_with(WEBHOOK_URL, "explode", "boom", False)


def test_check_services_no_alert_when_all_ok():
    service1 = Service("svc1", lambda: HealthResult(True, "ok"))
    service2 = Service("svc2", lambda: HealthResult(True, "fine"))

    with mock.patch("monitorlib.monitor.send_webhook_alert") as alert:
        statuses = check_services([service1, service2], WEBHOOK_URL)
        assert statuses["svc1"]["healthy"] is True
        assert statuses["svc2"]["healthy"] is True
        alert.assert_not_called()
