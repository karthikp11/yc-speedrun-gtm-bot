import json
import http.server
import socketserver
import threading
from typing import Dict, Any

class AgentHealthCheckHandler(http.server.BaseHTTPRequestHandler):
    metrics_provider = None

    def do_GET(self):
        if self.path in ["/healthz", "/metrics"]:
            status_data: Dict[str, Any] = self.metrics_provider() if self.metrics_provider else {"status": "UNKNOWN"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(status_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def start_telemetry_server(port: int, metrics_callback) -> threading.Thread:
    AgentHealthCheckHandler.metrics_provider = staticmethod(metrics_callback)
    server = socketserver.TCPServer(("", port), AgentHealthCheckHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server_thread
