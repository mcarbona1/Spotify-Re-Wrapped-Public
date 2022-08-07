#!/usr/bin/env python3
# script.py
# Making first text website for tutorial learning purposes

import os
from flask import session, request, redirect, Flask, render_template
from flask_session import Session
import spotipy
import googleapiclient.discovery as gapi
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
import google.oauth2.credentials
import google_auth_oauthlib.flow
import uuid
from pprint import pprint

try:
    from .apiRequests import spotifyRequests, youtubeRequests
except ImportError:
    from apiRequests import spotifyRequests, youtubeRequests

sps = dict()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(64)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = './.flask_session/'
    Session(app)

    caches_folder = './.spotify_caches/'
    if not os.path.exists(caches_folder):
        os.makedirs(caches_folder)

    def session_cache_path():
        return caches_folder + session.get('uuid')

    @app.route('/home/spotify/make-playlist', methods=["GET", "POST"])
    def makePlaylist():
        if not session.get("uuid") or not sps.get(session.get("uuid")):
            return redirect("/home/spotify/login")
        else:
            sp = sps.get(session.get("uuid"))
        if request.form.get("playlistId"):
            session['playlist'] = request.form.get("playlistId")
            session['owner'] = request.form.get("playlistOwner")
        response = spotifyRequests.get_playlist_tracks(sp, session['playlist'], session["owner"])
        tracks = []
        for track in response:
            newTrack = {}
            newTrack["name"] = track["track"]["name"]
            newTrack["artist"] = track["track"]["artists"][0]["name"]
            tracks.append(newTrack)

        authURL, flow = youtubeRequests.get_authenticated_service()

        if request.args.get("code"):
            flow.fetch_token(code=request.args["code"])
            credentials = flow.credentials
            session['credentials'] = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }

        if not session.get("credentials", None):
            return redirect(authURL)
        try:
            creds = google.oauth2.credentials.Credentials(**session['credentials'])
            auth = youtubeRequests.get_auth(creds)
            youtubeRequests.add_playlist(tracks, auth)
            del session['credentials']
            return render_template("success.html")
        except HttpError as e:
            print(f"{e}")
            return redirect("/home/spotify")



    @app.route('/')
    def home2():
        return redirect("/home/spotify/logout");

    @app.route('/home/spotify/playlist', methods=["GET", "POST"])
    def playlistMaker():
        params = dict()
        if not session.get("uuid") or not sps.get(session.get("uuid")):
            return redirect("/home/spotify/login")
        else:
            sp = sps.get(session.get("uuid"))

        params["title"] = "Playlist Maker"
        params["search"] = False
        headers = ["Name", "Image", "Owner", "Description"]
        if request.method == "POST" and request.form.get("query", None):
            query = request.form.get("query", None)
            response = spotifyRequests.get_playlist(sp, query)
            searches = []
            for search in response:
                searches.append({key: search[key.lower()] for key in headers if key != "Image"})
                searches[-1]["Image"] = search["images"][0]["url"]
                searches[-1]["playlist"] = {"id": search["id"],
                                            "owner": search["owner"]["id"]}

            params["fields"] = searches
            params["search"] = True
            params["headers"] = headers

        return render_template("playlist.html", **params)

    @app.route('/home/spotify/login')
    def login():
        if not session.get('uuid'):
            # Step 1. Visitor is unknown, give random ID
            session['uuid'] = str(uuid.uuid4())
        scope = [
        "user-read-email",
        "playlist-read-private",
        "playlist-read-collaborative",
        "user-read-email",
        "streaming",
        "user-read-private",
        "user-library-read",
        "user-top-read",
        #"user-library-modify"
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
        "user-read-recently-played",
        "user-read-playback-state",
        "user-follow-read",
        ];
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope,
                                                cache_handler=cache_handler,
                                                show_dialog=True)

        if request.args.get("code"):
            # Step 3. Being redirected from Spotify auth page
            auth_manager.get_access_token(request.args.get("code"))
            sp = spotipy.Spotify(auth_manager=auth_manager)
            sps[session.get('uuid')] = sp
            return redirect('/home/spotify')

        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            # Step 2. Display sign in link when no token
            auth_url = auth_manager.get_authorize_url()
            #return f'<h2><a href="{auth_url}">Sign in</a></h2>'
            return redirect(auth_url)

        # Step 4. Signed in, display data
        return redirect("/home/spotify/logout")


    @app.route('/home/spotify/logout')
    def logout():
        try:
            os.remove(session_cache_path())
            if session.get("uuid") in sps:
                del sps[session.get("uuid")]
            session.clear()
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))
        except TypeError:
            pass
        return redirect('/home/spotify')

    @app.route('/home/spotify')
    def spotify_home():
        if not session.get("uuid") or not sps.get(session.get("uuid")):
            login = True
        else:
            login = False
        return render_template("index.html", login=login);

    @app.route('/home/spotify/top-artists')
    def top_artists():
        params = {}
        if not session.get("uuid") or not sps.get(session.get("uuid")):
            return redirect("/home/spotify/login")
        else:
            sp = sps.get(session.get("uuid"))
        response = spotifyRequests.get_user_artists(sp)
        artists = []
        headers = ["Rank", "image", "Name", "Genres"]

        for num, artist in enumerate(response, start = 1):
            artist["genres"] = ', '.join(artist["genres"])
            artist['rank'] = num
            artists.append({key: artist[key.lower()] for key in headers if key != "image"})
            artists[-1]["image"] = artist["images"][2]["url"]

        params["fields"] = artists
        params["headers"] = headers
        params["title"] = "Your top Artists!"
        params["imageHead"] = "Artist's Picture"


        return render_template("displayResults.html", **params)


    @app.route('/home/spotify/top-songs')
    def top_songs():
        params = {}
        if not session.get("uuid") or not sps.get(session.get("uuid")):
            return redirect("/home/spotify/login")
        else:
            sp = sps.get(session.get("uuid"))
        response = spotifyRequests.get_user_tracks(sp)
        tracks = []
        headers = ["Rank", "image" ,"Name", "Artists"]

        for num, track in enumerate(response, start = 1):
            track["artists"] = ', '.join(map(lambda a: a["name"], track["artists"]))
            track['rank'] = num
            tracks.append({key: track[key.lower()] for key in headers if key != "image"})
            tracks[-1]["image"] = track["album"]["images"][1]["url"]

        params["fields"] = tracks
        params["headers"] = headers
        params["title"] = "Your top Tracks!"
        params["imageHead"] = "Album Artwork"


        return render_template("displayResults.html", **params)


    @app.route('/home/spotify/song-recommendations')
    def song_recs():
        params = {}
        if not session.get("uuid") or not sps.get(session.get("uuid")):
            return redirect("/home/spotify/login")
        else:
            sp = sps.get(session.get("uuid"))
        response = spotifyRequests.get_user_recommendations(sp)
        recs = []
        headers = ["Rank", "image", "Name", "Artists"]

        for num, rec in enumerate(response, start = 1):
            rec["artists"] = ', '.join(map(lambda a: a["name"], rec["artists"]))
            rec['rank'] = num
            recs.append({key: rec[key.lower()] for key in headers if key != "image"})
            recs[-1]["image"] = rec["album"]["images"][1]["url"]


        params["fields"] = recs
        params["headers"] = headers
        params["title"] = "Your top Recommendations!"
        params["imageHead"] = "Album Artwork"


        return render_template("displayResults.html", **params)

    return app


if __name__ =='__main__':
    # Launch the Flask dev server
    app = create_app()
    app.run(host="0.0.0.0", port = "9123")
