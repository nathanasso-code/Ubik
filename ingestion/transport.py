"""Bounded HTTP JSON transport for the independent ingestion subsystem.

No hidden retry on permanent failures; no secrets or response bodies in logs.
"""
import json
import random
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RETRYABLE = {429, 500, 502, 503, 504}


class AcquisitionError(RuntimeError):
    pass


def get_json(url, *, timeout=15, max_attempts=3, max_response_bytes=4_000_000,
             sleep=time.sleep, jitter=random.random, opener=urlopen):
    if type(max_attempts) is not int or not 1 <= max_attempts <= 5:
        raise ValueError("max_attempts must be 1..5")
    if not 1 <= timeout <= 60 or not 1024 <= max_response_bytes <= 10_000_000:
        raise ValueError("Invalid transport limits")
    req = Request(url, headers={"Accept": "application/json",
                                "User-Agent": "Ubik-research-ingestion/0.1"})
    for attempt in range(max_attempts):
        try:
            with opener(req, timeout=timeout) as response:
                content = response.read(max_response_bytes + 1)
                if len(content) > max_response_bytes:
                    raise AcquisitionError("JSON response exceeds configured byte limit")
                return json.loads(content)
        except HTTPError as exc:
            if exc.code not in RETRYABLE or attempt + 1 >= max_attempts:
                raise AcquisitionError(f"HTTP {exc.code}") from exc
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            try:
                delay = min(30, max(0, int(retry_after)))
            except (TypeError, ValueError):
                delay = min(8, 2 ** attempt + jitter())
            sleep(delay)
        except (URLError, TimeoutError, OSError) as exc:
            if attempt + 1 >= max_attempts:
                raise AcquisitionError("Network acquisition failed") from exc
            sleep(min(8, 2 ** attempt + jitter()))
    raise AcquisitionError("Acquisition attempts exhausted")
