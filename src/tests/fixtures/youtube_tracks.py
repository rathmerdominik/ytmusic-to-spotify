def get_youtube_tracks() -> dict:
    return {
        "tracks": [
            {
                "videoId": "0",
                "videoType": "MUSIC_VIDEO_TYPE_OMV",
                "title": "This should not appear",
                "artists": [{"name": "pleasedont", "id": "dont"}],
                "album": {"name": "dont"},
            },
            {
                "videoId": "1",
                "videoType": "MUSIC_VIDEO_TYPE_OMV",
                "title": "Another Song",
                "artists": [{"name": "Some Artist", "id": "some_id"}],
                "album": {"name": "Some Album"},
            },
            {
                "videoId": "2",
                "videoType": "MUSIC_VIDEO_TYPE_OMV",
                "title": "Amazing Song",
                "artists": [{"name": "Awesome Artist", "id": "awesome_id"}],
                "album": {"name": "Awesome Album"},
            },
            {
                "videoId": "3",
                "videoType": "MUSIC_VIDEO_TYPE_OMV",
                "title": "Classic Tune",
                "artists": [{"name": "Oldie Artist", "id": "oldie_id"}],
                "album": {"name": "Nostalgia Album"},
            },
        ]
    }
