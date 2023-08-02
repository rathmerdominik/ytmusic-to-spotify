import os
import sys
import spotipy  # type: ignore
import argparse
import ytmusicapi  # type: ignore


from typing import List, Union, Optional

from termcolor import cprint

from dataclasses import dataclass

from librespot.core import Session  # type: ignore


@dataclass
class OptionArgs:
    cleanup_spotify: bool
    dirty_search: bool
    user_choice: bool


options: Optional[OptionArgs] = None


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

    assert options is not None
    if options.cleanup_spotify:
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

    assert options is not None
    if options.dirty_search:
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

    chosen_track: Union[List[dict], bool] = []

    while True:
        choice = input(
            f"[1 - {len(spotify_tracks)}] => Track number \
                        \n[s] => Search for a track \
                        \n[x] => Exit the program \
                        \n[c] => Skip this song \
                        \nSelect an option > $  "
        )

        for i in range(5):
            print(LINE_UP, end=LINE_CLEAR)
        try:
            chosen_track = [spotify_tracks[int(choice) - 1]]
            break
        except Exception:
            if choice == "s":
                search_q = input("Please enter search query > $ ")

                tracks_to_handle = spotify.search(search_q)["tracks"]["items"]
                print(LINE_UP, end=LINE_CLEAR)
                chosen_track = handle_duplicates(
                    tracks_to_handle, track_name, track_artist, track_album, spotify
                )
                print(LINE_UP, end=LINE_CLEAR)
                break
            elif choice == "x":
                print("Closing the program!")
                raise KeyboardInterrupt
            elif choice == "c":
                return False
            else:
                print("Wrong input! Please select one of the following:")
                continue

    return chosen_track


def handle_duplicates(
    spotify_tracks: List[dict],
    track_name: str,
    track_artist: str,
    track_album: str,
    spotify: spotipy.Spotify,
) -> Union[List[dict], bool]:
    first_match_string = ""

    assert options is not None
    if not options.user_choice:
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

    if options.user_choice:
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

    parser = argparse.ArgumentParser(
        prog="YTMusic To Spotify",
        description="Convert YTMusic likes to Spotify saved tracks",
    )
    parser.add_argument(
        "-c",
        "--cleanup_spotify",
        action="store_true",
        help="Clear your entire spotify saved tracks first before starting to import. This can help to have a clean synchronization",
    )
    parser.add_argument(
        "-d",
        "--dirty_search",
        action="store_true",
        help="Enable dirty searching for a track when no matches have been found.",
    )
    parser.add_argument(
        "-u",
        "--user_choice",
        action="store_true",
        help="Enable user choice on found duplicates. Not enabling this will always take the first entry found, when multiple matches occur!",
    )

    options = OptionArgs(**vars(parser.parse_args()))

    try:
        spotify = spotify_setup()
        ytmusic = youtube_music_setup()

        sync_youtube_to_spotify(ytmusic, spotify)
    except KeyboardInterrupt:
        print("\n--- Program exit requested ---")
