#!/usr/bin/env python3
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyPKCE
from pprint import pprint
from dotenv import load_dotenv

'''
results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])

currUser = sp.me()
print(currUser)
'''
def get_user_tracks(sp, limit=25, timeframe="medium_term"):
    '''Usage: get_user_tracks(sp, limit, timeframe).
        sp: spotipy.Spotify object
        Return: list of track objects (dict format, check spotify API reference for fields)
        limit: between 1-50 (will accept  greater but only returns up to 50)
        timeframe: medium_term, short_term, or long_term
    '''
    if timeframe != "medium_term" and timeframe != "short_term" and timeframe != "long_term":
        print(f"{timeframe} is not a recognized timeframe!")
        return None

    return sp.current_user_top_tracks(limit=limit, time_range=timeframe)['items']


def get_user_artists(sp, limit=25, timeframe="medium_term"):
    '''Usage: get_user_artists(sp, limit, timeframe).
        Return: list of artist objects (dict format, check spotify API reference for fields)
        sp: spotipy.Spotify object
        limit: between 1-50 (will accept  greater but only returns up to 50)
        timeframe: medium_term, short_term, or long_term
    '''
    if timeframe != "medium_term" and timeframe != "short_term" and timeframe != "long_term":
        print(f"{timeframe} is not a recognized timeframe!")
        return None

    return sp.current_user_top_artists(limit=limit, time_range=timeframe)["items"]

def get_user_recommendations(sp):
    '''Usage: get_user_artists(sp).
        return: list of dictionaries, each dictionary is a track
        sp: spotipy.Spotify object
    '''
    seedTracks = []

    for track in get_user_tracks(sp, 3):
        seedTracks.append(track['uri'])

    seedArtists = []

    for artist in get_user_artists(sp, 2):
        seedArtists.append(artist['uri'])


    return sp.recommendations(seed_tracks=seedTracks,seed_artists=seedArtists)['tracks']

def get_playlist(sp, search_term, num_playlists=20):
    playlists = sp.search(search_term, limit=num_playlists, type="playlist")['playlists']

    return playlists['items']

def get_playlist_tracks(sp, playId, userID):
    tracks = sp.user_playlist_tracks(userID, playId)
    return tracks["items"]


'''
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

playlists = sp.user_playlists('2235zbnfkbxj54k34t2chcyha')
while playlists:
    for i, playlist in enumerate(playlists['items']):
        print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None
'''

def main():
    sp = get_user_auth()

    for num, artist in enumerate(get_user_artists(sp), start=1):
        print(f'{num:>2}. {artist["name"]:<20}\t{", ".join(artist["genres"])}')


    for num, track in enumerate(get_user_tracks(sp), start=1):
        print(f'{num:>2}. {track["name"]:<20}\t{track["album"]["artists"][0]["name"]}')


    for num, rec in enumerate(get_user_recommendations(sp), start=1):
        print(f"{num:>2}. {rec['name'] if len(rec['name']) < 24 else rec['name'][:21]+'...':>20}\t{rec['artists'][0]['name']}")

    num_playlists = 20
    playlists = get_playlist(sp, "summer vibes", num_playlists)
    if len(playlists) > 0:
        for num, playlist in enumerate(playlists, start=1):
            print(f"{num:>2}. {playlist['name']} by {playlist['owner']['display_name']}")

    selection = input("Select Desired Playlist: ")

    try:
        selection = int(selection)
        if selection <= num_playlists and selection >= 1:
            playlist = playlists[selection - 1]
        else:
            print("invalid selection")
            playlist = None
    except ValueError:
        print("invalid selection")
        playlist = None

    pprint(playlist)




if __name__ == "__main__":
    main()
