def combine_artist_data(spotify_data, lastfm_data, artist_input):
    tags = lastfm_data.get("tags", [])

    return {
        "id_spoti": spotify_data.get("id_spoti"),
        "id_lastfm": lastfm_data.get("id_lastfm"),
        "artist_name": spotify_data.get("artist_name_spotify")
            or lastfm_data.get("artist_name_lastfm")
            or artist_input.get("artist_name"),
        "listeners": lastfm_data.get("listeners"),
        "genres": ", ".join(tags),
        "language": artist_input.get("language"),
    }