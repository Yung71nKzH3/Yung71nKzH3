import urllib.parse
import urllib.request
import json
import base64

def main():
    print("=== Spotify Refresh Token Helper ===")
    client_id = input("Enter Spotify Client ID: ").strip()
    client_secret = input("Enter Spotify Client Secret: ").strip()
    redirect_uri = input("Enter Redirect URI configured in Developer Dashboard (e.g. https://example.com): ").strip()

    scope = "user-read-currently-playing user-read-recently-played"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)

    print(f"\n1. Open the following URL in your web browser and authorize:\n\n{auth_url}\n")
    print("2. You will be redirected to a new page (which might fail to load - this is normal).")
    print("   Copy the entire URL from the address bar of that page.")
    
    redirected_url = input("\nPaste the redirected URL (or the code parameter value): ").strip()

    code = redirected_url
    if "code=" in redirected_url:
        parsed = urllib.parse.urlparse(redirected_url)
        code_list = urllib.parse.parse_qs(parsed.query).get("code")
        if code_list:
            code = code_list[0]

    if not code:
        print("Error: Could not extract code from the input.")
        return

    # Exchange authorization code for refresh token
    token_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    payload = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            refresh_token = res_body.get("refresh_token")
            print("\n" + "="*40)
            print("SUCCESS! Your credentials have been verified.")
            print(f"Spotify Refresh Token:\n\n{refresh_token}\n")
            print("="*40)
            print("Copy the token above and add it to your GitHub secrets as: SPOTIFY_REFRESH_TOKEN")
    except Exception as e:
        print(f"\nError exchanging code: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8'))

if __name__ == "__main__":
    main()
