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
    (1, 1): "New Year's Day",
    (2, 14): "Valentine's Day",
    (3, 17): "St. Patrick's Day",
    (4, 1): "April Fool's Day",
    (4, 22): "Earth Day",
    (5, 1): "May Day",
    (6, 21): "Summer Solstice",
    (10, 31): "Halloween",
    (12, 25): "Christmas",
    (12, 31): "New Year's Eve",
    # Add yours below:
    # (month, day): "My Birthday! 🎂",
}


def get_year_progress():
    now = datetime.datetime.now()
    start_of_year = datetime.datetime(now.year, 1, 1)
    end_of_year = datetime.datetime(now.year + 1, 1, 1)
    progress = (now - start_of_year) / (end_of_year - start_of_year)
    return progress

def get_progress_bar(progress, length=20):
    filled_length = int(length * progress)
    bar = "█" * filled_length + "░" * (length - filled_length)
    return f"{bar} {progress*100:.1f}%"

def get_holidays(date):
    found_holidays = []
    
    # Check custom holidays
    if (date.month, date.day) in CUSTOM_HOLIDAYS:
        found_holidays.append(CUSTOM_HOLIDAYS[(date.month, date.day)])

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
    details_content = f"This is a dynamic display powered by Python, the `holidays` library, and GitHub Actions.\n"
    details_content += f"**Last updated:** {last_updated}"

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
