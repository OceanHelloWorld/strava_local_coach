"""One-time Strava OAuth bootstrap (local-loopback flow).

Run once:  python3 scripts/strava_login.py
Requires:  STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET in your environment, and the
app's "Authorization Callback Domain" set to `localhost` at strava.com/settings/api.

Opens your browser, captures the auth code on http://localhost:8721/callback,
exchanges it for tokens, and saves them to the data dir. The rotating refresh
token is persisted; the MCP server refreshes the 6-hour access token automatically.
"""

import os
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

# Make the server/ modules importable.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "server"))
import store  # noqa: E402
import strava_client  # noqa: E402

PORT = 8721
REDIRECT_URI = f"http://localhost:{PORT}/callback"
SCOPE = "read,activity:read_all,profile:read_all"

_result = {}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/callback":
            qs = urllib.parse.parse_qs(parsed.query)
            _result["code"] = (qs.get("code") or [None])[0]
            _result["scope"] = (qs.get("scope") or [""])[0]
            _result["error"] = (qs.get("error") or [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Strava connected. You can close this tab and return to your terminal.</h2>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass


def _serve_until_done(server):
    while not (_result.get("code") or _result.get("error")):
        server.handle_request()


def main() -> int:
    client_id = os.environ.get("STRAVA_CLIENT_ID")
    if not client_id or not os.environ.get("STRAVA_CLIENT_SECRET"):
        print("Set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET first "
              "(create an app at https://www.strava.com/settings/api).")
        return 1

    authorize_url = "https://www.strava.com/oauth/authorize?" + urllib.parse.urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "approval_prompt": "auto",
        "scope": SCOPE,
    })

    server = HTTPServer(("127.0.0.1", PORT), _Handler)
    threading.Thread(target=_serve_until_done, args=(server,), daemon=True).start()

    print("Opening your browser to authorize Strava…")
    print(f"If it doesn't open, visit:\n  {authorize_url}\n")
    webbrowser.open(authorize_url)

    for _ in range(300):  # wait up to ~5 minutes
        if _result.get("code") or _result.get("error"):
            break
        time.sleep(1)
    server.server_close()

    if _result.get("error"):
        print(f"Authorization failed: {_result['error']}")
        return 1
    code = _result.get("code")
    if not code:
        print("No authorization code received (timed out).")
        return 1

    granted = _result.get("scope", "")
    if "activity:read" not in granted:
        print(f"Warning: granted scopes = {granted!r}. Activity read was not granted — "
              "re-run and approve all permissions, or activity tools will fail.")

    try:
        data = strava_client.exchange_code(code)
    except strava_client.StravaError as e:
        print(f"Token exchange failed: {e}")
        return 1

    store.save_tokens({
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": data["expires_at"],
    })
    athlete = data.get("athlete", {})
    name = f"{athlete.get('firstname', '')} {athlete.get('lastname', '')}".strip()
    print(f"Connected{' as ' + name if name else ''}. Tokens saved to {store.data_dir() / 'tokens.json'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
