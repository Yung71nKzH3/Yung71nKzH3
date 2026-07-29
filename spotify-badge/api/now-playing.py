from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import base64
import os

def get_spotify_access_token(client_id, client_secret, refresh_token):
    token_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req) as response:
        res_body = json.loads(response.read().decode("utf-8"))
        return res_body.get("access_token")

def get_currently_playing(access_token):
    curr_url = "https://api.spotify.com/v1/me/player/currently-playing"
    req = urllib.request.Request(curr_url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                track_data = json.loads(response.read().decode("utf-8"))
                if track_data and track_data.get("is_playing"):
                    return track_data.get("item"), True
    except Exception:
        pass
    
    # Fallback to recently played
    recent_url = "https://api.spotify.com/v1/me/player/recently-played?limit=1"
    req_recent = urllib.request.Request(recent_url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req_recent) as response:
            if response.status == 200:
                recent_data = json.loads(response.read().decode("utf-8"))
                items = recent_data.get("items")
                if items:
                    return items[0].get("track"), False
    except Exception:
        pass
    return None, False

def get_base64_image(url):
    if not url:
        return ""
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            return "data:image/jpeg;base64," + base64.b64encode(response.read()).decode("utf-8")
    except Exception:
        return ""

def escape_xml(text):
    if not text:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

def generate_svg(track, is_playing):
    if not track:
        # Offline SVG
        return """<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100">
            <rect x="0.5" y="0.5" width="399" height="99" rx="8" fill="#181818" stroke="#333" />
            <text x="20" y="55" fill="#aaa" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="14" font-weight="bold">🎵 Spotify Offline</text>
            <text x="20" y="75" fill="#666" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="12">Not listening to anything right now</text>
        </svg>"""

    name = escape_xml(track.get("name"))
    artists = escape_xml(", ".join([a.get("name") for a in track.get("artists", [])]))
    album = track.get("album", {})
    images = album.get("images", [])
    album_art_url = images[0].get("url") if images else ""
    
    # Fetch and Base64 encode the album art so it renders inside GitHub's camo proxy
    album_art_base64 = get_base64_image(album_art_url)
    
    status_text = "Currently Playing" if is_playing else "Recently Played"
    status_color = "#1db954" if is_playing else "#aaa"

    # Animated bars indicator (only if currently playing)
    visualizer_svg = ""
    if is_playing:
        visualizer_svg = """
        <g transform="translate(360, 20)">
            <rect class="bar" x="0" y="2" width="3" height="12" fill="#1db954">
                <animate attributeName="height" values="4;16;4" dur="0.8s" repeatCount="indefinite" />
                <animate attributeName="y" values="14;2;14" dur="0.8s" repeatCount="indefinite" />
            </rect>
            <rect class="bar" x="5" y="6" width="3" height="8" fill="#1db954">
                <animate attributeName="height" values="2;16;2" dur="0.5s" repeatCount="indefinite" />
                <animate attributeName="y" values="16;2;16" dur="0.5s" repeatCount="indefinite" />
            </rect>
            <rect class="bar" x="10" y="4" width="3" height="10" fill="#1db954">
                <animate attributeName="height" values="3;16;3" dur="0.7s" repeatCount="indefinite" />
                <animate attributeName="y" values="15;2;15" dur="0.7s" repeatCount="indefinite" />
            </rect>
        </g>
        """

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100">
        <style>
            .track-name {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                fill: #ffffff;
            }}
            .artist-name {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 12px;
                fill: #aaaaaa;
            }}
            .status-lbl {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 10px;
                font-weight: bold;
                fill: {status_color};
            }}
        </style>
        <rect x="0.5" y="0.5" width="399" height="99" rx="8" fill="#181818" stroke="#333" />
        <clipPath id="album-clip">
            <rect x="10" y="10" width="80" height="80" rx="6" />
        </clipPath>
        
        <!-- Album Art -->
        {f'<image href="{album_art_base64}" x="10" y="10" width="80" height="80" clip-path="url(#album-clip)" />' if album_art_base64 else '<rect x="10" y="10" width="80" height="80" rx="6" fill="#333" />'}
        
        <!-- Texts -->
        <text x="105" y="30" class="status-lbl">{status_text.upper()}</text>
        <text x="105" y="52" class="track-name">{name}</text>
        <text x="105" y="72" class="artist-name">{artists}</text>
        
        <!-- Visualizer -->
        {visualizer_svg}
    </svg>"""

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        refresh_token = os.environ.get("SPOTIFY_REFRESH_TOKEN")

        track = None
        is_playing = False

        if client_id and client_secret and refresh_token:
            try:
                access_token = get_spotify_access_token(client_id, client_secret, refresh_token)
                track, is_playing = get_currently_playing(access_token)
            except Exception as e:
                print("Error fetching Spotify data in handler:", e)

        svg_content = generate_svg(track, is_playing)

        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(svg_content.encode("utf-8"))
