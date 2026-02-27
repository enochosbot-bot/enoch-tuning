#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 flow — captures access token via local callback server
"""
import os, sys, json, secrets, urllib.parse, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

CLIENT_ID = "869fp76go0gr0x"
CLIENT_SECRET = os.environ.get("LINKEDIN_CLIENT_SECRET", "")  # set via env — never hardcode
REDIRECT_URI = "http://localhost:8082/callback"
SCOPES = "w_member_social w_organization_social openid profile"
STATE = secrets.token_urlsafe(16)
TOKEN_FILE = os.path.expanduser("~/.openclaw/workspace/scripts/linkedin-token.json")

captured = {}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if "code" in params:
            code = params["code"][0]
            # Exchange code for token
            data = urllib.parse.urlencode({
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            }).encode()
            req = urllib.request.Request(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            try:
                with urllib.request.urlopen(req) as resp:
                    token_data = json.loads(resp.read())
                    with open(TOKEN_FILE, "w") as f:
                        json.dump(token_data, f, indent=2)
                    captured["token"] = token_data
                    # Save to Keychain
                    access_token = token_data.get("access_token", "")
                    if access_token:
                        import subprocess
                        subprocess.run([
                            "security", "add-generic-password",
                            "-U", "-s", "LINKEDIN_ACCESS_TOKEN",
                            "-a", "enoch", "-w", access_token
                        ], capture_output=True)
                        print(f"\n✅ Token saved to Keychain (LINKEDIN_ACCESS_TOKEN)")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"<h1>LinkedIn connected! You can close this tab.</h1>")
                    print(f"\n✅ Token captured! Access token saved to {TOKEN_FILE}")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {e}".encode())
                print(f"Token exchange failed: {e}")
        elif "error" in params:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Error: {params.get('error')}".encode())
            captured["done"] = True
        else:
            # Ignore bad/preflight requests — keep server alive
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Waiting for LinkedIn callback...")

    def log_message(self, *args):
        pass  # Suppress request logs

auth_url = (
    f"https://www.linkedin.com/oauth/v2/authorization"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&scope={urllib.parse.quote(SCOPES)}"
    f"&state={STATE}"
)

print(f"\n🔗 Open this URL in your browser:\n\n{auth_url}\n")
print("Waiting for authorization...")

server = HTTPServer(("0.0.0.0", 8082), Handler)
while not captured.get("done"):
    server.handle_request()

if captured.get("token"):
    print(f"\n✅ LinkedIn OAuth complete!")
    print(f"Access token: {captured['token'].get('access_token', '')[:30]}...")
else:
    print("\n❌ No token captured")
