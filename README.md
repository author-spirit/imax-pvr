## Note
Due to no IMAX shows for `Project Hail Mary` I came up with this script to track the shows PVR apis.
This saved time in manually checking shows in BMS, PVR, District
Make friendly request (every 1-6 hr) as currently no hard restrictions/auth/cloudfare (during test)

## TODO
- Enable Notification alert.

## Installation
```
pip install requests
pip install loguru
```

optional: you can install croniter or remove croniter logic
> pip install croniter


Just run the main.py in background (for cron)
> nohup python3 main.py > /dev/null 2>&1 &

One time run
> python main.py
