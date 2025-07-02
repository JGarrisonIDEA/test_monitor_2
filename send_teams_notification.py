import os
import sys

from monitorlib.monitor import send_webhook_alert


def main() -> None:
    # Prefer the WEBHOOK_URL environment variable but fall back to the
    # constant used in the tests so the script works out of the box.
    webhook_url = os.environ.get("WEBHOOK_URL")

    if not webhook_url:
        try:
            from tests.test_monitor import WEBHOOK_URL as TEST_WEBHOOK_URL
        except Exception:
            TEST_WEBHOOK_URL = None
        webhook_url = TEST_WEBHOOK_URL

    if not webhook_url:
        print("Usage: python send_teams_notification.py <webhook_url>")
        print("Or set WEBHOOK_URL environment variable")
        sys.exit(1)

    try:
        send_webhook_alert(
            webhook_url, "Test Notification", "This is a test message", True
        )
    except Exception as exc:
        print(f"Failed to send notification: {exc}")
    else:
        print("Notification sent")


if __name__ == "__main__":
    main()
