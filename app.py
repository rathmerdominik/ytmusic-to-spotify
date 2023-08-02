import os
import sys
import spotipy  # type: ignore
import ytmusicapi  # type: ignore

from typing import List, Union

from termcolor import cprint

from librespot.core import Session  # type: ignore

CLEANUP_FIRST = True  # Delete entire spotify library beforehand
DIRTY_SEARCH_ON_NOT_FOUND = (
    False  # Allow dirty searching if no match was found for file
)
USER_CHOICE_ON_MULTIPLE = (
    True  # Allow the user to choose when multiple options have been found
)


def write_log(location: str, log_messages: List[str]) -> None:
    with open(location, "w") as file:
        for log_message in log_messages:
            file.write(f"{log_message}\n")


def cleanup_spotify(spotify: spotipy.Spotify) -> None:
    while True:
        # Cleanup existing tracks
        items = spotify.current_user_saved_tracks(limit=50)["items"]
        if not items:
            break
        for item in items:
            spotify.current_user_saved_tracks_delete([item["track"]["id"]])


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

    spotify = spotipy.Spotify(auth=token.access_token)

    if CLEANUP_FIRST:
        cleanup_spotify(spotify)

    return spotify


def youtube_music_setup() -> ytmusicapi.YTMusic:
    if not os.path.isfile("oauth.json"):
        ytmusicapi.setup_oauth(filepath="oauth.json", open_browser=True)

    return ytmusicapi.YTMusic("oauth.json")


def handle_not_found(
    track_name: str, track_artist: str, track_album: str, spotify: spotipy.Spotify
) -> Union[dict, bool]:
    tracks = {}
    if DIRTY_SEARCH_ON_NOT_FOUND:
        cprint(
            f"Dirty search for {track_name}' with artist '{track_artist}'!",
            "yellow",
            "on_light_grey",
        )
        tracks = spotify.search(f"{track_name} {track_artist} {track_album}")["tracks"][
            "items"
        ]

        return tracks if len(tracks) > 0 else False

    else:
        cprint(
            f"'{track_name}' with artist '{track_artist}' has no tracks matched!",
            "yellow",
        )
        return False


def duplicate_choice(
    spotify_tracks: List[dict],
    track_name: str,
    track_artist: str,
    track_album: str,
    spotify: spotipy.Spotify,
) -> Union[List[dict], bool]:
    LINE_UP = "\033[1A"
    LINE_CLEAR = "\x1b[2K"

    while True:
        choice = input(
            f"\n[1 - {len(spotify_tracks)}] => Track number \
                        \n[s] => Search for a track \
                        \n[x] => Exit the program \
                        \n[c] => Skip this song \
                        \nSelect an option > $  "
        )

        for i in range(6):
            print(LINE_UP, end=LINE_CLEAR)
        try:
            return [spotify_tracks[int(choice)]]
        except Exception:
            if choice == "s":
                while True:
                    try:
                        search_q = input(
                            "Please enter search query or CTRL+C to cancel > "
                        )

                        tracks = spotify.search(search_q)["tracks"]["items"]
                        print(LINE_UP, end=LINE_CLEAR)
                        handle_duplicates(
                            tracks, track_name, track_artist, track_album, spotify
                        )
                        break
                    except KeyboardInterrupt:
                        print(LINE_UP, end=LINE_CLEAR)
                        print(LINE_UP, end=LINE_CLEAR)
                        break
                break
            elif choice == "x":
                print("Closing the program!")
                sys.exit(0)
                pass

            elif choice == "c":
                return False

            else:
                print("Wrong input! Please select one of the following:")


def handle_duplicates(
    spotify_tracks: List[dict],
    track_name: str,
    track_artist: str,
    track_album: str,
    spotify: spotipy.Spotify,
) -> Union[List[dict], bool]:
    first_match_string = ""
    if not USER_CHOICE_ON_MULTIPLE:
        first_match_string = (
            " Will match the first one as user choice has not been enabled!"
        )

    cprint(
        f"{track_name} with artist {track_artist} and album {track_album} has multiple tracks matched.{first_match_string}",
        "blue",
    )

    print("------------------------------")
    for idx, duplicate_track in enumerate(spotify_tracks, 1):
        print(
            f'{idx} Found: Track Name: {duplicate_track["name"]}, Artist: {duplicate_track["artists"][0]["name"]}, Album: {duplicate_track["album"]["name"]}'
        )
    print("------------------------------")

    if USER_CHOICE_ON_MULTIPLE:
        chosen_track = duplicate_choice(
            spotify_tracks, track_name, track_artist, track_album, spotify
        )

    else:
        chosen_track = spotify_tracks
    return chosen_track


def sync_youtube_to_spotify(
    ytmusic: ytmusicapi.YTMusic, spotify: spotipy.Spotify
) -> None:
    added = []
    errors = []
    not_found = []
    duplicates = []

    reversed_tracks: List[dict] = []

    # This is a hard limit of Youtube Music. 5000 max liked tracks lol
    for yt_track in ytmusic.get_liked_songs(5000)["tracks"]:
        reversed_tracks.insert(0, yt_track)

    for yt_track in reversed_tracks:
        try:
            if yt_track["videoType"] == "MUSIC_VIDEO_TYPE_ATV":
                track_name = yt_track["title"]
                track_artist = yt_track["artists"][0]["name"]
                track_album = yt_track["album"]["name"]

                results = spotify.search(
                    f"track:{track_name} artist:{track_artist} album:{track_album}"
                )

                spotify_tracks = results["tracks"]["items"]

                if len(spotify_tracks) == 0:
                    spotify_tracks = handle_not_found(
                        track_name, track_artist, track_album, spotify
                    )
                    if not spotify_tracks:
                        not_found.append(
                            f"Name: {track_name}, Artist: {track_artist}, Album: {track_album}"
                        )
                        continue

                if len(spotify_tracks) > 1:
                    spotify_tracks = handle_duplicates(
                        spotify_tracks, track_name, track_artist, track_album, spotify
                    )
                    if not spotify_tracks:
                        continue
                    duplicates.append(
                        f"Name: {track_name}, Artist: {track_artist}, Album: {track_album}"
                    )

                spotify.current_user_saved_tracks_add([spotify_tracks[0]["id"]])
                cprint(
                    f"Found and added track for {track_name} with artist {track_artist} and album {track_album}",
                    "green",
                )
                added.append(
                    f"Name: {track_name}, Artist: {track_artist}, Album: {track_album}"
                )
        except Exception as e:
            cprint(f"Error occured! Message: {e}", "red")
            errors.append(str(e))
            continue

    write_log("added.log", added)
    write_log("duplicates.log", duplicates)
    write_log("errors.log", errors)
    write_log("not_found.log", not_found)


if __name__ == "__main__":
    if os.name == "nt":  # Windows at it again
        os.system("ansi")

    spotify = spotify_setup()
    ytmusic = youtube_music_setup()

    sync_youtube_to_spotify(ytmusic, spotify)
