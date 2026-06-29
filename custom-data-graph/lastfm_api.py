import os
import requests
from dotenv import load_dotenv

load_dotenv() # reads the .env file

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "https://ws.audioscrobbler.com/2.0/"


class LastFMError(Exception):
    pass


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

# Method to do requests to the API
def lastfm_get(params):
    if not LASTFM_API_KEY:
        raise LastFMError("LASTFM_API_KEY not found on the .env file")

    default_params = {
        "api_key": LASTFM_API_KEY,
        "format": "json",
    }

    response = requests.get(
        BASE_URL,
        params={**default_params, **params},
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    if "error" in data:
        code = data.get("error")
        message = data.get("message")
        raise LastFMError(f"Last.fm error {code}: {message}")

    return data


def get_lastfm_artist(artist_name):
    data = lastfm_get({
        "method": "artist.getInfo",
        "artist": artist_name,
        "autocorrect": 1,
    })

    artist = data.get("artist", {})

    stats = artist.get("stats", {})

    return {
        "id_lastfm": artist.get("mbid") or None,
        "artist_name_lastfm": artist.get("name") or artist_name,
        "listeners": int(stats.get("listeners", 0)) if stats.get("listeners") else None,
        "playcount": int(stats.get("playcount", 0)) if stats.get("playcount") else None,
        "lastfm_url": artist.get("url"),
    }