import os
import requests
import re
import unicodedata
from dotenv import load_dotenv
from pathlib import Path

load_dotenv() # reads the .env file

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "https://ws.audioscrobbler.com/2.0/"

ALLOWED_TAGS_FILE = "input/allowed_tags"

class LastFMError(Exception):
    pass

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

# Establish tags
def normalize_tag(tag):
    tag = tag.lower().strip()

    tag = unicodedata.normalize("NFKD", tag)
    tag = "".join(c for c in tag if not unicodedata.combining(c))

    tag = re.sub(r"\s+", " ", tag)

    return tag


def load_allowed_tags(filepath=ALLOWED_TAGS_FILE):
    allowed_tags = set()

    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(
            f"No existe {filepath}. Crea el archivo con los tags permitidos."
        )

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            tag = line.strip()

            if not tag:
                continue

            if tag.startswith("#"):
                continue

            allowed_tags.add(normalize_tag(tag))

    return allowed_tags

def get_artist_top_tags(artist_name, limit=10):
    data = lastfm_get({
        "method": "artist.getTopTags",
        "artist": artist_name,
        "autocorrect": 1,
    })

    tags = data.get("toptags", {}).get("tag", [])

    if isinstance(tags, dict):
        tags = [tags]

    allowed_tags = load_allowed_tags()

    clean_tags = []

    for tag in tags:
        name = tag.get("name")

        if not name:
            continue

        name = normalize_tag(name)

        if name not in allowed_tags:
            continue

        if name in clean_tags:
            continue

        clean_tags.append(name)

        if len(clean_tags) >= limit:
            break

    return clean_tags

# Search complete artist
def get_lastfm_artist(artist_name):
    info_data = lastfm_get({
        "method": "artist.getInfo",
        "artist": artist_name,
        "autocorrect": 1,
    })

    artist = info_data.get("artist", {})
    stats = artist.get("stats", {})

    listeners = stats.get("listeners")
    playcount = stats.get("playcount")

    tags = get_artist_top_tags(artist_name, limit=10)

    return {
        "id_lastfm": artist.get("mbid") or None,
        "artist_name_lastfm": artist.get("name") or artist_name,
        "listeners": int(listeners) if listeners else None,
        "playcount": int(playcount) if playcount else None,
        "tags": tags,
        "lastfm_url": artist.get("url"),
    }