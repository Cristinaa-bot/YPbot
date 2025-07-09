import os

API_TOKEN = os.getenv("API_TOKEN")
ADMINS = list(map(int, os.getenv("ADMINS").split(",")))
CITIES = os.getenv("CITIES").split(",")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
