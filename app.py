import os
import spotipy  # type: ignore
import ytmusicapi  # type: ignore

from typing import List

from termcolor import cprint

from librespot.core import Session  # type: ignore

CLEANUP_FIRST = True  # Delete entire spotify library beforehand
DIRTY_SEARCH_ON_MULTIPLE = False  # Allow dirty searching if no match was found for file


def spotify_setup() -> spotipy.Spotify:
    if os.path.isfile("credentials.json"):
        try:
            session = Session.Builder().stored_file().create()
        except RuntimeError:
            pass
    else:
        while True:
            user_name = input("Spotify Username: ")
            password = input("Spotify Password: ")
            try:
                session = Session.Builder().user_pass(user_name, password).create()
            except RuntimeError:
                print("Wrong credentials!")
                pass
            break
    token = session.tokens().get_token(
        "user-library-read", "user-library-modify", "playlist-modify-private"
    )

    sp = spotipy.Spotify(auth=token.access_token)

    if CLEANUP_FIRST:
        while True:
            # Cleanup existing tracks
            items = sp.current_user_saved_tracks(limit=50)["items"]
            if not items:
                break
            for item in items:
                sp.current_user_saved_tracks_delete([item["track"]["id"]])

    return sp


def youtube_music_setup() -> ytmusicapi.YTMusic:
    if not os.path.isfile("oauth.json"):
        ytmusicapi.setup_oauth(filepath="oauth.json", open_browser=True)

    return ytmusicapi.YTMusic("oauth.json")


def sync_youtube_to_spotify(
    ytmusic: ytmusicapi.YTMusic, spotify: spotipy.Spotify
) -> None:
    not_found = []
    duplicates = []
    added = []
    errors = []
    reversed_tracks: List[dict] = []
    # This is a hard limit of Youtube Music. 5000 max liked tracks lol
    for yt_track in ytmusic.get_liked_songs(5000)["tracks"]:
        reversed_tracks.insert(0, yt_track)

    for yt_track in reversed_tracks:
        if yt_track["videoType"] == "MUSIC_VIDEO_TYPE_ATV":
            track_name = yt_track["title"]
            track_artist = yt_track["artists"][0]["name"]
            track_album = yt_track["album"]["name"]

            results = spotify.search(
                f"track:{track_name} artist:{track_artist} album:{track_album}"
            )

            tracks = results["tracks"]["items"]
            
            if len(tracks) == 0:
                if DIRTY_SEARCH_ON_MULTIPLE:
                    cprint(
                        f"Dirty search for {track_name}' with artist '{track_artist}'!",
                        "yellow",
                        "on_light_grey",
                    )
                    tracks = spotify.search(
                        f"{track_name} {track_artist} {track_album}"
                    )["tracks"]["items"]

            if (
                len(tracks) == 0
            ):
                cprint(
                    f"'{track_name}' with artist '{track_artist}' has no tracks matched!",
                    "yellow",
                )
                not_found.append(
                    f"Name: {track_name}, Artist: {track_artist}, Album: {track_album}"
                )
                continue

            if len(tracks) > 1:
                cprint(
                    f"{track_name} with artist {track_artist} has multiple tracks matched. Will sync first one",
                    "blue",
                )

                print("------------------------------")
                for duplicate_track in tracks:
                    print(
                        f'Found: Track Name: {duplicate_track["name"]}, Artist: {duplicate_track["artists"][0]["name"]}, Album: {duplicate_track["album"]["name"]}'
                    )
                print("------------------------------")
                duplicates.append(
                    f"Name: {track_name}, Artist: {track_artist}, Album: {track_album}"
                )
            try:
                spotify.current_user_saved_tracks_add([tracks[0]["id"]])
                added.append(
                    f"Name: {track_name}, Artist: {track_artist}, Album: {track_album}"
                )
            except Exception as e:
                cprint(f"Error occured! Message: {e}", "red")
                errors.append(str(e))
                continue

    with open("added.log", "w") as file:
        for add in added:
            file.write(f"{add}\n")

    with open("duplicates.log", "w") as file:
        for duplicate in duplicates:
            file.write(f"{duplicate}\n")

    with open("not_found.log", "w") as file:
        for not_f in not_found:
            file.write(f"{not_f}\n")

    with open("errors.log", "w") as file:
        for error in errors:
            file.write(f"{error}\n")


if __name__ == "__main__":
    if os.name == "nt":
        os.system("ansi")

    spotify = spotify_setup()
    ytmusic = youtube_music_setup()
    sync_youtube_to_spotify(ytmusic, spotify)
