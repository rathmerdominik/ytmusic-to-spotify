import src.ytmusic_to_spotify.ytmusic_to_spotify

from spotipy import Spotify  # type: ignore

from pytest_mock import MockerFixture

from src.tests.fixtures import spotify_tracks

from src.ytmusic_to_spotify.ytmusic_to_spotify import (
    spotify_setup,
    OptionArgs,
    cleanup_spotify,
)


def test_cleanup_spotify(mocker: MockerFixture) -> None:
    current_user_saved_tracks = mocker.patch(
        "spotipy.client.Spotify.current_user_saved_tracks",
    )

    current_user_saved_tracks_delete = mocker.patch(
        "spotipy.client.Spotify.current_user_saved_tracks_delete"
    )
    current_user_saved_tracks.side_effect = [
        spotify_tracks.get_spotify_tracks(),
        {"items": []},
    ]

    cleanup_spotify(Spotify)

    assert current_user_saved_tracks.call_count == 2
    assert current_user_saved_tracks_delete.call_count == 4


def test_spotify_setup_with_credentials_file(
    mocker: MockerFixture, monkeypatch
) -> None:
    os_path_isfile = mocker.patch("os.path.isfile", return_value=True)
    session_create = mocker.patch("librespot.core.Session.Builder")

    options = OptionArgs(False, False, False)

    monkeypatch.setattr(src.ytmusic_to_spotify.ytmusic_to_spotify, "options", options)

    return_value = spotify_setup()

    assert isinstance(return_value, Spotify)
    os_path_isfile.assert_called_with("../../credentials.json")
    session_create.assert_called_once()


def test_spotify_setup_without_credentials_file(
    mocker: MockerFixture, monkeypatch
) -> None:
    os_path_isfile = mocker.patch("os.path.isfile", return_value=False)
    session_create = mocker.patch("librespot.core.Session.Builder")

    options = OptionArgs(False, False, False)

    monkeypatch.setattr(src.ytmusic_to_spotify.ytmusic_to_spotify, "options", options)

    monkeypatch.setattr("builtins.input", lambda _: "test")

    return_value = spotify_setup()

    assert isinstance(return_value, Spotify)
    os_path_isfile.assert_called_with("../../credentials.json")
    session_create.assert_called_once()


def test_handle_duplicates_with_track_number():
    pass


def test_handle_duplicates_with_search():
    pass


def test_handle_duplicates_with_exit():
    pass


def test_handle_duplicates_with_skip():
    pass


def test_sync_youtube_to_spotify(mocker: MockerFixture) -> None:
    pass
