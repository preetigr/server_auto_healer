from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import sys
import time
import threading

class AppHandler(BaseHttpRequestHandler):
    def do_get(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"System is Healthy & OK!")
        elif self.path == "/crash":
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Simulating a crash. System is unhealthy.. \n")
            self.wfile.flush()

            #kill the container process after replying
            def kill_self():
                time.sleep(0.5)
                os._exit(1)
            threading.Thread(target=kill_self).start()
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print("Server on port 8080....", flush=True)
    server = HTTPServer(("0.0.0.0", 8080), AppHandler)
    server.serve_forever()
