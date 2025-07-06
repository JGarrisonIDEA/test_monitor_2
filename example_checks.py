from monitorlib.monitor import HealthResult
import urllib.request


def ping_example() -> HealthResult:
    """Simple health check that fetches https://example.com."""
    url = "https://example.com"
    try:
        with urllib.request.urlopen(url) as response:
            response.read()
            status = response.status
    except Exception as exc:
        return HealthResult(healthy=False, message=str(exc))
    return HealthResult(healthy=status == 200, message=f"HTTP {status}")
