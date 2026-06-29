import base64
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

TOKEN_URL = "https://accounts.spotify.com/api/token"
BASE_URL = "https://api.spotify.com/v1"

class SpotifyAPIError(Exception):
    pass

_access_token = None
_token_expires_at = 0


def get_access_token():
    global _access_token, _token_expires_at

    now = time.time()

    if _access_token and now < _token_expires_at:
        return _access_token

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise SpotifyAPIError("SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET are not on the .env file")

    credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "client_credentials",
    }

    response = requests.post(
        TOKEN_URL,
        headers=headers,
        data=data,
        timeout=10
    )

    response.raise_for_status()
    token_data = response.json()

    _access_token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 3600)
    _token_expires_at = now + expires_in - 60

    return _access_token

# Method to do the requests to the API
def spotify_get(endpoint, params=None):
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
    }

    url = f"{BASE_URL}{endpoint}"

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    # Rate limit
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))
        time.sleep(retry_after)

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )

    response.raise_for_status()

    return response.json()


def search_artist(artist_name, market="ES"):
    # Search request
    data = spotify_get(
        "/search",
        params={
            "q": artist_name,
            "type": "artist",
            "limit": 1,
            "market": market,
        }
    )

    artists = data.get("artists", {}).get("items", [])

    if not artists:
        return None

    return artists[0]


def get_artist_by_id(artist_id):
    return spotify_get(f"/artists/{artist_id}")


def get_spotify_artist(artist_name, market="ES"):
    search_result = search_artist(artist_name, market=market)

    if search_result is None:
        return {
            "id_spoti": None,
            "artist_name_spotify": None,
            "genres": [],
            "spotify_followers": None,
            "spotify_popularity": None,
            "spotify_url": None,
        }

    artist_id = search_result["id"]

    artist = get_artist_by_id(artist_id)

    return {
        "id_spoti": artist.get("id"),
        "artist_name_spotify": artist.get("name"),
        "genres": artist.get("genres", []),
        "spotify_followers": artist.get("followers", {}).get("total"),
        "spotify_popularity": artist.get("popularity"),
        "spotify_url": artist.get("external_urls", {}).get("spotify"),
    }
