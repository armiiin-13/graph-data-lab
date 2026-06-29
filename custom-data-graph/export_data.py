import csv
import time
from pathlib import Path

import pandas as pd

from spotify_api import get_spotify_artist
from lastfm_api import get_lastfm_artist


INPUT_FILE = "input/search_data"
OUTPUT_FILE = "output/artists.csv"
ERRORS_FILE = "output/errors.csv"

FINAL_COLUMNS = [
    "id_spoti",
    "id_lastfm",
    "artist_name",
    "listeners",
    "genres",
    "language",
]

def read_artists_txt(filepath):
    artists = []

    with open(filepath, "r", encoding="utf-8") as file:
        reader = csv.reader(file)

        for row in reader:
            if not row:
                continue

            artist_name = row[0].strip()

            if not artist_name or artist_name.startswith("#"):
                continue

            language = row[1].strip() if len(row) > 1 else None

            artists.append({
                "artist_name": artist_name,
                "language": language,
            })

    return artists

# Creates artist's csv row
def combine_artist_data(spotify_data, lastfm_data, artist_input):
    tags = lastfm_data.get("tags") or []

    if isinstance(tags, list):
        genres = ", ".join(tags)
    else:
        genres = tags

    artist_name = (
        spotify_data.get("artist_name_spotify")
        or lastfm_data.get("artist_name_lastfm")
        or artist_input.get("artist_name")
    )

    return {
        "id_spoti": spotify_data.get("id_spoti"),
        "id_lastfm": lastfm_data.get("id_lastfm"),
        "artist_name": artist_name,
        "listeners": lastfm_data.get("listeners"),
        "genres": genres,
        "language": artist_input.get("language"),
    }


def export():
    Path("output").mkdir(exist_ok=True)

    artists = read_artists_txt(INPUT_FILE)

    final_rows = []
    error_rows = []

    for index, artist_input in enumerate(artists, start=1):
        artist_name = artist_input["artist_name"]

        print(f"[{index}/{len(artists)}] Processing: {artist_name}")

        spotify_data = {}
        lastfm_data = {}

        spotify_error = None
        lastfm_error = None

        try:
            spotify_data = get_spotify_artist(artist_name)
        except Exception as e:
            spotify_error = str(e)
            spotify_data = {
                "id_spoti": None,
                "artist_name_spotify": None,
            }

        try:
            lastfm_data = get_lastfm_artist(artist_name)
        except Exception as e:
            lastfm_error = str(e)
            lastfm_data = {
                "id_lastfm": None,
                "artist_name_lastfm": None,
                "listeners": None,
                "tags": [],
            }

        final_row = combine_artist_data(
            spotify_data=spotify_data,
            lastfm_data=lastfm_data,
            artist_input=artist_input,
        )

        final_rows.append(final_row)

        if spotify_error or lastfm_error:
            error_rows.append({
                "artist_name": artist_name,
                "language": artist_input.get("language"),
                "spotify_error": spotify_error,
                "lastfm_error": lastfm_error,
            })

        time.sleep(0.3)

    df = pd.DataFrame(final_rows, columns=FINAL_COLUMNS)

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8"
    )

    print(f"\nCSV saved in: {OUTPUT_FILE}")

    if error_rows:
        errors_df = pd.DataFrame(error_rows)

        errors_df.to_csv(
            ERRORS_FILE,
            index=False,
            encoding="utf-8"
        )

        print(f"Some artist gave errors. Check: {ERRORS_FILE}")


if __name__ == "__main__":
    export()