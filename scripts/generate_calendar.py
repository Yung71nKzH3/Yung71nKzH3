import datetime
import os
import json

# Try to import holidays, if not available, we'll use a basic internal list
try:
    import holidays
except ImportError:
    holidays = None

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "assets", "calendar.svg")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def get_year_progress():
    now = datetime.datetime.now()
    start_of_year = datetime.datetime(now.year, 1, 1)
    end_of_year = datetime.datetime(now.year + 1, 1, 1)
    progress = (now - start_of_year) / (end_of_year - start_of_year)
    return progress * 100

def get_holidays(date):
    found_holidays = []
    
    # Internal fallback list for major global/fun holidays
    internal_holidays = {
        (1, 1): "New Year's Day",
        (2, 14): "Valentine's Day",
        (3, 17): "St. Patrick's Day",
        (4, 1): "April Fool's Day",
        (4, 22): "Earth Day",
        (5, 1): "May Day",
        (6, 21): "Summer Solstice",
        (10, 31): "Halloween",
        (12, 25): "Christmas",
        (12, 31): "New Year's Eve"
    }
    
    if (date.month, date.day) in internal_holidays:
        found_holidays.append(internal_holidays[(date.month, date.day)])
    
    if holidays:
        # Check US and Global/Common holidays if possible
        us_holidays = holidays.US()
        if date in us_holidays:
            found_holidays.extend(us_holidays.get_list(date))
            
    return list(set(found_holidays))

def generate_svg():
    now = datetime.datetime.now()
    day = now.strftime("%d")
    month_name = now.strftime("%B")
    year = now.strftime("%Y")
    day_of_week = now.strftime("%A")
    
    today_holidays = get_holidays(now)
    progress = get_year_progress()
    
    # Aesthetic settings
    width = 400
    height = 250
    primary_color = "#818cf8" # Indigo
    bg_color = "#0f172a"      # Slate 900
    text_color = "#f8fafc"    # Slate 50
    
    holiday_text = ""
    if not today_holidays:
        holiday_text = "No major holidays today"
    else:
        holiday_text = " • ".join(today_holidays)
        if len(holiday_text) > 40:
            holiday_text = holiday_text[:37] + "..."

    svg_content = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&amp;family=JetBrains+Mono&amp;display=swap');
        .container {{ font-family: 'Inter', sans-serif; }}
        .date {{ font-size: 80px; font-weight: 700; fill: {text_color}; }}
        .month {{ font-size: 24px; font-weight: 400; fill: {primary_color}; text-transform: uppercase; letter-spacing: 2px; }}
        .day-name {{ font-size: 18px; font-weight: 400; fill: #94a3b8; }}
        .holidays {{ font-size: 14px; fill: #cbd5e1; font-style: italic; }}
        .progress-label {{ font-size: 12px; fill: #64748b; font-family: 'JetBrains Mono', monospace; }}
        .progress-bg {{ fill: #1e293b; rx: 4; }}
        .progress-bar {{ fill: {primary_color}; rx: 4; }}
    </style>
    
    <rect width="100%" height="100%" fill="{bg_color}" rx="16"/>
    
    <!-- Decorative Glow -->
    <defs>
        <filter id="blur" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="15" />
        </filter>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{primary_color};stop-opacity:0.2" />
            <stop offset="100%" style="stop-color:#c084fc;stop-opacity:0.1" />
        </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#grad)" rx="16"/>
    <circle cx="350" cy="50" r="60" fill="{primary_color}" filter="url(#blur)" opacity="0.15"/>

    <g class="container" transform="translate(30, 40)">
        <text y="20" class="month">{month_name} {year}</text>
        <text y="100" class="date">{day}</text>
        <text x="120" y="85" class="day-name">{day_of_week}</text>
        
        <g transform="translate(0, 130)">
            <text y="0" class="holidays">{holiday_text}</text>
        </g>
        
        <!-- Year Progress -->
        <g transform="translate(0, 170)">
            <text y="0" class="progress-label">Year Progress: {progress:.1f}%</text>
            <rect y="10" width="340" height="8" class="progress-bg"/>
            <rect y="10" width="{3.4 * progress}" height="8" class="progress-bar"/>
        </g>
    </g>
    
    <text x="370" y="230" text-anchor="end" style="fill: #334155; font-size: 10px; font-family: 'JetBrains Mono';">Last updated: {now.strftime("%H:%M UTC")}</text>
</svg>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg_content)

if __name__ == "__main__":
    generate_svg()
