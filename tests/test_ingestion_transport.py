import io
import json
import unittest
from urllib.error import HTTPError
from ingestion.transport import get_json, AcquisitionError


class Response:
    def __init__(self, payload):
        self.stream = io.BytesIO(payload)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def read(self, n):
        return self.stream.read(n)


class TransportTests(unittest.TestCase):
    def test_success(self):
        result = get_json("https://example.org", opener=lambda *_args, **_kwargs: Response(b'{"ok":true}'))
        self.assertTrue(result["ok"])

    def test_429_retries_and_honors_retry_after(self):
        attempts, delays = [], []
        def opener(*_args, **_kwargs):
            attempts.append(1)
            if len(attempts) == 1:
                raise HTTPError("https://example.org", 429, "Rate limited", {"Retry-After": "2"}, None)
            return Response(b'{"ok":1}')
        result = get_json("https://example.org", opener=opener, sleep=delays.append)
        self.assertEqual(result["ok"], 1)
        self.assertEqual(delays, [2])

    def test_permanent_http_error_not_retried(self):
        attempts = []
        def opener(*_args, **_kwargs):
            attempts.append(1)
            raise HTTPError("https://example.org", 403, "Forbidden", {}, None)
        with self.assertRaises(AcquisitionError):
            get_json("https://example.org", opener=opener, sleep=lambda _: None)
        self.assertEqual(len(attempts), 1)

    def test_response_size_cap(self):
        with self.assertRaises(AcquisitionError):
            get_json("https://example.org", max_response_bytes=1024,
                     opener=lambda *_args, **_kwargs: Response(b"x" * 1025))


if __name__ == "__main__":
    unittest.main()
