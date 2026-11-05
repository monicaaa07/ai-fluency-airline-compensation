#!/usr/bin/env python3
"""Side-by-side visual console for the AI Fluency demo.

Serves one web page that sends the same situations to two running copies of the
airline service (Run A and Run B) and shows what each one did.

It only forwards requests. It does not change either app, and it needs nothing
beyond the Python standard library.

    python3 demo/visual/console.py
    python3 demo/visual/console.py --a http://127.0.0.1:8001 --b http://127.0.0.1:8002 --port 9000

Then open http://127.0.0.1:9000

Safety: it listens on 127.0.0.1 only, and it forwards only to the two addresses
you gave it, so it cannot be used to reach anything else.
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGE = Path(__file__).with_name("index.html")
FORWARDED_REQUEST_HEADERS = ("X-Staff-Id", "Content-Type")
UPSTREAM_TIMEOUT_SECONDS = 10


def make_handler(targets: dict):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # keep the terminal quiet
            pass

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, status: int, payload: dict) -> None:
            self._send(status, json.dumps(payload).encode(), "application/json")

        def _proxy(self) -> None:
            # /api/<a|b>/<rest...>  ->  <target>/<rest...>
            parts = self.path.split("/", 3)  # ['', 'api', side, rest]
            side = parts[2].split("?")[0] if len(parts) > 2 else ""
            rest = parts[3] if len(parts) > 3 else ""
            if side not in targets:
                self._send_json(404, {"proxy_error": "Unknown side. Use /api/a/... or /api/b/..."})
                return
            url = targets[side].rstrip("/") + "/" + rest
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else None
            headers = {h: self.headers[h] for h in FORWARDED_REQUEST_HEADERS if self.headers.get(h)}
            request = urllib.request.Request(url, data=body, method=self.command, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=UPSTREAM_TIMEOUT_SECONDS) as response:
                    self._send(
                        response.status,
                        response.read(),
                        response.headers.get("Content-Type", "application/json"),
                    )
            except urllib.error.HTTPError as error:  # 4xx and 5xx are real answers, pass them on
                self._send(error.code, error.read(), error.headers.get("Content-Type", "application/json"))
            except Exception as error:  # server not running, timed out, and so on
                self._send_json(502, {"proxy_error": f"Could not reach {targets[side]}: {error}"})

        def do_GET(self) -> None:
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif path == "/config":
                self._send_json(200, targets)
            elif path.startswith("/api/"):
                self._proxy()
            else:
                self._send_json(404, {"error": "Not found"})

        def do_POST(self) -> None:
            if self.path.startswith("/api/"):
                self._proxy()
            else:
                self._send_json(404, {"error": "Not found"})

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--a", default="http://127.0.0.1:8001", help="Run A server address")
    parser.add_argument("--b", default="http://127.0.0.1:8002", help="Run B server address")
    parser.add_argument("--port", type=int, default=9000, help="port for this console")
    args = parser.parse_args()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler({"a": args.a, "b": args.b}))
    print(f"Console ready:  http://127.0.0.1:{args.port}")
    print(f"  Run A server: {args.a}")
    print(f"  Run B server: {args.b}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
