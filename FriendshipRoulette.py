from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
import argparse
import socket

#!/usr/bin/env python3
"""
Simple single-file website server.

Usage (zsh):
    python3 simple_site.py
Then open http://localhost:8000

This script starts a minimal HTTP server on port 8000 and serves a single-page
HTML site (no external files). Good for demos and local previews.
"""


PORT = 8000

HTML = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Friend Roulette — Demo Site</title>
    <style>
        :root{font-family:system-ui,-apple-system,Segoe UI,Roboto,"Helvetica Neue",Arial}
        body{margin:0;background:#f6f8fa;color:#0b1221;display:flex;align-items:center;justify-content:center;min-height:100vh}
        .card{width:min(900px,96vw);background:white;border-radius:12px;padding:28px;box-shadow:0 6px 24px rgba(11,18,33,.08)}
        header{display:flex;gap:16px;align-items:center}
        .logo{width:56px;height:56px;border-radius:10px;background:linear-gradient(135deg,#6EE7B7,#3B82F6);display:flex;align-items:center;justify-content:center;color:white;font-weight:700}
        h1{margin:0;font-size:1.25rem}
        p.lead{color:#374151;margin:12px 0 20px}
        .grid{display:grid;grid-template-columns:1fr 320px;gap:20px}
        .panel{padding:16px;border-radius:8px;background:#f8fafc}
        .btn{display:inline-block;padding:10px 14px;border-radius:8px;background:#3B82F6;color:white;text-decoration:none}
        footer{margin-top:18px;color:#6b7280;font-size:.9rem}
        label{display:block;font-weight:600;margin-bottom:6px}
        input,textarea,select{width:100%;padding:8px;border-radius:6px;border:1px solid #e5e7eb;background:white}
    </style>
</head>
<body>
    <div class="card" role="main">
        <header>
            <div class="logo">FR</div>
            <div>
                <h1>Friend Roulette — Meetup demo</h1>
                <p class="lead">Convert availability and DMs into meetup suggestions. This static demo shows a simple UI for scheduling and notes.</p>
            </div>
        </header>

        <div class="grid" style="margin-top:18px">
            <section>
                <div class="panel">
                    <h2 style="margin-top:0">People & availability (example)</h2>
                    <p style="margin:.25rem 0 .5rem">This demo is static — in your project, parse CSV responses and compute overlaps server-side.</p>
                    <ul id="people-list" style="padding-left:1.1rem">
                        <li>Alice — Mondays 7am–9am, Wednesdays 3pm–5pm</li>
                        <li>Bob — Mondays 8am–10am, Thursdays 6pm–8pm</li>
                        <li>Chandra — Wednesdays 4pm–6pm, Fridays 1pm–3pm</li>
                    </ul>
                    <p><a class="btn" href="#" id="suggest-btn">Suggest meetup (demo)</a></p>
                </div>

                <div style="margin-top:12px">
                    <h3 style="margin:.25rem 0">Suggested meetup</h3>
                    <div class="panel" id="result">No suggestion yet.</div>
                    <footer>Tip: integrate CSV parsing code from friend-roulette-overlaps.py to produce real suggestions.</footer>
                </div>
            </section>

            <aside>
                <div class="panel">
                    <h3 style="margin-top:0">Quick note</h3>
                    <p class="lead" style="margin:0 .25rem .6rem">This demo is single-file. Replace the client UI with your real endpoints (Uvicorn / instagrapi) when ready.</p>

                    <form id="message-form" onsubmit="event.preventDefault(); sendDemoMessage();">
                        <label for="who">Your name</label>
                        <input id="who" placeholder="e.g. Cooper" required>

                        <label for="note" style="margin-top:8px">Note</label>
                        <textarea id="note" rows="4" placeholder="Optional meeting note"></textarea>

                        <div style="margin-top:10px;display:flex;gap:8px">
                            <button class="btn" type="submit">Send (demo)</button>
                            <button type="button" onclick="clearForm()" style="padding:10px 14px;border-radius:8px;background:#e5e7eb">Clear</button>
                        </div>
                    </form>
                </div>
            </aside>
        </div>
    </div>

    <script>
        function pickDemoSuggestion() {
            return {when: "Monday 8:30am", where: "Tartan Coffee (on-campus)", people: ["Alice", "Bob"]};
        }
        document.getElementById("suggest-btn").addEventListener("click", function(e){
            e.preventDefault();
            const s = pickDemoSuggestion();
            document.getElementById("result").textContent = `Suggested: ${s.when} at ${s.where} — ${s.people.join(", ")}`;
        });

        function sendDemoMessage(){
            const who = document.getElementById("who").value || "Anonymous";
            const note = document.getElementById("note").value || "";
            alert("Demo message sent:\\nFrom: " + who + (note ? "\\nNote: " + note : ""));
            document.getElementById("message-form").reset();
        }
        function clearForm(){ document.getElementById("message-form").reset(); }
    </script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(HTML.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Not found")

    def log_message(self, format, *args):
        # quieter logs
        print(
            "%s - - [%s] %s"
            % (self.client_address[0], self.log_date_time_string(), format % args)
        )


def find_free_port(start=8000, end=8100):
    for p in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Serve a simple demo website on localhost"
    )
    parser.add_argument(
        "--port", "-p", type=int, default=PORT, help="Port to serve on (default 8000)"
    )
    args = parser.parse_args()

    port = args.port
    if port == 0:
        port = find_free_port() or PORT

    server = HTTPServer(("0.0.0.0", port), Handler)
    url = f"http://localhost:{port}/"
    print(f"Serving demo site at {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()