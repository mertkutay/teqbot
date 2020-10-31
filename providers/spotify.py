import re

import requests

from teqbot import settings, cache


class SpotifyClient:
    AUTH_URL = "https://accounts.spotify.com/api/token"
    API_URL = "https://api.spotify.com/v1"

    def __init__(self):
        self.access_token = cache.get("SPOTIFY_ACCESS_TOKEN")
        if not self.access_token:
            self._refresh_access_token()

    def _refresh_access_token(self):
        response = requests.post(
            self.AUTH_URL,
            auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
            data={
                "grant_type": "refresh_token",
                "refresh_token": settings.SPOTIFY_REFRESH_TOKEN,
            },
        )
        response.raise_for_status()
        self.access_token = response.json()["access_token"]
        cache.set("SPOTIFY_ACCESS_TOKEN", self.access_token)

    def _get(self, path):
        response = requests.get(
            self.API_URL + path,
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        if response.status_code == 401:
            self._refresh_access_token()
            return self._get(path)

        return response.json()

    def playlist_songs(self, playlist_url):
        playlist_id = re.search(r"playlist/(\w+)\??", playlist_url).group(1)
        data = self._get(f"/playlists/{playlist_id}")
        tracks = [item["track"] for item in data["tracks"]["items"]]
        results = []
        for track in tracks:
            artist = track["artists"][0]["name"]
            song = track["name"]
            title = f"{artist} - {song}"
            if len(track["artists"]) > 1:
                title += " ft. " + ", ".join(
                    [artist["name"] for artist in track["artists"][1:]]
                )

            results.append(title)

        return results


spotify_client = SpotifyClient()
