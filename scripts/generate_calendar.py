import datetime
import os
import re

# Try to import holidays
try:
    import holidays
except ImportError:
    holidays = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(BASE_DIR, "README.md")

# 🎈 ADD YOUR CUSTOM HOLIDAYS HERE!
# Format: (month, day): "Holiday Name"
CUSTOM_HOLIDAYS = {
    # --- January ---
    (1, 1): "New Year's Day 🎆",
    (1, 4): "World Braille Day ⠃",
    (1, 25): "Burns Supper 🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    
    # --- February ---
    (2, 2): "World Wetlands Day 🦆",
    (2, 14): "Valentine's Day ❤️",
    (2, 24): "Dragobete 🇷🇴",
    
    # --- March ---
    (3, 1): "St. David's Day 🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    (3, 8): "International Women's Day ♀️",
    (3, 14): "Pi Day 🥧 / White Day 🍬",
    (3, 17): "St. Patrick's Day ☘️",
    (3, 20): "International Day of Happiness 😊",
    
    # --- April ---
    (4, 1): "April Fool's Day 🤡",
    (4, 7): "World Health Day 🩺",
    (4, 9): "National Unicorn Day 🦄",
    (4, 15): "World Art Day 🎨",
    (4, 22): "Earth Day 🌍",
    (4, 23): "World Book Day 📚",
    
    # --- May ---
    (5, 1): "May Day 🌸",
    (5, 4): "Star Wars Day (May the 4th) ✨",
    (5, 20): "World Bee Day 🐝",
    (5, 21): "International Tea Day ☕",
    (5, 25): "Africa Day 🌍",
    
    # --- June ---
    (6, 5): "World Environment Day 🌱",
    (6, 8): "World Oceans Day 🌊",
    (6, 16): "Bloomsday 📖",
    (6, 21): "Summer Solstice ☀️ / World Humanist Day",
    (6, 23): "Olympic Day 🏅",
    
    # --- July ---
    (7, 1): "International Joke Day 😂",
    (7, 7): "World Chocolate Day 🍫",
    (7, 18): "Nelson Mandela Day 🇿🇦",
    (7, 20): "World Chess Day ♟️ / Moon Day 🌕",
    
    # --- August ---
    (8, 12): "International Youth Day 👦👧",
    (8, 13): "International Left-handers Day ✍️",
    (8, 19): "World Humanitarian Day 🤝",
    (8, 22): "[Steam Account Birthday! 🎮](https://steamcommunity.com/id/zfw1ll0w/)",
    
    # --- September ---
    (9, 19): "Talk Like a Pirate Day 🏴‍☠️",
    (9, 21): "International Day of Peace 🕊️",
    (9, 27): "World Tourism Day ✈️",
    
    # --- October ---
    (10, 1): "International Coffee Day ☕",
    (10, 16): "World Food Day 🍎",
    (10, 20): "International Sloth Day 🦥",
    (10, 31): "Halloween 🎃",
    
    # --- November ---
    (11, 4): "King Tut Day ☥",
    (11, 14): "Pickle Day 🥒",
    (11, 19): "World Toilet Day 🚽",
    (11, 21): "World Television Day 📺",
    
    # --- December ---
    (12, 1): "World AIDS Day 🎗️",
    (12, 5): "World Ninja Day 🥷",
    (12, 10): "Human Rights Day ⚖️",
    (12, 25): "Christmas 🎄",
    (12, 31): "New Year's Eve 🥂",
}

# 📅 VARIABLE HOLIDAYS FOR 2026
# (Update these annually!)
VARIABLE_HOLIDAYS_2026 = {
    (2, 17): ["Pancake Day (Shrove Tuesday) 🥞", "Lunar New Year 🧧", "Ramadan Begins ☪️"],
    (4, 5): ["Easter Sunday 🐰"],
    (4, 12): ["Orthodox Easter ⛪"],
    (11, 8): ["Diwali 🪔"],
}



def get_year_progress():
    now = datetime.datetime.now()
    start_of_year = datetime.datetime(now.year, 1, 1)
    end_of_year = datetime.datetime(now.year + 1, 1, 1)
    progress = (now - start_of_year) / (end_of_year - start_of_year)
    return progress

def get_progress_bar(progress, length=20):
    filled_length = int(length * progress)
    bar = "▰" * filled_length + "▱" * (length - filled_length)
    return f"{bar} {progress*100:.1f}%"

def get_holidays(date):
    found_holidays = []
    
    # Check custom holidays
    if (date.month, date.day) in CUSTOM_HOLIDAYS:
        found_holidays.append(CUSTOM_HOLIDAYS[(date.month, date.day)])

    # Check variable holidays for 2026
    if (date.month, date.day) in VARIABLE_HOLIDAYS_2026:
        found_holidays.extend(VARIABLE_HOLIDAYS_2026[(date.month, date.day)])


    if holidays:
        us_holidays = holidays.US()
        if date in us_holidays:
            found_holidays.extend(us_holidays.get_list(date))
    return list(set(found_holidays))

def update_readme():
    now = datetime.datetime.now()
    date_str = now.strftime("%B %d, %Y")
    day_name = now.strftime("%A")
    
    today_holidays = get_holidays(now)
    holiday_text = " • ".join(today_holidays) if today_holidays else "No major holidays today"
    
    progress = get_year_progress()
    progress_bar = get_progress_bar(progress)
    
    last_updated = now.strftime("%H:%M UTC")

    # Calendar Section
    calendar_content = f"### 🗓️ {day_name}, {date_str}\n"
    calendar_content += f"**Today's Holidays:** {holiday_text}\n\n"
    calendar_content += f"**Year Progress:**\n`{progress_bar}`\n"

    # Details Section (including Last Updated)
    details_content = f"\nThis is a dynamic display powered by Python, the `holidays` library, and GitHub Actions.\n"
    details_content += f"**Last updated:** {last_updated}\n"


    if os.path.exists(README_PATH):
        with open(README_PATH, "r", encoding="utf-8") as f:
            readme_data = f.read()
        
        # Replace Calendar Section
        pattern_cal = r"<!-- START_CALENDAR -->.*?<!-- END_CALENDAR -->"
        replacement_cal = f"<!-- START_CALENDAR -->\n{calendar_content}<!-- END_CALENDAR -->"
        new_readme = re.sub(pattern_cal, replacement_cal, readme_data, flags=re.DOTALL)
        
        # Replace Details Section
        pattern_det = r"<!-- START_DETAILS -->.*?<!-- END_DETAILS -->"
        replacement_det = f"<!-- START_DETAILS -->\n{details_content}\n<!-- END_DETAILS -->"
        new_readme = re.sub(pattern_det, replacement_det, new_readme, flags=re.DOTALL)
        
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_readme)

if __name__ == "__main__":
    update_readme()
