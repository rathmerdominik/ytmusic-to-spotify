def get_spotify_tracks() -> dict:
    return {
        "items": [
            {
                "track": {
                    "name": "Track 1",
                    "artists": [{"name": "Artist 1"}],
                    "album": {"name": "Album 1"},
                    "id": "spotify_track_1",
                }
            },
            {
                "track": {
                    "name": "Track 2",
                    "artists": [{"name": "Artist 2"}],
                    "album": {"name": "Album 2"},
                    "id": "spotify_track_2",
                }
            },
            {
                "track": {
                    "name": "Track 3",
                    "artists": [{"name": "Artist 3"}],
                    "album": {"name": "Album 3"},
                    "id": "spotify_track_3",
                }
            },
            {
                "track": {
                    "name": "Track 4",
                    "artists": [{"name": "Artist 4"}],
                    "album": {"name": "Album 4"},
                    "id": "spotify_track_4",
                }
            },
        ]
    }
