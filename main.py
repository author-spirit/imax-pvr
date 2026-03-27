# NOTE, Currently there is no auth for PVR apis or too many restrictions
# Make Friendly requests (keep api calls minimal) before it is stopped.

import requests
from croniter import croniter
from datetime import datetime, timedelta
import time
import loguru
import sys

MY_CITY = "Bengaluru"
FORMAT = "imax"  # imax | pxl | laser | 4dx
SEARCH_STR = "hail mary"
URL = "https://api3.pvrcinemas.com/api/v1/booking/content/mshowtimes"
CRON_ON = False
CRON_EXPRESSION = "* * * * *"  # Run every hour
FETCH_N_DAYS = 3
LOG_FILE = "showtimes.log"

HEADERS = {
    "Content-Type": "application/json",
    "City": MY_CITY,
    "appVersion": "1.0",
    "Platform": "WEBSITE",
}


def setup_logging():
    loguru.logger.remove()
    loguru.logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO")
    loguru.logger.add(LOG_FILE, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", level="INFO", rotation="10 MB", retention="7 days")


def get_date(offset):
    d = datetime.now() + timedelta(days=offset)
    return d.strftime("%Y-%m-%d")


def fetch_showtimes():
    for i in range(FETCH_N_DAYS):
        date = get_date(i)

        payload = {
            "city": MY_CITY,
            # "lat": "",
            # "lng": "",
            "dated": date,
            "experience": FORMAT,
        }

        r = requests.post(URL, json=payload, headers=HEADERS)
        data = r.json()

        loguru.logger.info(f"=== {date} ===")

        for session in data.get("output", {}).get("showTimeSessions", []):
            film = session["movie"].get("filmName", "").lower()
            if SEARCH_STR not in film:
                continue

            for cs in session["movieCinemaSessions"]:
                for exp in cs["experienceSessions"]:
                    if exp["experience"].lower() != "imax":
                        continue

                    # theatre name.
                    loguru.logger.info(cs["cinema"]["name"])

                    for s in exp["shows"]:
                        # only available shows
                        # if s.get("availableSeats", 0) <= 0:
                        #     continue

                        slots = f"  {s['showDate']}  {s['showTime']}  [{s['language']}]  {s['statusTxt']}  ({s['availableSeats']}/{s['totalSeats']} seats)"
                        loguru.logger.info(slots)

def run_cron():
    base_time = datetime.now()
    cron = croniter(CRON_EXPRESSION, base_time)
    next_run_time = cron.get_next(datetime)
    loguru.logger.info(f"Next run scan at: {next_run_time}")
    while True:
        now = datetime.now()
        if now >= next_run_time:
            fetch_showtimes()
            next_run_time = cron.get_next(datetime)
            loguru.logger.info(f"Next scan scheduled at: {next_run_time}")
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    setup_logging()
    if not CRON_ON:
        fetch_showtimes()
        sys.exit()
    
    run_cron()
