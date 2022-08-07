#!/usr/bin/env python3
import os
import googleapiclient.discovery as gapi
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import google.oauth2.credentials
import google_auth_oauthlib.flow
from pprint import pprint

def yt_login():
	'''
		Creates a google API client to use for list requests
		Requires the API key for the project
		os.environ is a line that should not be used in large scale production,
			but it is fine for this purpose
	'''
	os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
	api_service_name = "youtube"
	api_version = "v3"
	DEVELOPER_KEY = "AIzaSyBlkRtPj-qOYl4kOpxsIaugLAhzNgpYPS8"
	youtube = gapi.build(
   	api_service_name, 
		api_version, 
		developerKey = DEVELOPER_KEY
	)
	return youtube

def make_yt_request(yt, query):
	'''
		Usage: make_request(youtube, query)
		youtube: google API client for youtubeV3 API
		query: string to use as YouTube's search query
		return: response JSON
	'''
	request = yt.search().list(
   	part="snippet",
		q=query
	)
	response = request.execute()
	return response

def get_authenticated_service():
	client_secret_file = "client_secret.json"
	api_service_name = "youtube"
	api_version = "v3"
	scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		client_secret_file,
		scopes=scopes
	)
	flow.redirect_uri = "http://127.0.0.1:5000/home/spotify/make-playlist"

	authorization_url, state = flow.authorization_url(
		access_type="offline",
		include_granted_scopes='true'
	)
	return authorization_url, flow
def get_auth(creds):
	api_service_name = "youtube"
	api_version = "v3"
	return build(api_service_name, api_version, credentials=creds)

def make_playlist(auth):
	playlist = auth.playlists().insert(
		part="snippet",
		body={
			"snippet": {
				"title": "Spotify Playlist"
			}
		}
	)
	pResponse = playlist.execute()
	return pResponse

def add_video(auth, vid_id, playlist_id):
	add_response = auth.playlistItems().insert(
		part="snippet",
		body={
			'snippet': {
			'playlistId': playlist_id, 
				'resourceId': {
					'kind': 'youtube#video',
					'videoId': vid_id
				}
			}
		}
	).execute()
	return add_response

def add_playlist(trackList, auth):
	youtube = yt_login()
	pResp = make_playlist(auth)
	for track in trackList:
		response = make_yt_request(youtube, f"{track['name']} {track['artist']}")
		if response.get("items")[0].get("id").get("videoId", None):
			addResp = add_video(auth, response["items"][0]["id"]["videoId"], pResp["id"])

def main():
	youtube = yt_login()
	response = make_yt_request(youtube, "Waves Kanye west")
	pprint(response["items"][0])
	url = "youtube.com/watch?v=" + response["items"][0]["id"]["videoId"]
	#print(url)
	auth = get_authenticated_service()
	pResp = make_playlist(auth)
	addResp = add_video(auth, response["items"][0]["id"]["videoId"], pResp["id"])
	#print(addResp)
	
if __name__ == "__main__":
	main()
